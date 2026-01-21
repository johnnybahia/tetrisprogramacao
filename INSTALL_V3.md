# 🚀 GUIA DE INSTALAÇÃO - VERSÃO 3.0

## ⚡ INSTALAÇÃO RÁPIDA (5 Minutos)

### Passo 1: Instalar Dependências

```bash
pip install --upgrade pip
pip install streamlit pandas plotly requests pyyaml python-dateutil
```

**Ou use o requirements.txt:**
```bash
pip install -r requirements.txt --upgrade
```

### Passo 2: Verificar Versões

```bash
streamlit --version
# Deve ser >= 1.32.0
```

**Se a versão for antiga:**
```bash
pip install --upgrade streamlit
```

### Passo 3: Configurar Google Apps Script

#### 3.1 Abrir Google Sheets
```
https://docs.google.com/spreadsheets/d/1TP1rN4V8nz2d7pTqPXXzK4I75ROkxDv-0GMQIx6R9SU/edit
```

#### 3.2 Ir para Apps Script
```
Extensões → Apps Script
```

#### 3.3 Colar o Código
- Delete o código padrão
- Abra: `google_apps_script.js`
- Copie TODO o conteúdo
- Cole no editor
- Salve (Ctrl+S ou 💾)

#### 3.4 Implantar
```
1. Clique em: Implantar → Nova implantação
2. Tipo: Aplicativo da Web
3. Executar como: Eu
4. Quem tem acesso: Qualquer pessoa
5. Implantar
6. COPIE A URL!
```

A URL será algo como:
```
https://script.google.com/macros/s/ABC123XYZ.../exec
```

### Passo 4: Configurar URL

Edite: `config/config.yaml`

```yaml
google_apps_script_url: "COLE_SUA_URL_AQUI"
```

### Passo 5: Executar!

```bash
streamlit run app_producao_v3.py
```

**Pronto! 🎉**

O sistema abrirá automaticamente no navegador.

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### ❌ Erro: "No module named 'yaml'"
```bash
pip install pyyaml
```

### ❌ Erro: "use_container_width"
```bash
pip install streamlit --upgrade
streamlit --version  # Deve ser >= 1.32.0
```

### ❌ Erro: "CSS não carrega"
Verifique se existe: `assets/style.css`

```bash
ls assets/
# Deve mostrar: style.css
```

### ❌ Erro: "Nenhuma máquina disponível"
**Causa:** Planilha DADOS_GERAIS vazia

**Solução:**
1. Abra a planilha no Google Sheets
2. Aba: DADOS_GERAIS
3. Adicione pelo menos uma linha:

| CLIENTE | ORDEM DE COMPRA | DATA DE ENTREGA | MAQUINAS | BOCAS |
|---------|-----------------|-----------------|----------|-------|
| Teste | OC-001 | 01/03/2025 | 48 FUSOS UNIMAT | 10 |

4. Volte ao sistema
5. Clique em "🔄 ATUALIZAR"

### ❌ Erro de conexão
**Causa:** URL do Apps Script incorreta

**Solução:**
1. Verifique se fez o deploy correto
2. Copie a URL novamente
3. Cole no `config/config.yaml`
4. Reinicie o Streamlit

---

## 🎨 VERIFICAR SE ESTÁ FUNCIONANDO

### Teste 1: Status de Conexão
```
✅ Sidebar deve mostrar: "✅ CONECTADO"
```

### Teste 2: Carregar Máquinas
```
✅ Tab CADASTRO deve listar máquinas no dropdown
```

### Teste 3: CSS Profissional
```
✅ Fundo deve ser gradiente roxo/azul
✅ Título deve ter cores animadas
✅ Botões devem ter gradientes
```

Se todos os ✅ aparecerem, está tudo OK!

---

## 🆙 ATUALIZAR DE V2 PARA V3

### Opção 1: Git Pull (Recomendado)
```bash
git pull origin claude/google-sheets-item-listing-4Ojbk
pip install -r requirements.txt --upgrade
streamlit run app_producao_v3.py
```

### Opção 2: Download Manual
1. Baixe os novos arquivos:
   - app_producao_v3.py
   - modules/optimizer.py
   - assets/style.css
2. Coloque na pasta do projeto
3. Execute

---

## 💻 EXECUTAR EM DIFERENTES SISTEMAS

### Windows
```powershell
# CMD ou PowerShell
cd C:\Users\seu_usuario\tetrisprogramacao
streamlit run app_producao_v3.py
```

### Linux/Mac
```bash
cd ~/tetrisprogramacao
streamlit run app_producao_v3.py
```

