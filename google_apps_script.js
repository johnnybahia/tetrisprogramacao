// ========================================
// GOOGLE APPS SCRIPT - API PARA STREAMLIT
// ========================================
// Cole este código no Google Apps Script da sua planilha
// Extensões > Apps Script > Cole este código > Implante como Web App

function doGet(e) {
  const action = e.parameter.action;

  if (action === 'getAll') {
    return getAllData();
  } else if (action === 'getSheet') {
    return getSheetData(e.parameter.sheetName);
  } else if (action === 'getCell') {
    return getCellValue(e.parameter.sheetName, e.parameter.cell);
  } else if (action === 'getMaquinas') {
    return getMaquinas();
  } else if (action === 'getClientes') {
    return getClientes();
  } else if (action === 'getOrdens') {
    return getOrdens();
  } else if (action === 'getDatas') {
    return getDatasEntrega();
  }

  return ContentService.createTextOutput(JSON.stringify({error: 'Ação inválida'}))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const action = data.action;

    if (action === 'addProduto') {
      return addProduto(data);
    } else if (action === 'addPedido') {
      return addPedido(data);
    }

    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: 'Ação inválida'
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// ========================================
// FUNÇÕES GET (Leitura de dados)
// ========================================

function getAllData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ss.getSheets();
  let result = {};

  sheets.forEach(sheet => {
    const sheetName = sheet.getName();
    const data = sheet.getDataRange().getValues();
    const headers = data[0];
    const rows = data.slice(1);

    result[sheetName] = rows.map(row => {
      let obj = {};
      headers.forEach((header, index) => {
        obj[header] = row[index];
      });
      return obj;
    });
  });

  return ContentService.createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}

function getSheetData(sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(sheetName);

  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify({error: 'Aba não encontrada'}))
      .setMimeType(ContentService.MimeType.JSON);
  }

  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const rows = data.slice(1);

  const result = rows.map(row => {
    let obj = {};
    headers.forEach((header, index) => {
      obj[header] = row[index];
    });
    return obj;
  });

  return ContentService.createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}

function getCellValue(sheetName, cellAddress) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(sheetName);

  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify({
      error: 'Aba não encontrada',
      value: null
    })).setMimeType(ContentService.MimeType.JSON);
  }

  try {
    const cell = sheet.getRange(cellAddress);
    let value = cell.getValue();

    // Se for uma data, converte para string
    if (value instanceof Date) {
      value = value.toISOString().split('T')[0];
    }

    return ContentService.createTextOutput(JSON.stringify({
      value: value,
      cell: cellAddress,
      sheet: sheetName
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      error: error.toString(),
      value: null
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function getMaquinas() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('DADOS_GERAIS');

  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }

  const data = sheet.getDataRange().getValues();
  const maquinasIndex = data[0].indexOf('MAQUINAS');

  if (maquinasIndex === -1) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }

  const maquinas = data.slice(1)
    .map(row => row[maquinasIndex])
    .filter(m => m !== null && m !== undefined && m !== '');

  const uniqueMaquinas = [...new Set(maquinas)];

  return ContentService.createTextOutput(JSON.stringify(uniqueMaquinas))
    .setMimeType(ContentService.MimeType.JSON);
}

function getClientes() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('DADOS_GERAIS');

  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }

  const data = sheet.getDataRange().getValues();
  const clientesIndex = data[0].indexOf('CLIENTE');

  if (clientesIndex === -1) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }

  const clientes = data.slice(1)
    .map(row => row[clientesIndex])
    .filter(c => c !== null && c !== undefined && c !== '');

  const uniqueClientes = [...new Set(clientes)];

  return ContentService.createTextOutput(JSON.stringify(uniqueClientes))
    .setMimeType(ContentService.MimeType.JSON);
}

function getOrdens() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('DADOS_GERAIS');

  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }

  const data = sheet.getDataRange().getValues();
  const ordensIndex = data[0].indexOf('ORDEM DE COMPRA');

  if (ordensIndex === -1) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }

  const ordens = data.slice(1)
    .map(row => row[ordensIndex])
    .filter(o => o !== null && o !== undefined && o !== '');

  const uniqueOrdens = [...new Set(ordens)];

  return ContentService.createTextOutput(JSON.stringify(uniqueOrdens))
    .setMimeType(ContentService.MimeType.JSON);
}

