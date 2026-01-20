# 🏭 Sistema de Planejamento de Produção

Sistema completo de planejamento e sequenciamento de produção integrado com Google Sheets.

## 📋 Funcionalidades

### ✅ Cadastro de Produtos
- Interface intuitiva para cadastrar produtos
- Seleção de máquina via dropdown
- Campos customizados por tipo de máquina
- Suporte a montagem 2x2
- Código de cores para identificação visual
- Salvamento automático no Google Sheets

### ✅ Lançamento de Pedidos
- Seleção de cliente, ordem de compra e data de entrega via dropdowns
- Escolha de produtos baseada na máquina selecionada
- Cálculo automático de tempos
- Lista temporária de pedidos antes de salvar
- Geração de planejamento otimizado

### ✅ Planejamento Visual
- Sequenciamento automático por prioridade (data de entrega)
- Distribuição inteligente entre bocas
- Visualização colorida por produto
- Cálculo de tempos e prazos
- Alertas para pedidos urgentes

### ✅ Relatórios
- Estatísticas consolidadas
- Distribuição por máquina
- Análise de prazos críticos
- Exportação para CSV
- Métricas de produtividade

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Conta Google
- Planilha Google Sheets configurada

### Passo 1: Clone o Repositório
```bash
git clone <seu-repositorio>
cd tetrisprogramacao
```

### Passo 2: Instale as Dependências
```bash
pip install -r requirements.txt
```

### Passo 3: Configure o Google Apps Script

1. Abra sua planilha Google Sheets
2. Vá em: **Extensões > Apps Script**
3. Delete o código padrão
4. Copie TODO o conteúdo do arquivo `google_apps_script.js`
5. Cole no editor do Apps Script
6. Clique em **Salvar projeto** (💾)
7. Clique em **Implantar > Nova implantação**
8. Em "Tipo", selecione: **Aplicativo da Web**
9. Configure:
   - **Executar como:** Eu
   - **Quem tem acesso:** Qualquer pessoa
10. Clique em **Implantar**
11. **COPIE A URL GERADA** (você vai precisar dela!)

### Passo 4: Configure a URL no Sistema

1. Abra o arquivo: `config/config.yaml`
2. Substitua a URL na linha `google_apps_script_url`:

```yaml
google_apps_script_url: "SUA_URL_AQUI"
```

3. Substitua também o ID da planilha (opcional):

```yaml
spreadsheet_id: "SEU_ID_AQUI"
```

---

## ▶️ Como Executar

### Localmente (Desenvolvimento)
```bash
streamlit run app_producao_v2.py
```

O sistema abrirá automaticamente no navegador em: `http://localhost:8501`

### Deploy na Nuvem (Streamlit Cloud)

