# 📊 Guia do Sistema de Planejamento Dinâmico de Produção

## 🎯 Visão Geral

Este sistema permite planejar a produção de forma dinâmica, considerando:
- **Disponibilidade das máquinas** (horas/dia disponíveis)
- **Calendário de trabalho** (feriados, fins de semana)
- **Sequenciamento inteligente** de pedidos
- **Cálculo automático** de datas de início e fim
- **Reordenação drag-and-drop** com recálculo automático

---

## 🔧 Configuração Inicial

### 1. Configurar Disponibilidade das Máquinas

A disponibilidade de cada máquina deve ser configurada na **célula K1** da aba correspondente no Google Sheets.

**Exemplo:**
- Aba: `DADOS_48_FUSOS_UNIMAT`
- Célula K1: `8` (indica 8 horas disponíveis por dia)

**Passos:**
1. Abra sua planilha Google Sheets
2. Acesse a aba da máquina (ex: `DADOS_48_FUSOS_UNIMAT`)
3. Na célula **K1**, digite o número de horas disponíveis por dia
4. Repita para todas as máquinas

**Valores recomendados:**
- Turno normal: `8` horas/dia
- Dois turnos: `16` horas/dia
- Três turnos: `24` horas/dia
- Meio período: `4` horas/dia

---

### 2. Atualizar o Google Apps Script

O Google Apps Script precisa ser atualizado para suportar a leitura da célula K1.

**Passos:**

1. Abra sua planilha Google Sheets
2. Vá em: **Extensões** > **Apps Script**
3. Cole o código atualizado do arquivo `google_apps_script.js`
4. Clique em **Salvar projeto**
5. Clique em **Implantar** > **Nova implantação**
6. Configure:
   - **Tipo**: Aplicativo da Web
   - **Executar como**: Eu
   - **Quem tem acesso**: Qualquer pessoa
7. Clique em **Implantar**
8. Copie a URL gerada
9. Cole no arquivo `config/config.yaml` na chave `google_apps_script_url`

---

## 📅 Configuração do Calendário de Trabalho

### Acessar a Página de Calendário

1. Execute o sistema: `python main.py`
2. Abra o navegador em: `http://localhost:8000`
3. Clique na aba **📅 Calendário**

### Configurar Fins de Semana

**Configuração Padrão:**
- Marque se trabalha aos **Sábados** por padrão
- Marque se trabalha aos **Domingos** por padrão
- Clique em **💾 Salvar Configuração**

**Exceções (Datas Específicas):**
1. Digite o ano desejado (ex: 2025)
2. Clique em **🔍 Carregar Fins de Semana**
3. Marque os sábados e domingos específicos que **SÃO dias de trabalho**
4. Clique em **💾 Salvar Seleção**

### Adicionar Feriados

1. No campo de texto, digite as datas dos feriados (uma por linha)
2. Formato: **DD/MM/AAAA**

**Exemplo:**
```
25/12/2025
01/01/2026
07/09/2026
20/11/2026
```

3. Clique em **➕ Adicionar Feriados**

**Lista de Feriados Nacionais Brasileiros (exemplo para 2025):**
```
01/01/2025
04/03/2025
18/04/2025
21/04/2025
01/05/2025
19/06/2025
07/09/2025
12/10/2025
02/11/2025
15/11/2025
20/11/2025
25/12/2025
```

### Remover Feriados

- Na lista de feriados cadastrados, clique em **Remover** ao lado da data

---

## 📦 Cadastro de Produtos e Pedidos

### 1. Cadastrar Produtos

1. Vá na aba **📝 Cadastro**
2. Preencha os campos:
   - **Máquina**: Selecione a máquina
   - **Referência**: Código do produto
   - **Tempo Produção**: Tempo em minutos
   - **Tempo Montagem**: Tempo de montagem em minutos
   - **Cor**: Cor para identificação visual
   - **Montagem 2x2**: Se tem montagem adicional
3. Clique em **💾 Salvar Produto**

### 2. Adicionar Pedidos

1. Vá na aba **📦 Pedidos**
2. Preencha os campos:
   - **Cliente**: Nome do cliente
   - **Ordem de Compra**: Número do pedido
   - **Data Entrega**: Data limite (DD/MM/AAAA)
   - **Máquina**: Selecione a máquina
   - **Produto**: Selecione o produto
   - **Bocas**: Número de bocas a utilizar
   - **Quantidade**: Quantidade de peças
3. Clique em **➕ Adicionar Pedido**
4. Repita para todos os pedidos

---

## 📊 Gerar Planejamento Dinâmico

### Passo a Passo

1. Adicione todos os pedidos (conforme seção anterior)
2. Vá na aba **📊 Planejamento**
3. (Opcional) Defina uma data de início customizada
4. Clique em **📊 Gerar Planejamento Dinâmico**

### O que o Sistema Calcula

✅ **Data de início** de cada pedido
✅ **Data de fim** de cada pedido
✅ **Dias úteis** necessários (excluindo feriados e fins de semana não trabalhados)
✅ **Horas totais** de produção
✅ **Alertas** para pedidos com margem apertada ou em atraso

### Visualização do Planejamento

