# 📋 CONFIGURAÇÃO DO GOOGLE APPS SCRIPT

## Passo 1: Abrir o Editor de Scripts

1. Abra sua planilha: https://docs.google.com/spreadsheets/d/1TP1rN4V8nz2d7pTqPXXzK4I75ROkxDv-0GMQIx6R9SU
2. Clique em **Extensões** → **Apps Script**
3. Você verá um editor de código

## Passo 2: Copiar o Código

1. Delete qualquer código que estiver no editor
2. Copie TODO o conteúdo do arquivo `google_apps_script.js` do seu projeto
3. Cole no editor do Google Apps Script
4. Clique em **Salvar** (ícone de disquete) ou Ctrl+S

## Passo 3: Implantar como Web App

1. No editor de scripts, clique em **Implantar** (botão azul no canto superior direito)
2. Escolha **Nova implantação**
3. Configure:
   - **Tipo**: Selecione "Web app" (ícone de engrenagem → Aplicativo da Web)
   - **Descrição**: "API para Sistema de Produção"
   - **Executar como**: Eu (seu email)
   - **Quem tem acesso**: Qualquer pessoa
4. Clique em **Implantar**

## Passo 4: Autorizar Permissões

1. Clique em **Autorizar acesso**
2. Escolha sua conta Google
3. Clique em **Avançado** (se aparecer aviso)
4. Clique em **Acessar [nome do projeto] (não seguro)**
5. Clique em **Permitir**

## Passo 5: Copiar a URL

1. Após a implantação, você verá uma tela com "URL do aplicativo da Web"
2. **COPIE ESSA URL** - será algo como:
   ```
   https://script.google.com/macros/s/AKfycby...../exec
   ```

## Passo 6: Configurar no Projeto

1. Abra o arquivo `config/config.yaml` no seu projeto
2. Cole a URL que você copiou no campo `google_apps_script_url`:
   ```yaml
   google_apps_script_url: "https://script.google.com/macros/s/SUA_URL_AQUI/exec"
   ```
3. Salve o arquivo

## Passo 7: Testar

Abra no navegador (substitua SUA_URL pela URL que você copiou):
```
https://script.google.com/macros/s/SUA_URL_AQUI/exec?action=getMaquinas
```

Você deve ver uma lista JSON com suas máquinas!

---

## 🔄 Se precisar atualizar o código no futuro:

1. Faça as alterações no editor
2. Salve (Ctrl+S)
3. Clique em **Implantar** → **Gerenciar implantações**
4. Clique no ícone de lápis (editar)
5. Em "Versão", escolha **Nova versão**
6. Clique em **Implantar**

---

## ✅ CHECKLIST

- [ ] Código colado no Apps Script
- [ ] Código salvo
- [ ] Implantado como Web App
- [ ] Permissões autorizadas
- [ ] URL copiada
- [ ] URL configurada no config.yaml
- [ ] Teste no navegador funcionou
- [ ] Servidor FastAPI reiniciado
