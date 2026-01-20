"""
Componentes de interface reutilizáveis
"""
import streamlit as st
import pandas as pd
from typing import Dict, List
import plotly.graph_objects as go
import plotly.express as px


def render_product_card(produto: Dict, index: int = 0):
    """
    Renderiza card de produto

    Args:
        produto: Dicionário com dados do produto
        index: Índice do produto
    """
    cor = produto.get('COR', '#CCCCCC')

    with st.container():
        col1, col2, col3 = st.columns([1, 3, 2])

        with col1:
            # Quadrado com a cor do produto
            st.markdown(
                f"""
                <div style="width: 50px; height: 50px; background-color: {cor};
                            border: 2px solid #333; border-radius: 5px;"></div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(f"**{produto.get('REFERENCIA', 'N/A')}**")
            st.caption(f"Tempo: {produto.get('TEMPO DE PRODUÇÃO', 0)}min + "
                      f"{produto.get('TEMPO DE MONTAGEM', 0)}min")

        with col3:
            if produto.get('MONTAGEM 2X2') == 'Sim':
                st.badge("2x2", type="secondary")


def render_machine_visual(ocupacao: Dict[str, List[Dict]]):
    """
    Renderiza visualização das máquinas

    Args:
        ocupacao: Dicionário com ocupação por máquina
    """
    st.markdown("""
    <style>
        .machine-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }
        .machine-box {
            border: 2px solid #444;
            background-color: #f0f2f6;
            border-radius: 8px;
            padding: 15px;
            min-width: 200px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .machine-title {
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 10px;
            color: #333;
        }
        .boca-container {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .boca-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 5px;
            border-radius: 4px;
            background-color: white;
        }
        .boca-color {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 1px solid #666;
        }
        .boca-text {
            font-size: 11px;
            color: #555;
        }
    </style>
    """, unsafe_allow_html=True)

    html_output = '<div class="machine-container">'

    for maquina, bocas_list in ocupacao.items():
        html_output += f'<div class="machine-box">'
        html_output += f'<div class="machine-title">🔧 {maquina}</div>'
        html_output += '<div class="boca-container">'

        for boca_info in bocas_list:
            cor = boca_info.get('cor', '#CCCCCC')
            produto = boca_info.get('produto', 'N/A')
            qtd = boca_info.get('quantidade', 0)
            tempo = boca_info.get('tempo_horas', 0)
            boca_num = boca_info.get('boca', 1)

            html_output += f'''
            <div class="boca-item">
                <div class="boca-color" style="background-color: {cor};"></div>
                <div class="boca-text">
                    Boca {boca_num}: {produto} ({qtd} un - {tempo:.1f}h)
                </div>
            </div>
            '''

        html_output += '</div></div>'

    html_output += '</div>'

    st.markdown(html_output, unsafe_allow_html=True)


def render_gantt_timeline(sequencia: List[Dict]):
    """
    Renderiza linha do tempo Gantt

    Args:
        sequencia: Sequência de produção
    """
    if not sequencia:
        st.info("Nenhum pedido para exibir")
        return

    # Prepara dados para o Gantt
    df_gantt = []
    tempo_acumulado = 0

    for item in sequencia:
        inicio = tempo_acumulado
        fim = tempo_acumulado + item['tempo_total']

        df_gantt.append({
            'Tarefa': f"{item['cliente']} - {item['produto']}",
            'Início': inicio,
            'Fim': fim,
            'Máquina': item['maquina'],
            'Cor': item.get('cor', '#CCCCCC')
        })

        tempo_acumulado = fim

    df = pd.DataFrame(df_gantt)

    # Cria gráfico Gantt
    fig = px.timeline(
        df,
        x_start='Início',
        x_end='Fim',
        y='Tarefa',
        color='Máquina',
        title='Linha do Tempo de Produção'
    )

    fig.update_yaxes(categoryorder='total ascending')
    fig.update_layout(xaxis_title='Tempo (minutos)', height=400)

    st.plotly_chart(fig, use_container_width=True)


def render_production_table(sequencia: List[Dict]):
    """
    Renderiza tabela de sequência de produção

    Args:
        sequencia: Sequência de produção
    """
    if not sequencia:
        st.info("Nenhum pedido na sequência")
        return

    # Prepara DataFrame
    df = pd.DataFrame(sequencia)

    # Seleciona colunas relevantes
    colunas_exibir = [
        'ordem', 'cliente', 'produto', 'maquina', 'quantidade',
        'bocas', 'tempo_total', 'data_entrega', 'dias_para_entrega'
    ]

    df_display = df[colunas_exibir].copy()

    # Renomeia colunas
    df_display.columns = [
        'Ordem', 'Cliente', 'Produto', 'Máquina', 'Qtd',
        'Bocas', 'Tempo Total (min)', 'Data Entrega', 'Dias p/ Entrega'
    ]

    # Formata tempo
    df_display['Tempo Total (h)'] = (df_display['Tempo Total (min)'] / 60).round(2)

    # Aplica estilo
    def highlight_urgente(row):
        if row['Dias p/ Entrega'] < 7:
            return ['background-color: #ffcccc'] * len(row)
        elif row['Dias p/ Entrega'] < 15:
            return ['background-color: #ffffcc'] * len(row)
        else:
            return ['background-color: #ccffcc'] * len(row)

    styled_df = df_display.style.apply(highlight_urgente, axis=1)

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # Legenda
    st.caption("🟥 Vermelho: Entrega em menos de 7 dias | "
              "🟨 Amarelo: Entrega entre 7-15 dias | "
              "🟩 Verde: Mais de 15 dias")


def render_stats_cards(stats: Dict):
    """
    Renderiza cards de estatísticas

    Args:
        stats: Dicionário com estatísticas
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="⏱️ Tempo Total",
            value=f"{stats['tempo_total_horas']:.1f}h",
            delta=f"{stats['tempo_total_dias']:.1f} dias"
        )

    with col2:
        st.metric(
            label="📦 Total de Peças",
            value=f"{stats['total_pecas']:,}",
        )

    with col3:
        st.metric(
            label="📋 Total de Pedidos",
            value=stats['total_pedidos']
        )

    with col4:
        st.metric(
            label="⚡ Tempo Médio/Peça",
            value=f"{stats['tempo_medio_por_peca']:.1f}min"
        )