O planejamento mostra:
- **Resumo Geral**: Total de pedidos, horas, pedidos críticos
- **Alertas**: Pedidos que terminarão após a data de entrega
- **Planejamento por Máquina**:
  - Disponibilidade (horas/dia)
  - Lista de pedidos em ordem de produção
  - Para cada pedido:
    - Cliente e produto
    - Data de início e fim
    - Data de entrega
    - Dias úteis necessários
    - Status (OK, ATENÇÃO, ATRASADO)

---

## 🔄 Reordenar Pedidos (Drag and Drop)

### Como Funciona

O sistema permite **arrastar e soltar** pedidos para reordenar a sequência de produção.

**Importante:** Só é possível reordenar pedidos **da mesma máquina**.

### Passos

1. No planejamento gerado, localize o pedido que deseja mover
2. Clique e **segure** o pedido (você verá um ícone de drag ⋮⋮ na lateral)
3. **Arraste** para a posição desejada
4. **Solte** o pedido
5. ⚡ O sistema **recalcula automaticamente** todas as datas!

### Recálculo Automático

Quando você move um pedido, o sistema:
1. Atualiza a ordem de produção
2. Recalcula as datas de início e fim de **todos os pedidos afetados**
3. Atualiza os alertas
4. Mostra o novo planejamento instantaneamente

---

## 💾 Salvar e Carregar Planos

### Salvar um Plano

1. Após gerar o planejamento, clique em **💾 Salvar Plano**
2. Digite um nome para o plano (ex: "Produção Janeiro 2025")
3. Clique em OK
4. ✅ Plano salvo com sucesso!

### Carregar um Plano Salvo

1. Clique em **📂 Carregar Plano**
2. Selecione o plano desejado da lista
3. Digite o número do plano
4. ✅ Plano carregado!

**Arquivos salvos em:** `config/production_plans.json`

---

## 🎯 Exemplo Prático Completo

### Cenário

**Empresa:** Fábrica de Elásticos
**Objetivo:** Planejar produção da semana

### 1. Configuração Inicial

```
Máquina: 48_FUSOS_UNIMAT
Disponibilidade (K1): 8 horas/dia
```

**Calendário:**
- Não trabalha aos sábados e domingos
- Feriado: 20/11/2025 (Dia da Consciência Negra)

### 2. Pedidos

| Cliente | Produto | Qtd | Entrega    | Bocas |
|---------|---------|-----|------------|-------|
| Cliente A | ELASTICO_10MM | 1000 | 25/11/2025 | 2 |
| Cliente B | ELASTICO_15MM | 500  | 22/11/2025 | 1 |
| Cliente C | ELASTICO_20MM | 800  | 28/11/2025 | 2 |

### 3. Adicionar Pedidos

1. Vá em **📦 Pedidos**
2. Adicione os 3 pedidos acima
3. Clique em **📊 Planejamento**
4. Clique em **📊 Gerar Planejamento Dinâmico**

### 4. Resultado

O sistema mostra:
- **Cliente B** - Início: 18/11, Fim: 21/11 (OK)
- **Cliente A** - Início: 22/11, Fim: 26/11 (ATENÇÃO - atraso de 1 dia)
- **Cliente C** - Início: 27/11, Fim: 29/11 (OK)

### 5. Ajuste Manual

Para priorizar Cliente A:
1. **Arraste** o pedido de Cliente A para o topo
2. O sistema recalcula:
   - **Cliente A** - Início: 18/11, Fim: 24/11 (OK)
   - **Cliente B** - Início: 25/11, Fim: 28/11 (ATENÇÃO)
   - **Cliente C** - Início: 29/11, Fim: 02/12 (ATENÇÃO)

---

## ⚠️ Dicas Importantes

### ✅ Boas Práticas

1. **Configure o calendário ANTES** de gerar planejamentos
2. **Revise a disponibilidade** das máquinas regularmente
3. **Salve planos importantes** para referência futura
4. **Use drag-and-drop** para ajustes finos após gerar o plano
5. **Verifique alertas** e tome ações preventivas

### ⚠️ Limitações

- Só é possível reordenar pedidos da mesma máquina
- O sistema não considera:
  - Setup de máquinas entre produtos diferentes
  - Manutenções programadas
  - Quebras de máquina
  - Disponibilidade de matéria-prima

### 🔧 Manutenção

**Atualizar feriados anualmente:**
- No início de cada ano, cadastre os feriados
- Atualize feriados municipais/estaduais específicos

**Revisar disponibilidade:**
- Ajuste a célula K1 se houver mudanças nos turnos
- Considere férias coletivas reduzindo temporariamente a disponibilidade

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se o Google Apps Script está atualizado
2. Confirme que a célula K1 tem um valor numérico válido
3. Verifique os logs do console (F12 no navegador)
4. Verifique os logs do servidor Python

---

## 🚀 Próximas Funcionalidades

Possíveis melhorias futuras:
- [ ] Considerar setup entre produtos
- [ ] Programação de manutenções
- [ ] Gráfico de Gantt visual
- [ ] Exportação para PDF/Excel
- [ ] Notificações de alertas por e-mail
- [ ] Análise de capacidade de produção
- [ ] Simulação de cenários

---

**Versão:** 4.0.0
**Data:** Janeiro 2025
**Desenvolvido com:** Python FastAPI + HTML/CSS/JS
