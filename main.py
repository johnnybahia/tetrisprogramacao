"""
Backend FastAPI - Sistema de Planejamento de Produção
Frontend: HTML/CSS/JS puro
Backend: Python com FastAPI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
from pathlib import Path

# Importa módulos existentes
from modules.database_manager import GoogleSheetsManager
from modules.calculator import ProductionCalculator, formatar_data_br
from modules.optimizer import ProductionOptimizer
from modules.workday_calendar import get_calendar
from modules.dynamic_planner import get_planner
from modules.machine_optimizer import get_machine_optimizer

# ========================================
# INICIALIZAÇÃO
# ========================================
app = FastAPI(
    title="Sistema de Planejamento de Produção",
    description="API REST para planejamento inteligente de produção",
    version="3.0.0"
)

# CORS - Permite frontend acessar API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve arquivos estáticos (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Inicializa gerenciador de dados
db_manager = GoogleSheetsManager()

# ========================================
# MODELOS PYDANTIC (Validação)
# ========================================

class ProdutoCreate(BaseModel):
    maquina: str
    referenciaMaquina: str
    referencia: str
    tempoProducao: float
    tempoMontagem: float
    voltasEspula: int = 0
    producaoPorMinuto: float = 0
    cor: str = "#667eea"
    largura: float = 0
    montagem2x2: str = "Não"
    tempoMontagem2x2: float = 0

class PedidoCreate(BaseModel):
    cliente: str
    ordem_compra: str
    data_entrega: str
    maquina: str
    bocas: int
    produto: str
    quantidade: int

class OtimizacaoRequest(BaseModel):
    pedidos: List[Dict]

class HolidaysRequest(BaseModel):
    dates: List[str]

class WeekendConfigRequest(BaseModel):
    work_saturday: bool
    work_sunday: bool

class WeekendDatesRequest(BaseModel):
    saturdays: List[str]
    sundays: List[str]

class DynamicPlanRequest(BaseModel):
    orders: List[Dict]
    start_date: Optional[str] = None

class ReorderRequest(BaseModel):
    machine: str
    order_ids: List[str]
    all_orders: List[Dict]
    start_date: Optional[str] = None

class MoveOrderRequest(BaseModel):
    order_id: str
    from_position: int
    to_position: int
    machine: str
    all_orders: List[Dict]
    start_date: Optional[str] = None

class SavePlanRequest(BaseModel):
    plan_name: str
    plan: Dict

class OptimizeMachinesRequest(BaseModel):
    orders: List[Dict]
    start_date: Optional[str] = None

class ApplySuggestionsRequest(BaseModel):
    orders: List[Dict]
    suggestions: List[Dict]

# ========================================
# ROTA PRINCIPAL - Serve o HTML
# ========================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a página principal HTML"""
    html_file = Path("frontend/index.html")
    if html_file.exists():
        return FileResponse(html_file)
    return HTMLResponse("<h1>Frontend não encontrado</h1>")

# ========================================
# ROTAS DE CONEXÃO
# ========================================