def render_sequencia_detalhada(sequencia: List[Dict]):
    """
    Renderiza sequência de produção detalhada por máquina

    Args:
        sequencia: Sequência de produção
    """
    if not sequencia:
        st.info("Nenhuma sequência para exibir")
        return

    # Agrupa por máquina
    maquinas = {}
    for item in sequencia:
        maq = item['maquina']
        if maq not in maquinas:
            maquinas[maq] = []
        maquinas[maq].append(item)

    # Renderiza por máquina
    for maquina, itens in maquinas.items():
        with st.expander(f"🔧 {maquina} ({len(itens)} pedidos)", expanded=True):
            for idx, item in enumerate(itens, 1):
                col1, col2, col3 = st.columns([1, 4, 2])

                with col1:
                    # Cor do produto
                    cor = item.get('cor', '#CCCCCC')
                    st.markdown(
                        f'<div style="width: 40px; height: 40px; '
                        f'background-color: {cor}; border: 2px solid #333; '
                        f'border-radius: 5px;"></div>',
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(f"**[{idx}] {item['cliente']} - {item['produto']}**")
                    st.caption(
                        f"📦 Quantidade: {item['quantidade']} | "
                        f"🔢 Bocas: {item['bocas']} | "
                        f"⏱️ Tempo: {item['tempo_total']/60:.1f}h"
                    )

                with col3:
                    dias = item['dias_para_entrega']
                    if dias < 7:
                        st.error(f"🚨 {dias} dias")
                    elif dias < 15:
                        st.warning(f"⚠️ {dias} dias")
                    else:
                        st.success(f"✅ {dias} dias")

            st.markdown("---")