### Google Colab (Não recomendado)
```python
!pip install streamlit pyyaml
!streamlit run app_producao_v3.py &
```

---

## 🌐 DEPLOY NA NUVEM (SEM INSTALAR NADA!)

### Streamlit Cloud (Grátis)

#### Passo 1: GitHub
```bash
git add .
git commit -m "Deploy V3"
git push
```

#### Passo 2: Streamlit Cloud
1. Acesse: https://share.streamlit.io
2. Login com GitHub
3. New app
4. Repository: johnnybahia/tetrisprogramacao
5. Branch: claude/google-sheets-item-listing-4Ojbk
6. Main file: app_producao_v3.py
7. Deploy!

#### Passo 3: Configurar Secrets
```
No Streamlit Cloud:
Settings → Secrets

Cole o conteúdo de config/config.yaml
```

#### Passo 4: URL Pública
```
Você receberá uma URL tipo:
https://seu-app.streamlit.app

Compartilhe com sua equipe!
```

**VANTAGENS:**
- ✅ Sem instalar Python
- ✅ Acesso via URL
- ✅ Multi-usuário automático
- ✅ 100% grátis
- ✅ Atualização automática

---

## 📋 CHECKLIST DE INSTALAÇÃO

- [ ] Python instalado (≥ 3.8)
- [ ] Dependências instaladas
- [ ] Streamlit ≥ 1.32.0
- [ ] Google Apps Script configurado
- [ ] URL copiada e colada no config.yaml
- [ ] Planilha tem dados em DADOS_GERAIS
- [ ] Arquivo assets/style.css existe
- [ ] Executou: `streamlit run app_producao_v3.py`
- [ ] Sidebar mostra "CONECTADO"
- [ ] Design está bonito (gradientes, etc)

---

## 🎓 PRIMEIRO USO

### Tutorial Básico

#### 1. CADASTRE UM PRODUTO
```
Tab: CADASTRO
Máquina: 48 FUSOS UNIMAT
Referência: TESTE-001
Tempo Produção: 10 min
Tempo Montagem: 5 min
Cor: Azul (#3b82f6)
→ SALVAR
```

#### 2. LANCE UM PEDIDO
```
Tab: PEDIDOS
Cliente: Cliente Teste
Ordem: OC-001
Data: [30 dias a partir de hoje]
Máquina: 48 FUSOS UNIMAT
Produto: TESTE-001
Quantidade: 100
Bocas: 5
→ ADICIONAR À LISTA
→ GERAR PLANEJAMENTO
```

#### 3. OTIMIZE
```
Tab: OTIMIZAÇÃO
→ Clique em: 🚀 OTIMIZAR DISTRIBUIÇÃO
→ Veja a mágica acontecer!
```

#### 4. VISUALIZE
```
Tab: PLANEJAMENTO
→ Veja sequência, tempos, cores
```

#### 5. EXPORTE
```
Tab: RELATÓRIOS
→ BAIXAR CSV
```

**Pronto! Agora você sabe usar o sistema!** 🎉

---

## 🔐 SEGURANÇA

### Dados Sensíveis

**NÃO commite:**
- ❌ credentials.json
- ❌ Tokens de acesso
- ❌ Senhas

**Já no .gitignore:**
- ✅ credentials.json
- ✅ *.key
- ✅ *.pem

### Permissões do Apps Script

```
O Apps Script TEM acesso a:
- ✅ Ler sua planilha
- ✅ Escrever na planilha
- ✅ Criar abas

Não tem acesso a:
- ❌ Outras planilhas
- ❌ Gmail
- ❌ Drive (além da planilha)
```

---

## 🎯 PRÓXIMOS PASSOS

Após instalação, recomendamos:

1. 📖 Ler: `CHANGELOG_V3.md`
2. 🧪 Testar todas as funcionalidades
3. 🎨 Customizar cores (opcional)
4. 👥 Treinar equipe
5. 🌐 Deploy na nuvem
6. 📊 Usar em produção

---

## 📞 AJUDA

### Documentação
- `README.md` - Guia completo
- `QUICKSTART.md` - Início rápido
- `CHANGELOG_V3.md` - Novidades V3
- `INSTALL_V3.md` - Este arquivo

### Suporte
Se tiver problemas:
1. Leia a seção "Solução de Problemas" acima
2. Verifique o Checklist
3. Consulte os arquivos de documentação

---

**Boa sorte! 🚀**

Qualquer dúvida, consulte a documentação ou entre em contato.

---

**Versão:** 3.0.0
**Última atualização:** 21/01/2025
**Status:** ✅ Testado e Aprovado
