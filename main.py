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
