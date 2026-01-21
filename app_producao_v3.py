"""
Sistema de Planejamento de Produção - Versão 3.0 PROFESSIONAL
Integrado com Google Sheets + Otimização Inteligente + Design Profissional
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Adiciona o diretório de módulos ao path
sys.path.append(str(Path(__file__).parent))

from modules.database_manager import GoogleSheetsManager
from modules.calculator import ProductionCalculator, formatar_data_br
from modules.optimizer import ProductionOptimizer
from modules.ui_components import (
    render_machine_visual,
    render_production_table,
    render_stats_cards,
    render_sequencia_detalhada
)

# ========================================
# CONFIGURAÇÃO DA PÁGINA
# ========================================
st.set_page_config(
    page_title="Sistema de Planejamento de Produção Pro",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Sistema Profissional de Planejamento de Produção v3.0"
    }
)

# ========================================
# CSS PROFISSIONAL
# ========================================
def load_css():
    """Carrega CSS personalizado"""
    css_file = Path(__file__).parent / 'assets' / 'style.css'
    if css_file.exists():
        with open(css_file, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # CSS adicional inline
    st.markdown("""
    <style>
        /* Gradiente de fundo */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-attachment: fixed;
        }

        /* Botão de otimização especial */
        .optimize-button {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 10px 30px rgba(240, 147, 251, 0.4);
            animation: pulse-optimize 2s infinite;
        }

        @keyframes pulse-optimize {
            0%, 100% {
                box-shadow: 0 10px 30px rgba(240, 147, 251, 0.4);
            }
            50% {
                box-shadow: 0 15px 40px rgba(240, 147, 251, 0.6);
            }
        }

        /* Cards de resultado otimização */
        .optimization-result {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
            border-left: 5px solid #f5576c;
        }

        /* Badge de urgência */
        .urgency-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-weight: 700;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .urgency-critico {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
            color: white;
            animation: blink-red 1s infinite;
        }

        .urgency-atencao {
            background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
            color: #000;
        }

        .urgency-ok {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }

        @keyframes blink-red {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        /* Status connection */
        .status-connected {
            background: #10b981;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
        }

        .status-disconnected {
            background: #ef4444;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
        }

        /* Título com gradiente animado */
        .animated-title {
            background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #667eea);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradient-shift 3s ease infinite;
            font-size: 3.5rem;
            font-weight: 900;
            text-align: center;
            margin: 2rem 0;
            letter-spacing: -2px;
        }

        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ========================================
# INICIALIZAÇÃO
# ========================================
@st.cache_resource
def init_manager():
    """Inicializa o gerenciador de dados"""
    return GoogleSheetsManager()

# Inicializa session state
if 'pedidos_temp' not in st.session_state:
    st.session_state.pedidos_temp = []

if 'sequencia_gerada' not in st.session_state:
    st.session_state.sequencia_gerada = []

if 'otimizacao_resultado' not in st.session_state:
    st.session_state.otimizacao_resultado = None

# ========================================
# HEADER PRINCIPAL
# ========================================
st.markdown(
    '<h1 class="animated-title">🏭 SISTEMA DE PRODUÇÃO INTELIGENTE</h1>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="subtitle">Planejamento Otimizado • Análise em Tempo Real • Decisões Inteligentes</p>',
    unsafe_allow_html=True
)
st.markdown("---")

# Inicializa manager
db_manager = init_manager()

# ========================================
# SIDEBAR - CONTROLES E STATUS
# ========================================
with st.sidebar:
    st.markdown("## 🎛️ PAINEL DE CONTROLE")
    st.markdown("---")

    # Status da conexão
    st.markdown("### 📡 Status da Conexão")
    try:
        maquinas_test = db_manager.get_maquinas()
        if maquinas_test:
            st.markdown(
                '<div class="status-connected">✅ CONECTADO</div>',
                unsafe_allow_html=True
            )
            st.caption(f"📊 {len(maquinas_test)} máquinas disponíveis")
        else:
            st.markdown(
                '<div class="status-disconnected">⚠️ SEM DADOS</div>',
                unsafe_allow_html=True
            )
    except Exception as e:
        st.markdown(
            '<div class="status-disconnected">❌ ERRO DE CONEXÃO</div>',
            unsafe_allow_html=True
        )
        with st.expander("Ver detalhes do erro"):
            st.code(str(e))

    st.markdown("---")

    # Botões de controle
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 ATUALIZAR", use_container_width=True):
            db_manager.limpar_cache()
            st.rerun()

    with col2:
        if st.button("🗑️ LIMPAR", use_container_width=True):
            st.session_state.pedidos_temp = []
            st.session_state.sequencia_gerada = []
            st.session_state.otimizacao_resultado = None
            st.rerun()

    st.markdown("---")

    # Estatísticas rápidas
    if st.session_state.pedidos_temp:
        st.markdown("### 📊 RESUMO RÁPIDO")
        total_pedidos = len(st.session_state.pedidos_temp)
        total_pecas = sum(p['quantidade'] for p in st.session_state.pedidos_temp)

        st.metric("Pedidos na Lista", total_pedidos)
        st.metric("Total de Peças", f"{total_pecas:,}")

    st.markdown("---")

    # Ajuda
    with st.expander("❓ AJUDA RÁPIDA"):
        st.markdown("""
        **FLUXO BÁSICO:**
        1. 📝 Cadastre produtos
        2. 📦 Lance pedidos
        3. 🧠 Gere otimização
        4. 📊 Visualize resultados

        **DICAS:**
        - Use formato DD/MM/AAAA para datas
        - Botão OTIMIZAR analisa melhor distribuição
        - Pedidos críticos aparecem em vermelho
        """)

# ========================================
# TABS PRINCIPAIS
# ========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 CADASTRO",
    "📦 PEDIDOS",
    "🧠 OTIMIZAÇÃO",
    "📊 PLANEJAMENTO",
    "📈 RELATÓRIOS"
])