@app.get("/api/status")
async def get_status():
    """Verifica status da conexão com Google Sheets"""
    try:
        maquinas = db_manager.get_maquinas()
        return {
            "status": "connected",
            "maquinas_count": len(maquinas) if maquinas else 0,
            "message": "Conectado ao Google Sheets"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ========================================
# ROTAS DE MÁQUINAS
# ========================================

@app.get("/api/maquinas")
async def get_maquinas():
    """Retorna lista de máquinas disponíveis"""
    try:
        maquinas = db_manager.get_maquinas()
        return {"maquinas": maquinas if maquinas else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ROTAS DE PRODUTOS
# ========================================

@app.get("/api/produtos/{maquina}")
async def get_produtos_por_maquina(maquina: str):
    """Retorna produtos de uma máquina específica"""
    try:
        df_produtos = db_manager.get_produtos_por_maquina(maquina)

        if df_produtos.empty:
            return {"produtos": []}

        produtos = df_produtos.to_dict('records')
        return {"produtos": produtos}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/produtos")
async def criar_produto(produto: ProdutoCreate):
    """Cria novo produto no Google Sheets"""
    try:
        produto_data = produto.dict()
        sucesso = db_manager.add_produto(produto_data)

        if sucesso:
            return {
                "success": True,
                "message": f"Produto '{produto.referencia}' cadastrado com sucesso!"
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao cadastrar produto")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ROTAS DE CLIENTES E ORDENS
# ========================================

@app.get("/api/clientes")
async def get_clientes():
    """Retorna lista de clientes"""
    try:
        clientes = db_manager.get_clientes()
        return {"clientes": clientes if clientes else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ordens")
async def get_ordens():
    """Retorna lista de ordens de compra"""
    try:
        ordens = db_manager.get_ordens()
        return {"ordens": ordens if ordens else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datas")
async def get_datas():
    """Retorna lista de datas de entrega"""
    try:
        datas = db_manager.get_datas_entrega()
        return {"datas": datas if datas else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pedidos-cadastrados")
async def get_pedidos_cadastrados():
    """Retorna lista completa de pedidos da aba DADOS_GERAIS"""
    try:
        pedidos = db_manager.get_pedidos_cadastrados()
        return {"pedidos": pedidos if pedidos else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ROTAS DE PEDIDOS
# ========================================

@app.post("/api/pedidos")
async def criar_pedido(pedido: PedidoCreate):
    """Cria novo pedido"""
    try:
        pedido_data = pedido.dict()
        sucesso = db_manager.add_pedido(pedido_data)

        if sucesso:
            return {
                "success": True,
                "message": "Pedido adicionado com sucesso!"
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao adicionar pedido")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ROTAS DE CÁLCULOS
# ========================================

@app.post("/api/calcular/tempo-produto")
async def calcular_tempo_produto(produto: Dict):
    """Calcula tempo total de produção de um produto"""
    try:
        calc = ProductionCalculator()
        tempo_total = calc.calcular_tempo_total_produto(produto)

        return {
            "tempo_total": tempo_total,
            "tempo_total_horas": tempo_total / 60
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calcular/dias-entrega/{data_entrega}")
async def calcular_dias_entrega(data_entrega: str):
    """Calcula dias até a entrega"""
    try:
        calc = ProductionCalculator()
        dias = calc.calcular_dias_ate_entrega(data_entrega)

        return {
            "dias": dias,
            "urgencia": "CRITICO" if dias <= 7 else "ATENCAO" if dias <= 15 else "OK"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ROTAS DE PLANEJAMENTO
# ========================================

@app.post("/api/planejamento/gerar")
async def gerar_planejamento(pedidos_data: Dict):
    """Gera planejamento simples"""
    try:
        pedidos = pedidos_data.get('pedidos', [])
        sequencia = []

        for pedido in pedidos:
            # Busca informações do produto
            df_prod = db_manager.get_produtos_por_maquina(pedido['maquina'])
            produto_info = df_prod[df_prod['REFERENCIA'] == pedido['produto']]

            if not produto_info.empty:
                produto_dict = produto_info.iloc[0].to_dict()
                calc = ProductionCalculator()

                tempo_total_unit = calc.calcular_tempo_total_produto(produto_dict)
                dias_entrega = calc.calcular_dias_ate_entrega(pedido['data_entrega'])

                sequencia.append({
                    'cliente': pedido['cliente'],
                    'ordem_compra': pedido['ordem_compra'],
                    'produto': pedido['produto'],
                    'maquina': pedido['maquina'],
                    'quantidade': pedido['quantidade'],
                    'bocas': pedido['bocas'],
                    'tempo_unitario': tempo_total_unit,
                    'tempo_total': tempo_total_unit * pedido['quantidade'],
                    'data_entrega': pedido['data_entrega'],
                    'dias_para_entrega': dias_entrega,
                    'prioridade': 1000 - dias_entrega,
                    'cor': produto_dict.get('COR', '#CCCCCC')
                })

        # Ordena por prioridade
        sequencia = sorted(sequencia, key=lambda x: x['prioridade'], reverse=True)

        # Adiciona ordem
        for i, item in enumerate(sequencia, 1):
            item['ordem'] = i

        # Calcula estatísticas
        calc = ProductionCalculator()
        stats = calc.gerar_relatorio_tempo(sequencia)

        return {
            "success": True,
            "sequencia": sequencia,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ROTAS DE OTIMIZAÇÃO (PRINCIPAL!)
# ========================================

@app.post("/api/otimizacao/analisar")
async def otimizar_distribuicao(request: OtimizacaoRequest):
    """
    FUNCIONALIDADE PRINCIPAL: Otimização Inteligente
    Analisa urgência, distribui bocas, gera sugestões
    """
    try:
        pedidos = request.pedidos

        # Prepara dados dos produtos
        produtos_completos = pd.DataFrame()

        for maq in set(p['maquina'] for p in pedidos):
            df_maq = db_manager.get_produtos_por_maquina(maq)
            produtos_completos = pd.concat([produtos_completos, df_maq], ignore_index=True)

        # Executa otimização
        optimizer = ProductionOptimizer()
        resultado = optimizer.otimizar_distribuicao(pedidos, produtos_completos)

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/otimizacao/relatorio")
async def gerar_relatorio_otimizacao(resultado_data: Dict):
    """Gera relatório textual da otimização"""
    try:
        optimizer = ProductionOptimizer()
        relatorio = optimizer.gerar_relatorio_otimizacao(resultado_data)

        return {
            "success": True,
            "relatorio": relatorio
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ROTAS DE CALENDÁRIO DE TRABALHO
# ========================================

@app.get("/api/calendario/summary")
async def get_calendar_summary():
    """Retorna resumo do calendário de trabalho"""
    try:
        calendar = get_calendar()
        return calendar.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calendario/feriados")
async def add_holidays(request: HolidaysRequest):
    """Adiciona feriados ao calendário"""
    try:
        calendar = get_calendar()
        result = calendar.add_holidays(request.dates)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/calendario/feriados")
async def remove_holidays(request: HolidaysRequest):
    """Remove feriados do calendário"""
    try:
        calendar = get_calendar()
        result = calendar.remove_holidays(request.dates)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendario/feriados")
async def get_holidays():
    """Lista todos os feriados cadastrados"""
    try:
        calendar = get_calendar()
        holidays = calendar.get_holidays()
        return {"holidays": holidays}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calendario/fins-de-semana/config")
async def set_weekend_config(request: WeekendConfigRequest):
    """Define se trabalha aos fins de semana por padrão"""
    try:
        calendar = get_calendar()
        calendar.set_weekend_working(request.work_saturday, request.work_sunday)
        return {
            "success": True,
            "message": "Configuração de fins de semana atualizada"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendario/fins-de-semana/config")
async def get_weekend_config():
    """Retorna configuração de fins de semana"""
    try:
        calendar = get_calendar()
        return calendar.get_weekend_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendario/fins-de-semana/{year}")
async def get_weekends_in_year(year: int):
    """Lista todos os sábados e domingos de um ano"""
    try:
        calendar = get_calendar()
        weekends = calendar.get_weekends_in_year(year)
        return weekends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calendario/fins-de-semana/datas")
async def set_working_weekend_dates(request: WeekendDatesRequest):
    """Define datas específicas de fins de semana como dias de trabalho"""
    try:
        calendar = get_calendar()
        calendar.set_working_weekend_dates(request.saturdays, request.sundays)
        return {
            "success": True,
            "message": "Datas de fins de semana atualizadas"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calendario/limpar")
async def clear_calendar():
    """Limpa todas as configurações do calendário"""
    try:
        calendar = get_calendar()
        calendar.clear_all()
        return {
            "success": True,
            "message": "Calendário limpo com sucesso"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ROTAS DE PLANEJAMENTO DINÂMICO
# ========================================

@app.post("/api/planejamento/dinamico/criar")
async def create_dynamic_plan(request: DynamicPlanRequest):
    """Cria um plano de produção dinâmico"""
    try:
        planner = get_planner()

        # Converte data se fornecida
        start_date = None
        if request.start_date:
            try:
                start_date = datetime.strptime(request.start_date, "%d/%m/%Y")
            except:
                start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        plan = planner.create_plan(request.orders, start_date)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/planejamento/dinamico/reordenar")
async def reorder_orders(request: ReorderRequest):
    """Reordena pedidos de uma máquina e recalcula"""
    try:
        planner = get_planner()

        # Converte data se fornecida
        start_date = None
        if request.start_date:
            try:
                start_date = datetime.strptime(request.start_date, "%d/%m/%Y")
            except:
                start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        plan = planner.reorder_and_recalculate(
            request.machine,
            request.order_ids,
            request.all_orders,
            start_date
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/planejamento/dinamico/mover")
async def move_order(request: MoveOrderRequest):
    """Move um pedido de uma posição para outra"""
    try:
        planner = get_planner()

        # Converte data se fornecida
        start_date = None
        if request.start_date:
            try:
                start_date = datetime.strptime(request.start_date, "%d/%m/%Y")
            except:
                start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        plan = planner.move_order(
            request.order_id,
            request.from_position,
            request.to_position,
            request.machine,
            request.all_orders,
            start_date
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/planejamento/dinamico/timeline/{machine}")
async def get_machine_timeline(machine: str, plan: Dict):
    """Obtém timeline de uma máquina"""
    try:
        planner = get_planner()
        timeline = planner.get_machine_timeline(machine, plan)
        return timeline
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/planejamento/dinamico/salvar")
async def save_plan(request: SavePlanRequest):
    """Salva um plano"""
    try:
        planner = get_planner()
        success = planner.save_plan(request.plan_name, request.plan)
        return {
            "success": success,
            "message": f"Plano '{request.plan_name}' salvo com sucesso" if success else "Erro ao salvar plano"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/planejamento/dinamico/carregar/{plan_name}")
async def load_plan(plan_name: str):
    """Carrega um plano salvo"""
    try:
        planner = get_planner()
        plan = planner.load_plan(plan_name)

        if plan is None:
            raise HTTPException(status_code=404, detail="Plano não encontrado")

        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/planejamento/dinamico/listar")
async def list_saved_plans():
    """Lista todos os planos salvos"""
    try:
        planner = get_planner()
        plans = planner.list_saved_plans()
        return {"plans": plans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/maquinas/{maquina}/disponibilidade")
async def get_machine_availability(maquina: str):
    """Retorna a disponibilidade (horas/dia) de uma máquina"""
    try:
        availability = db_manager.get_machine_availability(maquina)
        return {
            "maquina": maquina,
            "availability_hours": availability
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/maquinas/disponibilidade/todas")
async def get_all_machines_availability():
    """Retorna a disponibilidade de todas as máquinas"""
    try:
        availability_dict = db_manager.get_all_machines_availability()
        return {"machines_availability": availability_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ROTAS DE OTIMIZAÇÃO DE MÁQUINAS
# ========================================

@app.post("/api/otimizacao/sugerir-maquinas")
async def suggest_machine_optimization(request: OptimizeMachinesRequest):
    """
    Analisa pedidos e sugere melhor distribuição de máquinas
    para minimizar atrasos e otimizar produção
    """
    try:
        optimizer = get_machine_optimizer()

        # Converte data se fornecida
        start_date = None
        if request.start_date:
            try:
                start_date = datetime.strptime(request.start_date, "%d/%m/%Y")
            except:
                start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        result = optimizer.analyze_and_suggest(request.orders, start_date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/otimizacao/aplicar-sugestoes")
async def apply_machine_suggestions(request: ApplySuggestionsRequest):
    """Aplica sugestões de otimização aos pedidos"""
    try:
        optimizer = get_machine_optimizer()
        optimized_orders = optimizer.apply_suggestions(
            request.orders,
            request.suggestions
        )

        return {
            "success": True,
            "optimized_orders": optimized_orders,
            "total_changed": sum(
                1 for i, order in enumerate(optimized_orders)
                if order.get('maquina') != request.orders[i].get('maquina')
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# ROTAS DE UTILITÁRIOS
# ========================================

@app.get("/api/limpar-cache")
async def limpar_cache():
    """Limpa cache de dados"""
    try:
        db_manager.limpar_cache()
        return {
            "success": True,
            "message": "Cache limpo com sucesso"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0"
    }

# ========================================
# EXECUÇÃO
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
