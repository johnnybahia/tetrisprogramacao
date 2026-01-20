# ⚡ QUICK START - Início Rápido

## 🎯 Setup em 5 Minutos

### 1️⃣ Instalar Dependências (1 min)
```bash
pip install -r requirements.txt
```

### 2️⃣ Configurar Google Apps Script (2 min)

1. Abra: https://docs.google.com/spreadsheets/d/1TP1rN4V8nz2d7pTqPXXzK4I75ROkxDv-0GMQIx6R9SU/edit
2. **Extensões > Apps Script**
3. Cole o código de: `google_apps_script.js`
4. **Implantar > Nova implantação > Aplicativo da Web**
5. Configurar:
   - Executar como: **Eu**
   - Quem tem acesso: **Qualquer pessoa**
6. **COPIE A URL**

### 3️⃣ Configurar URL (1 min)

Edite: `config/config.yaml`

```yaml
google_apps_script_url: "COLE_SUA_URL_AQUI"
```

### 4️⃣ Executar (1 min)
```bash
streamlit run app_producao_v2.py
```

**Pronto! 🎉**

---

## 📋 Checklist Inicial

Antes de usar, certifique-se:

- [x] Planilha tem aba: **DADOS_GERAIS**
- [x] Aba DADOS_GERAIS tem colunas: CLIENTE, ORDEM DE COMPRA, DATA DE ENTREGA, MAQUINAS, BOCAS
- [x] Apps Script está implantado
- [x] URL está no config.yaml
- [x] Dependências instaladas

---

## 🚀 Primeiro Uso

### 1. Cadastre uma Máquina
Na planilha DADOS_GERAIS, adicione uma linha:
```
CLIENTE: Cliente Teste
ORDEM DE COMPRA: OC-001
DATA DE ENTREGA: 2024-03-01
MAQUINAS: 48 FUSOS UNIMAT
BOCAS: 10
```

### 2. Cadastre um Produto
No sistema (aba "Cadastro de Produtos"):
- Máquina: 48 FUSOS UNIMAT
- Referência: PROD-001
- Tempo Produção: 15 min
- Tempo Montagem: 10 min
- Salvar

### 3. Lance um Pedido
Na aba "Lançamento de Pedidos":
- Selecione: Cliente, Ordem, Data, Máquina
- Escolha o produto cadastrado
- Quantidade: 100
- Adicionar

### 4. Gere o Planejamento
- Clique em "Gerar Planejamento"
- Veja na aba "Planejamento Visual"

**✅ Sistema funcionando!**

---

## ⚠️ Problemas Comuns

| Erro | Solução |
|------|---------|
| "Erro de conexão" | Verifique URL no config.yaml |
| "Nenhuma máquina" | Adicione dados em DADOS_GERAIS |
| "Erro ao salvar" | Reimplante o Apps Script com permissões corretas |

---

## 📞 Ajuda

- Documentação completa: `README.md`
- Código do Apps Script: `google_apps_script.js`
- Configurações: `config/config.yaml`