1. Faça push do código para o GitHub
2. Acesse: [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu repositório
4. Configure o arquivo principal: `app_producao_v2.py`
5. Deploy!

**✨ VANTAGEM:** Outras pessoas podem acessar via URL pública!

---

## 📁 Estrutura do Projeto

```
tetrisprogramacao/
├── app_producao_v2.py              # Aplicativo principal (EXECUTE ESTE)
├── app_producao.py                 # Versão antiga (backup)
├── google_apps_script.js           # Código para Google Apps Script
├── requirements.txt                # Dependências Python
├── README.md                       # Este arquivo
│
├── config/
│   └── config.yaml                 # Configurações (URL, IDs, etc.)
│
└── modules/
    ├── __init__.py
    ├── database_manager.py         # Conexão com Google Sheets
    ├── calculator.py               # Cálculos de tempo e sequência
    └── ui_components.py            # Componentes visuais
```

---

## 📊 Estrutura da Planilha Google Sheets

### Aba: DADOS_GERAIS
**Colunas obrigatórias:**
- CLIENTE
- ORDEM DE COMPRA
- DATA DE ENTREGA
- MAQUINAS
- BOCAS

**Exemplo:**
| CLIENTE | ORDEM DE COMPRA | DATA DE ENTREGA | MAQUINAS | BOCAS |
|---------|----------------|-----------------|----------|-------|
| Cliente A | OC-001 | 2024-02-15 | 48 FUSOS UNIMAT | 10 |
| Cliente B | OC-002 | 2024-03-01 | 32 FUSOS UNIMAT | 8 |

### Abas Dinâmicas por Máquina

**Nome da aba:** `DADOS_[NOME_DA_MAQUINA]`

Exemplos:
- `DADOS_48_FUSOS_UNIMAT`
- `DADOS_32_FUSOS_UNIMAT`
- `DADOS_FABRIZI_12`

**Colunas obrigatórias:**
- REFERÊNCIAS/MÁQUINA
- TEMPO DE PRODUÇÃO
- TEMPO DE MONTAGEM
- VOLTAS NA ESPULA
- PRODUÇÃO POR MINUTO
- COR
- REFERENCIA
- LARGURA
- MONTAGEM 2X2
- TEMPO MONTAGEM 2X2

**Exemplo:**
| REFERÊNCIAS/MÁQUINA | TEMPO DE PRODUÇÃO | TEMPO DE MONTAGEM | ... | COR | REFERENCIA |
|---------------------|-------------------|-------------------|-----|-----|------------|
| REF-001 | 15 | 10 | ... | #00cc66 | PROD-A |
| REF-002 | 20 | 8 | ... | #3366ff | PROD-B |

---

## 🎯 Como Usar o Sistema

### 1️⃣ Cadastrar Produtos

1. Acesse a aba: **"📝 Cadastro de Produtos"**
2. Selecione a **Máquina**
3. Preencha os campos obrigatórios:
   - Referência/Máquina
   - Referência
   - Tempo de Produção
   - Tempo de Montagem
4. Escolha a **cor** do produto
5. Se necessário, marque **Montagem 2x2** e informe o tempo extra
6. Clique em **"💾 Salvar Produto"**

✅ O produto será salvo automaticamente na aba correspondente no Google Sheets!

### 2️⃣ Lançar Pedidos

1. Acesse a aba: **"📦 Lançamento de Pedidos"**
2. Selecione nos dropdowns:
   - Cliente
   - Ordem de Compra
   - Data de Entrega
   - Máquina
3. Informe:
   - Número de Bocas disponíveis
   - Quantidade a produzir
4. Selecione o **Produto** (lista filtrada pela máquina escolhida)
5. Clique em **"➕ Adicionar Pedido à Lista"**
6. Repita para adicionar mais pedidos
7. Quando terminar, clique em:
   - **"📊 Gerar Planejamento"** → Gera a sequência otimizada
   - **"💾 Salvar no Google Sheets"** → Salva os pedidos na planilha

### 3️⃣ Visualizar Planejamento

1. Acesse a aba: **"📊 Planejamento Visual"**
2. Veja:
   - ⏱️ **Estatísticas:** Tempo total, peças, pedidos
   - 📋 **Sequência Otimizada:** Ordem de produção por prioridade
   - 🔧 **Detalhamento por Máquina:** Instruções detalhadas
   - 🏭 **Ocupação:** Visualização colorida das bocas

**Cores dos alertas:**
- 🟥 **Vermelho:** Entrega em menos de 7 dias (URGENTE!)
- 🟨 **Amarelo:** Entrega entre 7-15 dias (ATENÇÃO)
- 🟩 **Verde:** Mais de 15 dias (OK)

### 4️⃣ Gerar Relatórios

1. Acesse a aba: **"📋 Relatórios"**
2. Veja:
   - Relatório consolidado
   - Distribuição por máquina
   - Análise de prazos críticos
3. Clique em **"📥 Download CSV"** para exportar

---

## 🔄 Atualizar Dados

Se você fizer alterações direto na planilha Google Sheets:

1. Clique no botão: **"🔄 Atualizar Dados"** (sidebar)
2. Ou recarregue a página

O sistema usa **cache** para melhorar a performance. O cache expira a cada 5 minutos automaticamente.

---

## 🛠️ Solução de Problemas

### ❌ "Erro de conexão"
**Causa:** URL do Apps Script incorreta ou não implantado

**Solução:**
1. Verifique se você implantou o Apps Script
2. Copie a URL correta da implantação
3. Cole no arquivo `config/config.yaml`
4. Reinicie o Streamlit

### ❌ "Nenhuma máquina disponível"
**Causa:** Aba DADOS_GERAIS vazia ou sem a coluna MAQUINAS

**Solução:**
1. Abra a planilha Google Sheets
2. Na aba DADOS_GERAIS, adicione dados
3. Certifique-se que existe a coluna "MAQUINAS"
4. Atualize os dados no sistema

### ❌ "Nenhum produto cadastrado"
**Causa:** Não existem abas de dados para a máquina selecionada

**Solução:**
1. Use o sistema para cadastrar produtos (recomendado)
2. OU crie manualmente a aba: `DADOS_NOME_DA_MAQUINA`
3. Adicione as colunas obrigatórias

### ❌ "Erro ao salvar"
**Causa:** Permissões do Apps Script

**Solução:**
1. No Apps Script, vá em: **Implantar > Gerenciar implantações**
2. Clique em ✏️ **Editar**
3. Em "Quem tem acesso", selecione: **Qualquer pessoa**
4. Salve a nova versão

---

## 🌐 Acesso Multi-usuário

### Opção 1: Streamlit Cloud (Recomendado)
✅ Grátis
✅ URL pública
✅ Acesso de qualquer lugar
✅ Sem necessidade de servidor

1. Faça push para GitHub
2. Deploy no [Streamlit Cloud](https://share.streamlit.io)
3. Compartilhe a URL com sua equipe

### Opção 2: Servidor Local (Rede Interna)
1. Execute em um computador da rede:
```bash
streamlit run app_producao_v2.py --server.address 0.0.0.0
```
2. Outras pessoas na mesma rede acessam via: `http://IP_DO_COMPUTADOR:8501`

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique o arquivo `README.md`
2. Confira se seguiu todos os passos de instalação
3. Teste a conexão com o Google Sheets
4. Verifique os logs no terminal

---

## 📝 Notas Importantes

⚠️ **IMPORTANTE:** Sempre que alterar o código do Google Apps Script, você precisa fazer uma **NOVA IMPLANTAÇÃO**

⚠️ **CACHE:** O sistema usa cache de 5 minutos. Para forçar atualização, use o botão "🔄 Atualizar Dados"

⚠️ **NOMENCLATURA:** Os nomes das máquinas em DADOS_GERAIS devem corresponder exatamente às abas (ex: "48 FUSOS UNIMAT" → "DADOS_48_FUSOS_UNIMAT")

---

## 🎨 Personalização

### Alterar Cores Padrão
Edite o arquivo: `config/config.yaml`

```yaml
default_colors:
  - "#00cc66"  # Verde
  - "#3366ff"  # Azul
  # Adicione mais cores aqui
```

### Alterar Tempo de Cache
Edite: `config/config.yaml`

```yaml
cache:
  ttl: 300  # segundos (5 minutos)
```

---

## 🚀 Melhorias Futuras

- [ ] Export para Excel
- [ ] Gráficos de Gantt interativos
- [ ] Notificações por email
- [ ] Histórico de planejamentos
- [ ] Dashboard de KPIs
- [ ] Integração com outros sistemas

---

## 📜 Licença

Este projeto é de uso livre para fins internos da empresa.

---

## ✨ Desenvolvido com

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/)
- [Google Apps Script](https://script.google.com/)

---

**Versão:** 2.0
**Data:** Janeiro 2025
**Status:** ✅ Pronto para produção
