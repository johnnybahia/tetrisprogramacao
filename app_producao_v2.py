"""
Sistema de Planejamento de Produção - Versão 2.0
Integrado com Google Sheets
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Adiciona o diretório de módulos ao path
sys.path.append(str(Path(__file__).parent))

from modules.database_manager import GoogleSheetsManager
from modules.calculator import ProductionCalculator
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
    page_title="Sistema de Planejamento de Produção",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# CSS CUSTOMIZADO
# ========================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #ff7f0e;
        padding-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

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

# ========================================
# HEADER
# ========================================
st.markdown('<div class="main-header">🏭 Sistema de Planejamento de Produção</div>',
            unsafe_allow_html=True)
st.markdown("---")

# Inicializa manager
db_manager = init_manager()

# ========================================
# SIDEBAR - CONTROLES
# ========================================
with st.sidebar:
    st.markdown("### 🏭 Sistema de Produção")

    st.markdown("### ⚙️ Controles")

    if st.button("🔄 Atualizar Dados", use_container_width=True):
        db_manager.limpar_cache()
        st.rerun()

    st.markdown("---")

    st.markdown("### 📊 Status da Conexão")
    try:
        maquinas_test = db_manager.get_maquinas()
        if maquinas_test:
            st.success("✅ Conectado ao Google Sheets")
            st.caption(f"Máquinas disponíveis: {len(maquinas_test)}")
        else:
            st.warning("⚠️ Conectado mas sem dados")
    except Exception as e:
        st.error("❌ Erro de conexão")
        st.caption(str(e))

    st.markdown("---")

    # Informações
    st.markdown("### ℹ️ Ajuda")
    with st.expander("Como usar"):
        st.markdown("""
        **1. Cadastro de Produtos:**
        - Selecione a máquina
        - Preencha os dados do produto
        - Clique em 'Salvar Produto'

        **2. Lançamento de Pedidos:**
        - Selecione cliente, ordem, etc.
        - Escolha o produto
        - Adicione à lista

        **3. Planejamento:**
        - Veja a sequência otimizada
        - Analise tempos e prazos
        - Exporte se necessário
        """)

# ========================================
# TABS PRINCIPAIS
# ========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Cadastro de Produtos",
    "📦 Lançamento de Pedidos",
    "📊 Planejamento Visual",
    "📋 Relatórios"
])

# ========================================
# TAB 1: CADASTRO DE PRODUTOS
# ========================================
with tab1:
    st.markdown('<div class="section-header">Cadastrar Novo Produto</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("form_cadastro_produto", clear_on_submit=True):
            st.markdown("#### Informações Básicas")

            col_a, col_b = st.columns(2)

            with col_a:
                # Carrega máquinas disponíveis
                maquinas_disponiveis = db_manager.get_maquinas()

                if not maquinas_disponiveis:
                    st.warning("⚠️ Nenhuma máquina cadastrada. Adicione máquinas em DADOS_GERAIS")
                    maquina_selecionada = st.text_input("Máquina",
                        placeholder="Ex: 48 FUSOS UNIMAT")
                else:
                    maquina_selecionada = st.selectbox(
                        "Máquina *",
                        options=maquinas_disponiveis,
                        help="Selecione a máquina para este produto"
                    )

                referencia_maquina = st.text_input(
                    "Referência/Máquina *",
                    placeholder="Ex: REF-001",
                    help="Código de referência do produto para a máquina"
                )

                referencia = st.text_input(
                    "Referência *",
                    placeholder="Ex: PROD-A-001",
                    help="Código único do produto"
                )

                largura = st.number_input(
                    "Largura (mm)",
                    min_value=0.0,
                    value=0.0,
                    step=0.1
                )

            with col_b:
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

            st.markdown("#### Características Especiais")

            col_c, col_d = st.columns(2)

            with col_c:
                cor = st.color_picker(
                    "Cor do Produto",
                    value="#00cc66",
                    help="Cor para identificação visual"
                )

            with col_d:
                montagem_2x2 = st.selectbox(
                    "Montagem 2x2?",
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

            col_submit, col_clear = st.columns(2)

            with col_submit:
                submit_produto = st.form_submit_button(
                    "💾 Salvar Produto",
                    use_container_width=True,
                    type="primary"
                )

            with col_clear:
                st.form_submit_button(
                    "🗑️ Limpar",
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
                    with st.spinner("Salvando produto..."):
                        if db_manager.add_produto(produto_data):
                            st.success(f"✅ Produto '{referencia}' cadastrado com sucesso!")
                            st.balloons()
                        else:
                            st.error("❌ Erro ao cadastrar produto. Tente novamente.")

    with col2:
        st.markdown("#### 📋 Preview")

        st.info("""
        **Campos Obrigatórios (*):**
        - Máquina
        - Referência/Máquina
        - Referência
        - Tempo de Produção
        - Tempo de Montagem
        """)

        st.markdown("#### 🎨 Visualização")
        st.markdown(
            f'<div style="width: 100px; height: 100px; '
            f'background-color: #00cc66; border: 2px solid #333; '
            f'border-radius: 10px; margin: 20px auto;"></div>',
            unsafe_allow_html=True
        )

    # Lista de produtos cadastrados
    st.markdown("---")
    st.markdown('<div class="section-header">Produtos Cadastrados</div>',
                unsafe_allow_html=True)

    maquinas = db_manager.get_maquinas()

    if maquinas:
        maq_visualizar = st.selectbox(
            "Selecione a máquina para visualizar produtos:",
            options=maquinas,
            key="maq_visualizar"
        )

        if maq_visualizar:
            df_produtos = db_manager.get_produtos_por_maquina(maq_visualizar)

            if not df_produtos.empty:
                st.dataframe(df_produtos, use_container_width=True, hide_index=True)
                st.caption(f"Total: {len(df_produtos)} produtos cadastrados para {maq_visualizar}")
            else:
                st.info(f"Nenhum produto cadastrado para {maq_visualizar}")
    else:
        st.warning("Nenhuma máquina disponível")

# ========================================
# TAB 2: LANÇAMENTO DE PEDIDOS
# ========================================
with tab2:
    st.markdown('<div class="section-header">Lançar Novo Pedido</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("form_lancamento_pedido", clear_on_submit=True):
            st.markdown("#### Informações do Pedido")

            col_a, col_b = st.columns(2)

            with col_a:
                # Carrega dados
                clientes = db_manager.get_clientes()
                ordens = db_manager.get_ordens()
                datas = db_manager.get_datas_entrega()
                maquinas = db_manager.get_maquinas()

                # Se não tem clientes, permite digitar
                if not clientes:
                    cliente = st.text_input("Cliente *", placeholder="Digite o nome do cliente")
                else:
                    cliente = st.selectbox("Cliente *", options=clientes)

                # Se não tem ordens, permite digitar
                if not ordens:
                    ordem_compra = st.text_input("Ordem de Compra *",
                        placeholder="Digite a ordem")
                else:
                    ordem_compra = st.selectbox("Ordem de Compra *", options=ordens)

                # Data de entrega
                if not datas:
                    data_entrega = st.date_input(
                        "Data de Entrega *",
                        value=datetime.now() + timedelta(days=30),
                        min_value=datetime.now()
                    )
                else:
                    data_entrega = st.selectbox("Data de Entrega *", options=datas)

            with col_b:
                # Máquina
                if not maquinas:
                    st.error("❌ Cadastre máquinas primeiro em DADOS_GERAIS")
                    maquina = st.text_input("Máquina", disabled=True)
                else:
                    maquina = st.selectbox("Máquina *", options=maquinas)

                bocas = st.number_input(
                    "Número de Bocas *",
                    min_value=1,
                    value=1,
                    step=1,
                    help="Quantidade de bocas disponíveis na máquina"
                )

                quantidade = st.number_input(
                    "Quantidade *",
                    min_value=1,
                    value=1,
                    step=1,
                    help="Quantidade total a produzir"
                )

            st.markdown("#### Seleção de Produto")

            # Carrega produtos da máquina selecionada
            if maquina and maquinas:
                df_produtos_maq = db_manager.get_produtos_por_maquina(maquina)

                if not df_produtos_maq.empty:
                    produtos_opcoes = df_produtos_maq['REFERENCIA'].tolist()
                    produto_selecionado = st.selectbox(
                        "Produto *",
                        options=produtos_opcoes,
                        help=f"Produtos disponíveis para {maquina}"
                    )

                    # Mostra informações do produto
                    produto_info = df_produtos_maq[
                        df_produtos_maq['REFERENCIA'] == produto_selecionado
                    ].iloc[0]

                    col_info1, col_info2, col_info3 = st.columns(3)

                    with col_info1:
                        st.metric("Tempo Produção",
                                f"{produto_info['TEMPO DE PRODUÇÃO']}min")
                    with col_info2:
                        st.metric("Tempo Montagem",
                                f"{produto_info['TEMPO DE MONTAGEM']}min")
                    with col_info3:
                        tempo_total = ProductionCalculator.calcular_tempo_total_produto(
                            produto_info.to_dict()
                        )
                        st.metric("Tempo Total/Unidade", f"{tempo_total}min")

                else:
                    st.warning(f"⚠️ Nenhum produto cadastrado para {maquina}")
                    produto_selecionado = None
            else:
                produto_selecionado = None

            st.markdown("---")

            submit_pedido = st.form_submit_button(
                "➕ Adicionar Pedido à Lista",
                use_container_width=True,
                type="primary"
            )

            if submit_pedido:
                # Validações
                if not cliente:
                    st.error("❌ Selecione um cliente!")
                elif not ordem_compra:
                    st.error("❌ Informe a ordem de compra!")
                elif not data_entrega:
                    st.error("❌ Selecione a data de entrega!")
                elif not maquina:
                    st.error("❌ Selecione uma máquina!")
                elif not produto_selecionado:
                    st.error("❌ Selecione um produto!")
                else:
                    # Adiciona à lista temporária
                    pedido = {
                        'cliente': cliente,
                        'ordem_compra': ordem_compra,
                        'data_entrega': str(data_entrega),
                        'maquina': maquina,
                        'bocas': bocas,
                        'produto': produto_selecionado,
                        'quantidade': quantidade
                    }

                    st.session_state.pedidos_temp.append(pedido)
                    st.success(f"✅ Pedido adicionado! Total: {len(st.session_state.pedidos_temp)}")
                    st.rerun()

    with col2:
        st.markdown("#### 📊 Resumo")

        if st.session_state.pedidos_temp:
            total_pedidos = len(st.session_state.pedidos_temp)
            total_pecas = sum(p['quantidade'] for p in st.session_state.pedidos_temp)

            st.metric("Pedidos na Lista", total_pedidos)
            st.metric("Total de Peças", total_pecas)

            if st.button("🗑️ Limpar Lista", use_container_width=True):
                st.session_state.pedidos_temp = []
                st.rerun()
        else:
            st.info("Nenhum pedido na lista")

    # Lista de pedidos temporários
    if st.session_state.pedidos_temp:
        st.markdown("---")
        st.markdown('<div class="section-header">Pedidos Adicionados</div>',
                    unsafe_allow_html=True)

        df_pedidos_temp = pd.DataFrame(st.session_state.pedidos_temp)
        st.dataframe(df_pedidos_temp, use_container_width=True, hide_index=True)

        col_action1, col_action2 = st.columns(2)

        with col_action1:
            if st.button("📊 Gerar Planejamento", use_container_width=True, type="primary"):
                with st.spinner("Gerando planejamento..."):
                    # Gera sequência
                    sequencia = []

                    for pedido in st.session_state.pedidos_temp:
                        # Busca informações do produto
                        df_prod = db_manager.get_produtos_por_maquina(pedido['maquina'])
                        produto_info = df_prod[
                            df_prod['REFERENCIA'] == pedido['produto']
                        ]

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

                    st.session_state.sequencia_gerada = sequencia

                    st.success("✅ Planejamento gerado! Veja na aba 'Planejamento Visual'")
                    st.balloons()

        with col_action2:
            if st.button("💾 Salvar no Google Sheets", use_container_width=True):
                with st.spinner("Salvando pedidos..."):
                    erros = 0
                    for pedido in st.session_state.pedidos_temp:
                        if not db_manager.add_pedido(pedido):
                            erros += 1

                    if erros == 0:
                        st.success("✅ Todos os pedidos foram salvos!")
                        st.session_state.pedidos_temp = []
                        st.rerun()
                    else:
                        st.error(f"❌ {erros} pedidos falharam ao salvar")

# ========================================
# TAB 3: PLANEJAMENTO VISUAL
# ========================================
with tab3:
    st.markdown('<div class="section-header">Planejamento de Produção</div>',
                unsafe_allow_html=True)

    if st.session_state.sequencia_gerada:
        sequencia = st.session_state.sequencia_gerada
        calc = ProductionCalculator()

        # Estatísticas
        stats = calc.gerar_relatorio_tempo(sequencia)
        render_stats_cards(stats)

        st.markdown("---")

        # Tabela de sequência
        st.markdown("### 📋 Sequência de Produção Otimizada")
        render_production_table(sequencia)

        st.markdown("---")

        # Visualização por máquina
        st.markdown("### 🔧 Detalhamento por Máquina")
        render_sequencia_detalhada(sequencia)

        st.markdown("---")

        # Ocupação das máquinas
        st.markdown("### 🏭 Ocupação das Máquinas")
        ocupacao = calc.calcular_ocupacao_maquinas(sequencia)
        render_machine_visual(ocupacao)

    else:
        st.info("👈 Adicione pedidos na aba 'Lançamento de Pedidos' e gere o planejamento")

# ========================================
# TAB 4: RELATÓRIOS
# ========================================
with tab4:
    st.markdown('<div class="section-header">Relatórios e Análises</div>',
                unsafe_allow_html=True)

    if st.session_state.sequencia_gerada:
        sequencia = st.session_state.sequencia_gerada
        calc = ProductionCalculator()

        # Relatório consolidado
        st.markdown("### 📊 Relatório Consolidado")

        stats = calc.gerar_relatorio_tempo(sequencia)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ⏱️ Tempos de Produção")
            st.write(f"- **Tempo Total:** {stats['tempo_total_horas']:.1f} horas "
                    f"({stats['tempo_total_dias']:.1f} dias)")
            st.write(f"- **Total de Peças:** {stats['total_pecas']:,}")
            st.write(f"- **Total de Pedidos:** {stats['total_pedidos']}")
            st.write(f"- **Tempo Médio/Peça:** {stats['tempo_medio_por_peca']:.1f} min")

        with col2:
            st.markdown("#### 🎯 Análise de Prazos")

            # Analisa cada pedido
            pedidos_criticos = 0
            pedidos_atenção = 0
            pedidos_ok = 0

            for item in sequencia:
                dias = item['dias_para_entrega']
                if dias < 7:
                    pedidos_criticos += 1
                elif dias < 15:
                    pedidos_atenção += 1
                else:
                    pedidos_ok += 1

            st.write(f"- 🔴 **Críticos (< 7 dias):** {pedidos_criticos}")
            st.write(f"- 🟡 **Atenção (7-15 dias):** {pedidos_atenção}")
            st.write(f"- 🟢 **OK (> 15 dias):** {pedidos_ok}")

        st.markdown("---")

        # Distribuição por máquina
        st.markdown("### 🔧 Distribuição por Máquina")

        df_seq = pd.DataFrame(sequencia)

        # Agrupa por máquina
        dist_maq = df_seq.groupby('maquina').agg({
            'quantidade': 'sum',
            'tempo_total': 'sum',
            'ordem': 'count'
        }).reset_index()

        dist_maq.columns = ['Máquina', 'Total Peças', 'Tempo Total (min)', 'Nº Pedidos']
        dist_maq['Tempo (horas)'] = (dist_maq['Tempo Total (min)'] / 60).round(2)

        st.dataframe(dist_maq, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Exportação
        st.markdown("### 💾 Exportar Dados")

        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            # Converte para CSV
            csv = df_seq.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"planejamento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_exp2:
            # Converte para Excel
            st.info("📊 Export Excel em desenvolvimento")

    else:
        st.info("👈 Gere um planejamento primeiro na aba 'Lançamento de Pedidos'")

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        Sistema de Planejamento de Produção v2.0 |
        Desenvolvido com ❤️ usando Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