function getDatasEntrega() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('DADOS_GERAIS');

  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }

  const data = sheet.getDataRange().getValues();
  const datasIndex = data[0].indexOf('DATA DE ENTREGA');

  if (datasIndex === -1) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }

  const datas = data.slice(1)
    .map(row => row[datasIndex])
    .filter(d => d !== null && d !== undefined && d !== '');

  const uniqueDatas = [...new Set(datas)].map(d => {
    if (d instanceof Date) {
      return d.toISOString().split('T')[0];
    }
    return d;
  });

  return ContentService.createTextOutput(JSON.stringify(uniqueDatas))
    .setMimeType(ContentService.MimeType.JSON);
}

// ========================================
// FUNÇÕES POST (Escrita de dados)
// ========================================

function addProduto(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const maquina = data.maquina;
  const sheetName = 'DADOS_' + maquina.replace(/\s+/g, '_').toUpperCase();

  let sheet = ss.getSheetByName(sheetName);

  // Se a aba não existe, cria
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);

    // Adiciona cabeçalhos
    const headers = [
      'REFERÊNCIAS/MÁQUINA',
      'TEMPO DE PRODUÇÃO',
      'TEMPO DE MONTAGEM',
      'VOLTAS NA ESPULA',
      'PRODUÇÃO POR MINUTO',
      'COR',
      'REFERENCIA',
      'LARGURA',
      'MONTAGEM 2X2',
      'TEMPO MONTAGEM 2X2'
    ];
    sheet.appendRow(headers);
  }

  // Calcula tempo total de montagem
  let tempoMontagemTotal = parseFloat(data.tempoMontagem) || 0;
  if (data.montagem2x2 === 'Sim' && data.tempoMontagem2x2) {
    tempoMontagemTotal += parseFloat(data.tempoMontagem2x2);
  }

  // Adiciona nova linha
  const newRow = [
    data.referenciaMaquina || '',
    data.tempoProducao || 0,
    tempoMontagemTotal,
    data.voltasEspula || 0,
    data.producaoPorMinuto || 0,
    data.cor || '#FFFFFF',
    data.referencia || '',
    data.largura || 0,
    data.montagem2x2 || 'Não',
    data.tempoMontagem2x2 || 0
  ];

  sheet.appendRow(newRow);

  return ContentService.createTextOutput(JSON.stringify({
    success: true,
    message: 'Produto adicionado com sucesso!',
    sheetName: sheetName
  })).setMimeType(ContentService.MimeType.JSON);
}

function addPedido(data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('DADOS_GERAIS');

  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: 'Aba DADOS_GERAIS não encontrada'
    })).setMimeType(ContentService.MimeType.JSON);
  }

  // Adiciona nova linha
  const newRow = [
    data.cliente || '',
    data.ordemCompra || '',
    data.dataEntrega || '',
    data.maquina || '',
    data.bocas || 0
  ];

  sheet.appendRow(newRow);

  return ContentService.createTextOutput(JSON.stringify({
    success: true,
    message: 'Pedido adicionado com sucesso!'
  })).setMimeType(ContentService.MimeType.JSON);
}

// ========================================
// INSTRUÇÕES DE DEPLOY
// ========================================
/*
COMO IMPLANTAR:

1. Abra sua planilha Google Sheets
2. Vá em: Extensões > Apps Script
3. Delete o código padrão e cole TODO este código
4. Clique em "Salvar projeto"
5. Clique em "Implantar" > "Nova implantação"
6. Em "Tipo", selecione "Aplicativo da Web"
7. Em "Executar como", selecione "Eu"
8. Em "Quem tem acesso", selecione "Qualquer pessoa"
9. Clique em "Implantar"
10. Copie a URL da Web App gerada
11. Cole essa URL no arquivo config.yaml do Streamlit

IMPORTANTE:
- Sempre que alterar o código, precisa fazer nova implantação
- Use "Nova implantação" para cada mudança
*/