# ========================================
# TAB 1: CADASTRO DE PRODUTOS
# ========================================
with tab1:
    st.markdown("## 📝 Cadastrar Novo Produto")
    st.markdown("Preencha as informações do produto para adicionar ao banco de dados.")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        with st.form("form_cadastro_produto", clear_on_submit=True):

            # Seção 1: Informações Básicas
            st.markdown("### 🔹 Informações Básicas")
            col1, col2 = st.columns(2)

            with col1:
                maquinas_disponiveis = db_manager.get_maquinas()

                if not maquinas_disponiveis:
                    st.warning("⚠️ Nenhuma máquina cadastrada. Adicione máquinas em DADOS_GERAIS")
                    maquina_selecionada = st.text_input("Máquina *", placeholder="Ex: 48 FUSOS UNIMAT")
                else:
                    maquina_selecionada = st.selectbox(
                        "Máquina *",
                        options=maquinas_disponiveis,
                        help="Selecione a máquina para este produto"
                    )

                referencia = st.text_input(
                    "Referência *",
                    placeholder="Ex: PROD-A-001",
                    help="Código único do produto"
                )

            with col2:
                referencia_maquina = st.text_input(
                    "Referência/Máquina *",
                    placeholder="Ex: REF-001",
                    help="Código de referência do produto para a máquina"
                )

                largura = st.number_input(
                    "Largura (mm)",
                    min_value=0.0,
                    value=0.0,
                    step=0.1
                )

            st.markdown("---")

            # Seção 2: Tempos e Produção
            st.markdown("### ⏱️ Tempos e Produção")
            col3, col4 = st.columns(2)

            with col3:
                tempo_producao = st.number_input(
                    "Tempo de Produção (min) *",
                    min_value=0.0,
                    value=0.0,
                    step=0.5,
                    help="Tempo em minutos para produzir uma unidade"
                )

                tempo_montagem = st.number_input(
                    "Tempo de Montagem (min) *",
                    min_value=0.0,
                    value=0.0,
                    step=0.5,
                    help="Tempo em minutos para montar uma unidade"
                )

            with col4:
                voltas_espula = st.number_input(
                    "Voltas na Espula",
                    min_value=0,
                    value=0,
                    step=1
                )

                producao_por_minuto = st.number_input(
                    "Produção por Minuto",
                    min_value=0.0,
                    value=0.0,
                    step=0.1
                )

            st.markdown("---")

            # Seção 3: Características Especiais
            st.markdown("### ⚙️ Características Especiais")
            col5, col6 = st.columns(2)

            with col5:
                cor = st.color_picker(
                    "Cor do Produto 🎨",
                    value="#667eea",
                    help="Cor para identificação visual no planejamento"
                )

            with col6:
                montagem_2x2 = st.selectbox(
                    "Montagem 2x2? ⚡",
                    options=["Não", "Sim"],
                    help="Produto requer montagem 2x2?"
                )

                tempo_montagem_2x2 = 0.0
                if montagem_2x2 == "Sim":
                    tempo_montagem_2x2 = st.number_input(
                        "Tempo Extra Montagem 2x2 (min)",
                        min_value=0.0,
                        value=0.0,
                        step=0.5,
                        help="Tempo adicional para montagem 2x2"
                    )

            st.markdown("---")

            # Botões de ação
            col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

            with col_btn1:
                submit_produto = st.form_submit_button(
                    "💾 SALVAR PRODUTO",
                    use_container_width=True,
                    type="primary"
                )

            with col_btn2:
                st.form_submit_button(
                    "🗑️ LIMPAR",
                    use_container_width=True
                )

            with col_btn3:
                st.form_submit_button(
                    "ℹ️ AJUDA",
                    use_container_width=True
                )

            if submit_produto:
                # Validações
                if not maquina_selecionada:
                    st.error("❌ Selecione uma máquina!")
                elif not referencia_maquina:
                    st.error("❌ Preencha a Referência/Máquina!")
                elif not referencia:
                    st.error("❌ Preencha a Referência!")
                elif tempo_producao == 0 and tempo_montagem == 0:
                    st.error("❌ Informe pelo menos um tempo (produção ou montagem)!")
                else:
                    # Prepara dados
                    produto_data = {
                        'maquina': maquina_selecionada,
                        'referenciaMaquina': referencia_maquina,
                        'referencia': referencia,
                        'tempoProducao': tempo_producao,
                        'tempoMontagem': tempo_montagem,
                        'voltasEspula': voltas_espula,
                        'producaoPorMinuto': producao_por_minuto,
                        'cor': cor,
                        'largura': largura,
                        'montagem2x2': montagem_2x2,
                        'tempoMontagem2x2': tempo_montagem_2x2
                    }

                    # Salva no Google Sheets
                    with st.spinner("💾 Salvando produto..."):
                        if db_manager.add_produto(produto_data):
                            st.success(f"✅ Produto '{referencia}' cadastrado com sucesso!")
                            st.balloons()
                        else:
                            st.error("❌ Erro ao cadastrar produto. Tente novamente.")

    with col_right:
        st.markdown("### 📋 PREVIEW")

        # Card de informações
        st.info("""
        **CAMPOS OBRIGATÓRIOS (*):**
        - Máquina
        - Referência/Máquina
        - Referência
        - Tempo de Produção OU Montagem

        **DICA:** A cor escolhida será usada
        na visualização do planejamento.
        """)

        # Preview da cor
        st.markdown("### 🎨 PREVIEW DA COR")
        st.markdown(
            f'<div style="width: 100%; height: 150px; background-color: #667eea; '
            f'border-radius: 20px; border: 3px solid #ddd; '
            f'box-shadow: 0 10px 30px rgba(0,0,0,0.2);"></div>',
            unsafe_allow_html=True
        )

        # Estatísticas
        if maquinas_disponiveis:
            st.markdown("### 📊 ESTATÍSTICAS")
            maq_count = len(maquinas_disponiveis)
            st.metric("Máquinas Cadastradas", maq_count)

    # Lista de produtos cadastrados
    st.markdown("---")
    st.markdown("## 📚 Produtos Cadastrados")

    if maquinas_disponiveis:
        maq_visualizar = st.selectbox(
            "Selecione a máquina para visualizar produtos:",
            options=maquinas_disponiveis,
            key="maq_visualizar_produtos"
        )

        if maq_visualizar:
            df_produtos = db_manager.get_produtos_por_maquina(maq_visualizar)

            if not df_produtos.empty:
                # Formata a visualização
                st.dataframe(
                    df_produtos,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                st.caption(f"📦 Total: {len(df_produtos)} produtos cadastrados para **{maq_visualizar}**")

                # Botão de exportação
                csv = df_produtos.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 EXPORTAR CSV",
                    data=csv,
                    file_name=f"produtos_{maq_visualizar}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )
            else:
                st.info(f"ℹ️ Nenhum produto cadastrado para {maq_visualizar}")
    else:
        st.warning("⚠️ Nenhuma máquina disponível. Cadastre máquinas em DADOS_GERAIS da planilha.")

# Continua no próximo bloco...

# ========================================
# TAB 2: LANÇAMENTO DE PEDIDOS (Simplificado)
# ========================================
with tab2:
    st.markdown("## 📦 Lançar Pedidos")
    
    # Formulário inline simplificado
    col1, col2, col3 = st.columns(3)
    
    with col1:
        clientes = db_manager.get_clientes()
        cliente = st.selectbox("Cliente", options=clientes if clientes else [""])
        
        maquinas = db_manager.get_maquinas()
        maquina = st.selectbox("Máquina", options=maquinas if maquinas else [""])
    
    with col2:
        ordem_compra = st.text_input("Ordem de Compra")
        data_entrega = st.date_input("Data Entrega", format="DD/MM/YYYY")
    
    with col3:
        bocas = st.number_input("Bocas", min_value=1, value=1)
        quantidade = st.number_input("Quantidade", min_value=1, value=1)
    
    # Produto baseado na máquina
    produto_selecionado = None
    if maquina:
        df_prods = db_manager.get_produtos_por_maquina(maquina)
        if not df_prods.empty:
            produto_selecionado = st.selectbox("Produto", df_prods['REFERENCIA'].tolist())
    
    if st.button("➕ ADICIONAR PEDIDO", type="primary"):
        if all([cliente, ordem_compra, maquina, produto_selecionado]):
            pedido = {
                'cliente': cliente,
                'ordem_compra': ordem_compra,
                'data_entrega': data_entrega.strftime('%d/%m/%Y'),
                'maquina': maquina,
                'bocas': bocas,
                'produto': produto_selecionado,
                'quantidade': quantidade
            }
            st.session_state.pedidos_temp.append(pedido)
            st.success(f"✅ Pedido adicionado! Total: {len(st.session_state.pedidos_temp)}")
            st.rerun()
        else:
            st.error("❌ Preencha todos os campos!")
    
    # Lista de pedidos
    if st.session_state.pedidos_temp:
        st.markdown("---")
        st.markdown("### 📋 LISTA DE PEDIDOS")
        df_temp = pd.DataFrame(st.session_state.pedidos_temp)
        st.dataframe(df_temp, use_container_width=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("💾 SALVAR TODOS", use_container_width=True):
                for p in st.session_state.pedidos_temp:
                    db_manager.add_pedido(p)
                st.success("✅ Salvos!")
                st.session_state.pedidos_temp = []
                st.rerun()
        
        with col_b:
            if st.button("📊 GERAR PLANEJAMENTO", use_container_width=True, type="primary"):
                # Gera sequência básica
                sequencia = []
                for pedido in st.session_state.pedidos_temp:
                    df_prod = db_manager.get_produtos_por_maquina(pedido['maquina'])
                    prod_info = df_prod[df_prod['REFERENCIA'] == pedido['produto']]
                    
                    if not prod_info.empty:
                        p_dict = prod_info.iloc[0].to_dict()
                        calc = ProductionCalculator()
                        tempo_unit = calc.calcular_tempo_total_produto(p_dict)
                        dias = calc.calcular_dias_ate_entrega(pedido['data_entrega'])
                        
                        sequencia.append({
                            'cliente': pedido['cliente'],
                            'ordem_compra': pedido['ordem_compra'],
                            'produto': pedido['produto'],
                            'maquina': pedido['maquina'],
                            'quantidade': pedido['quantidade'],
                            'bocas': pedido['bocas'],
                            'tempo_unitario': tempo_unit,
                            'tempo_total': tempo_unit * pedido['quantidade'],
                            'data_entrega': pedido['data_entrega'],
                            'dias_para_entrega': dias,
                            'prioridade': 1000 - dias,
                            'cor': p_dict.get('COR', '#CCCCCC')
                        })
                
                sequencia = sorted(sequencia, key=lambda x: x['prioridade'], reverse=True)
                for i, item in enumerate(sequencia, 1):
                    item['ordem'] = i
                
                st.session_state.sequencia_gerada = sequencia
                st.success("✅ Planejamento gerado! Veja nas próximas abas")

# ========================================
# TAB 3: OTIMIZAÇÃO INTELIGENTE
# ========================================
with tab3:
    st.markdown("## 🧠 ANÁLISE E OTIMIZAÇÃO INTELIGENTE")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 20px; color: white; text-align: center;'>
        <h2>🎯 Otimizador Inteligente de Produção</h2>
        <p>Analisa urgência, distribui bocas e sugere melhor sequência</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.pedidos_temp:
        st.info("ℹ️ Adicione pedidos na aba 'PEDIDOS' primeiro")
    else:
        # Estatísticas antes da otimização
        st.markdown("### 📊 ANÁLISE PRÉVIA")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Pedidos", len(st.session_state.pedidos_temp))
        with col2:
            total_pecas = sum(p['quantidade'] for p in st.session_state.pedidos_temp)
            st.metric("Total de Peças", f"{total_pecas:,}")
        with col3:
            maquinas_usadas = len(set(p['maquina'] for p in st.session_state.pedidos_temp))
            st.metric("Máquinas Utilizadas", maquinas_usadas)
        
        st.markdown("---")
        
        # BOTÃO MÁGICO DE OTIMIZAÇÃO
        col_center = st.columns([1, 2, 1])[1]
        with col_center:
            if st.button("🚀 OTIMIZAR DISTRIBUIÇÃO", use_container_width=True, type="primary"):
                with st.spinner("🧠 Analisando e otimizando..."):
                    # Prepara dados dos produtos
                    produtos_completos = pd.DataFrame()
                    for maq in set(p['maquina'] for p in st.session_state.pedidos_temp):
                        df_maq = db_manager.get_produtos_por_maquina(maq)
                        produtos_completos = pd.concat([produtos_completos, df_maq])
                    
                    # Executa otimização
                    optimizer = ProductionOptimizer()
                    resultado = optimizer.otimizar_distribuicao(
                        st.session_state.pedidos_temp,
                        produtos_completos
                    )
                    
                    st.session_state.otimizacao_resultado = resultado
                    st.success("✅ Otimização concluída!")
                    st.balloons()
                    st.rerun()
        
        # Mostra resultado da otimização
        if st.session_state.otimizacao_resultado:
            resultado = st.session_state.otimizacao_resultado
            
            st.markdown("---")
            st.markdown("## 📈 RESULTADO DA OTIMIZAÇÃO")
            
            # Métricas da otimização
            metricas = resultado['metricas']
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("⏱️ Tempo Total", f"{metricas['tempo_total_horas']:.1f}h")
            with col_m2:
                st.metric("🔴 Críticos", metricas['pedidos_criticos'])
            with col_m3:
                st.metric("🟡 Atenção", metricas['pedidos_atenção'])
            with col_m4:
                st.metric("✅ Eficiência", f"{metricas['eficiencia_geral']}%")
            
            # Alertas
            if resultado['alertas']:
                st.markdown("---")
                st.markdown("### ⚠️ ALERTAS IMPORTANTES")
                
                for alerta in resultado['alertas']:
                    if alerta['tipo'] == 'critico':
                        st.error(f"🔴 {alerta['mensagem']}")
                    elif alerta['tipo'] == 'inviavel':
                        st.warning(f"⚠️ {alerta['mensagem']}")
            
            # Distribuição sugerida
            st.markdown("---")
            st.markdown("### 🎯 DISTRIBUIÇÃO OTIMIZADA POR MÁQUINA")
            
            for maquina, distribuicao in resultado['sugestoes'].items():
                with st.expander(f"🔧 {maquina} ({len(distribuicao)} pedidos)", expanded=True):
                    for item in distribuicao:
                        # Badge de urgência
                        if item['nivel_urgencia'] == 'CRÍTICO':
                            badge_class = "urgency-critico"
                        elif item['nivel_urgencia'] == 'ATENÇÃO':
                            badge_class = "urgency-atencao"
                        else:
                            badge_class = "urgency-ok"
                        
                        st.markdown(f"""
                        <div style='background: white; padding: 1rem; border-radius: 10px; 
                                    margin: 0.5rem 0; border-left: 5px solid {item['cor']};'>
                            <strong>[{item['ordem']}] {item['cliente']} - {item['produto']}</strong>
                            <span class='urgency-badge {badge_class}'>{item['nivel_urgencia']}</span>
                            <br>
                            📦 Qtd: {item['quantidade']} | 
                            ⏱️ Tempo: {item['tempo_total_horas']:.1f}h | 
                            📅 Entrega: {item['data_entrega']}
                            <br>
                            <small>Distribuição: {len(item['bocas_distribuicao'])} bocas</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Detalhe das bocas
                        cols_bocas = st.columns(len(item['bocas_distribuicao']))
                        for idx, boca_info in enumerate(item['bocas_distribuicao']):
                            with cols_bocas[idx]:
                                st.metric(
                                    f"Boca {boca_info['boca']}",
                                    f"{boca_info['quantidade']} un",
                                    f"{boca_info['tempo_horas']:.1f}h"
                                )
            
            # Relatório texto
            st.markdown("---")
            if st.button("📄 GERAR RELATÓRIO TEXTUAL"):
                relatorio = optimizer.gerar_relatorio_otimizacao(resultado)
                st.text_area("Relatório", relatorio, height=400)
                
                st.download_button(
                    label="📥 BAIXAR RELATÓRIO",
                    data=relatorio,
                    file_name=f"relatorio_otimizacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

# ========================================
# TAB 4: PLANEJAMENTO VISUAL
# ========================================
with tab4:
    st.markdown("## 📊 Visualização do Planejamento")
    
    if not st.session_state.sequencia_gerada:
        st.info("ℹ️ Gere um planejamento na aba 'PEDIDOS' ou 'OTIMIZAÇÃO' primeiro")
    else:
        sequencia = st.session_state.sequencia_gerada
        calc = ProductionCalculator()
        
        # Estatísticas
        stats = calc.gerar_relatorio_tempo(sequencia)
        render_stats_cards(stats)
        
        st.markdown("---")
        
        # Tabela
        st.markdown("### 📋 Sequência de Produção")
        render_production_table(sequencia)
        
        st.markdown("---")
        
        # Detalhamento por máquina
        st.markdown("### 🔧 Detalhamento por Máquina")
        render_sequencia_detalhada(sequencia)
        
        st.markdown("---")
        
        # Ocupação visual
        st.markdown("### 🏭 Mapa de Ocupação")
        ocupacao = calc.calcular_ocupacao_maquinas(sequencia)
        render_machine_visual(ocupacao)

# ========================================
# TAB 5: RELATÓRIOS
# ========================================
with tab5:
    st.markdown("## 📈 Relatórios e Análises")
    
    if not st.session_state.sequencia_gerada:
        st.info("ℹ️ Gere um planejamento primeiro")
    else:
        sequencia = st.session_state.sequencia_gerada
        df_seq = pd.DataFrame(sequencia)
        
        # Relatório consolidado
        st.markdown("### 📊 RELATÓRIO CONSOLIDADO")
        
        calc = ProductionCalculator()
        stats = calc.gerar_relatorio_tempo(sequencia)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⏱️ Tempos")
            st.write(f"- Tempo Total: **{stats['tempo_total_horas']:.1f} horas**")
            st.write(f"- Dias: **{stats['tempo_total_dias']:.1f} dias**")
            st.write(f"- Tempo Médio/Peça: **{stats['tempo_medio_por_peca']:.1f} min**")
        
        with col2:
            st.markdown("#### 📦 Produção")
            st.write(f"- Total de Peças: **{stats['total_pecas']:,}**")
            st.write(f"- Total de Pedidos: **{stats['total_pedidos']}**")
        
        st.markdown("---")
        
        # Distribuição por máquina
        st.markdown("### 🔧 Distribuição por Máquina")
        dist_maq = df_seq.groupby('maquina').agg({
            'quantidade': 'sum',
            'tempo_total': 'sum',
            'ordem': 'count'
        }).reset_index()
        dist_maq.columns = ['Máquina', 'Total Peças', 'Tempo (min)', 'Pedidos']
        dist_maq['Tempo (h)'] = (dist_maq['Tempo (min)'] / 60).round(2)
        
        st.dataframe(dist_maq, use_container_width=True)
        
        st.markdown("---")
        
        # Export
        st.markdown("### 💾 EXPORTAR DADOS")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            csv = df_seq.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 BAIXAR CSV COMPLETO",
                data=csv,
                file_name=f"planejamento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            csv_simples = dist_maq.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 BAIXAR RESUMO",
                data=csv_simples,
                file_name=f"resumo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 20px; color: white; margin-top: 2rem;'>
    <h3>🏭 Sistema Profissional de Planejamento de Produção v3.0</h3>
    <p>Desenvolvido com ❤️ usando Python + Streamlit + Google Sheets</p>
    <small>© 2025 - Todos os direitos reservados</small>
</div>
""", unsafe_allow_html=True)
