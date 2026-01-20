import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Visualizador de Fábrica", layout="wide")

# --- CSS PARA DESENHAR AS MÁQUINAS (RETÂNGULOS E CÍRCULOS) ---
st.markdown("""
<style>
    /* O Container da Bancada (Retângulo) */
    .bancada {
        border: 2px solid #444;
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 10px;
        margin: 5px;
        display: inline-flex; /* Fica um do lado do outro */
        flex-direction: column;
        align-items: center;
        width: 110px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Área das Cabeças (Para alinhar os círculos) */
    .cabecas-container {
        display: flex;
        justify_content: center;
        gap: 5px;
        margin-bottom: 5px;
    }

    /* A Máquina/Cabeça (Círculo) */
    .maquina-circle {
        width: 25px;
        height: 25px;
        border-radius: 50%;
        border: 1px solid #666;
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.3);
    }
    
    /* Cores dos Produtos (Classes dinâmicas) */
    .prod-m6034 { background-color: #00cc66; } /* Verde */
    .prod-mr140019 { background-color: #3366ff; } /* Azul */
    .prod-m6019 { background-color: #ff9933; } /* Laranja */
    .prod-livre { background-color: #d1d1d1; } /* Cinza */
    
    /* Texto */
    .label-maq { font-size: 10px; font-weight: bold; color: #333; }
    .label-prod { font-size: 9px; color: #555; }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Controle de Produção Visual")
st.markdown("---")

# ==============================================================================
# 1. SETUP (LATERAL)
# ==============================================================================
st.sidebar.header("1. Máquinas (Bancadas)")

# Configuração Padrão
dados_maquinas_padrao = [
    {"Modelo": "Fabrizi 12", "Qtd Bancadas": 54, "Cabeças/Bancada": 1},
    {"Modelo": "Chinesa", "Qtd Bancadas": 21, "Cabeças/Bancada": 2},
]
df_recursos = st.sidebar.data_editor(pd.DataFrame(dados_maquinas_padrao), num_rows="dynamic", key="maquinas")

st.sidebar.header("2. Produtos")
# Cores para o visual
mapa_cores = {
    "M6034": "#00cc66 (Verde)",
    "MR140019": "#3366ff (Azul)",
    "M6019": "#ff9933 (Laranja)"
}
st.sidebar.write("Legenda de Cores:")
st.sidebar.text(f"M6034: Verde\nMR140019: Azul\nM6019: Laranja")

# ==============================================================================
# 2. ENTRADA DE PEDIDOS
# ==============================================================================
st.header("📦 Pedidos")
df_pedidos_padrao = pd.DataFrame([
    {"Pedido": "P1", "Produto": "M6034", "Qtd": 50},
    {"Pedido": "P2", "Produto": "MR140019", "Qtd": 30},
    {"Pedido": "P3", "Produto": "M6019", "Qtd": 60},
])
df_pedidos = st.data_editor(df_pedidos_padrao, num_rows="dynamic", use_container_width=True)

# ==============================================================================
# 3. LÓGICA DE DISTRIBUIÇÃO (SIMPLIFICADA PARA O VISUAL)
# ==============================================================================
# Aqui vamos criar uma lista "virtual" de todas as cabeças de produção e atribuir os pedidos
# sequencialmente apenas para gerar o visual.

if st.button("🔄 Gerar Mapa da Fábrica"):
    
    # A. Criar lista de todas as cabeças individuais disponíveis
    todas_cabecas = []
    
    for _, row in df_recursos.iterrows():
        modelo = row["Modelo"]
        qtd_bancadas = int(row["Qtd Bancadas"])
        num_cabecas = int(row["Cabeças/Bancada"])
        
        for b in range(qtd_bancadas):
            # Cria a bancada
            bancada_id = f"{modelo} {b+1}"
            cabecas_desta_bancada = []
            
            for c in range(num_cabecas):
                cabecas_desta_bancada.append({
                    "id_unico": f"{bancada_id}-C{c+1}",
                    "status": "Livre", # Vai virar o nome do produto
                    "cor_class": "prod-livre"
                })
            
            todas_cabecas.append({
                "bancada": bancada_id,
                "cabecas": cabecas_desta_bancada
            })

    # B. "Preencher" as máquinas com os pedidos (Lógica simples de preenchimento)
    # Transforma pedidos em uma fila de "unidades a fazer"
    fila_producao = []
    for _, ped in df_pedidos.iterrows():
        prod = ped["Produto"]
        # Definir classe CSS baseada no nome do produto
        css_class = "prod-livre"
        if "M6034" in prod: css_class = "prod-m6034"
        elif "MR140019" in prod: css_class = "prod-mr140019"
        elif "M6019" in prod: css_class = "prod-m6019"
        
        # Adiciona na fila (simplificado: 1 unidade ocupa 1 máquina visualmente neste exemplo)
        # Para ficar visualmente interessante, vamos distribuir proporcionalmente
        fila_producao.append({"prod": prod, "class": css_class})

    # C. Atribuição (Distribuir a fila nas máquinas)
    # Isso é apenas visual: pega o ultimo produto da fila e joga na máquina
    # Na vida real, ligaríamos isso ao cronograma de tempo
    
    iterator_fila = 0
    total_fila = len(fila_producao)
    
    # Vamos iterar sobre as BANCADAS e suas CABEÇAS
    layout_final = []
    
    # Modo de distribuição: Round Robin (vai jogando um pouco em cada pra ficar colorido)
    # Ou Sequencial. Vamos fazer sequencial nas cabeças globais.
    
    contador_global_cabecas = 0
    # Precisamos "achatá-lo" para distribuir, mas manter a estrutura de bancada para o HTML
    
    # Lógica simples de visualização:
    # Se temos 3 pedidos (50 de A, 30 de B, 60 de C), vamos pintar as máquinas
    # proporcionalmente.
    
    total_maquinas_reais = sum([len(b["cabecas"]) for b in todas_cabecas])
    
    # Calcular % de ocupação de cada produto
    total_pecas = df_pedidos["Qtd"].sum()
    if total_pecas == 0: total_pecas = 1
    
    # Cria uma lista mestra de cores para preencher as máquinas
    lista_cores_alocadas = []
    for _, ped in df_pedidos.iterrows():
        # Quantas máquinas esse pedido vai ocupar visualmente?
        # Regra de 3: (Qtd Pedido / Total Pedidos) * Total Máquinas
        slots_ocupados = int((ped["Qtd"] / total_pecas) * total_maquinas_reais)
        
        classe = "prod-livre"
        if "M6034" in str(ped["Produto"]): classe = "prod-m6034"
        elif "MR140019" in str(ped["Produto"]): classe = "prod-mr140019"
        elif "M6019" in str(ped["Produto"]): classe = "prod-m6019"
        
        lista_cores_alocadas.extend([{"prod": ped["Produto"], "class": classe}] * slots_ocupados)
    
    # Preencher com "Livre" se sobrar máquina
    while len(lista_cores_alocadas) < total_maquinas_reais:
        lista_cores_alocadas.append({"prod": "Livre", "class": "prod-livre"})
        
    # Agora aplica nas bancadas
    idx_cor = 0
    html_output = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
    
    for bancada in todas_cabecas:
        nome_bancada = bancada["bancada"]
        
        # Abre o Retângulo (Bancada)
        html_output += f'<div class="bancada"><span class="label-maq">{nome_bancada}</span><div class="cabecas-container">'
        
        # Desenha as Bolinhas (Cabeças)
        for cabeca in bancada["cabecas"]:
            if idx_cor < len(lista_cores_alocadas):
                info = lista_cores_alocadas[idx_cor]
                cor = info["class"]
                prod_nome = info["prod"]
                idx_cor += 1
            else:
                cor = "prod-livre"
                prod_nome = "Livre"
                
            # HTML da Bolinha
            html_output += f'<div class="maquina-circle {cor}" title="{prod_nome}"></div>'
            
        html_output += '</div>' # Fecha container cabeças
        
        # Legenda do produto embaixo da bancada (pega o do primeiro slot pra simplificar)
        html_output += '</div>' # Fecha Bancada
        
    html_output += '</div>'
    
    st.subheader("Mapa de Ocupação Atual")
    st.caption("Cada retângulo é uma bancada. Cada círculo é uma cabeça de produção.")
    st.markdown(html_output, unsafe_allow_html=True)
    
    st.info("💡 Passe o mouse sobre as bolinhas para ver qual produto está programado.")
