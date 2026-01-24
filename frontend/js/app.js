// Configuração da API
const API_URL = 'http://localhost:8000/api';

// Estado da aplicação
let pedidosTemporarios = [];
let sequenciaGerada = [];

// ========================================
// INICIALIZAÇÃO
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Sistema iniciado');

    // Verifica status da conexão
    checkStatus();

    // Carrega máquinas
    loadMaquinas();

    // Carrega pedidos cadastrados
    loadPedidosCadastrados();

    // Event listeners de navegação
    setupNavigation();

    // Event listeners de formulários
    setupForms();
});

// ========================================
// NAVEGAÇÃO
// ========================================

function setupNavigation() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const page = btn.dataset.page;
            showPage(page);
        });
    });
}

function showPage(pageName) {
    // Remove active de todos
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    // Adiciona active no selecionado
    document.getElementById('page-' + pageName).classList.add('active');
    document.querySelector('[data-page="' + pageName + '"]').classList.add('active');
}

// ========================================
// STATUS E CONEXÃO
// ========================================

async function checkStatus() {
    try {
        const response = await fetch(API_URL + '/status');
        const data = await response.json();

        const badge = document.getElementById('statusBadge');
        const text = document.getElementById('statusText');

        if (data.status === 'connected') {
            badge.classList.add('connected');
            text.textContent = '✅ Conectado (' + data.maquinas_count + ' máquinas)';
        } else {
            badge.classList.add('error');
            text.textContent = '❌ Erro de conexão';
        }
    } catch (error) {
        console.error('Erro ao verificar status:', error);
        const badge = document.getElementById('statusBadge');
        badge.classList.add('error');
        document.getElementById('statusText').textContent = '❌ Erro';
    }
}

// ========================================
// MÁQUINAS
// ========================================

// Estado global para pedidos cadastrados
let pedidosCadastradosGlobal = [];

async function loadMaquinas() {
    try {
        const response = await fetch(API_URL + '/maquinas');
        const data = await response.json();

        const selectCadastro = document.getElementById('inputMaquina');

        selectCadastro.innerHTML = '<option value="">Selecione...</option>';

        data.maquinas.forEach(maq => {
            selectCadastro.innerHTML += '<option value="' + maq + '">' + maq + '</option>';
        });

        selectCadastro.addEventListener('change', (e) => {
            if (e.target.value) {
                loadProdutosCadastrados(e.target.value);
            }
        });

    } catch (error) {
        console.error('Erro ao carregar máquinas:', error);
    }
}

// ========================================
// PEDIDOS CADASTRADOS (DADOS_GERAIS)
// ========================================

// Carrega pedidos cadastrados da aba DADOS_GERAIS
async function loadPedidosCadastrados() {
    try {
        const response = await fetch(API_URL + '/pedidos-cadastrados');
        const data = await response.json();

        pedidosCadastradosGlobal = data.pedidos || [];

        // Preenche select de clientes (únicos)
        const clientes = [...new Set(pedidosCadastradosGlobal.map(p => p.CLIENTE))].filter(c => c);
        const selectCliente = document.getElementById('inputCliente');

        selectCliente.innerHTML = '<option value="">Selecione...</option>';
        clientes.forEach(cliente => {
            selectCliente.innerHTML += `<option value="${cliente}">${cliente}</option>`;
        });

        // Event listener para cliente
        selectCliente.removeEventListener('change', onClienteChange);
        selectCliente.addEventListener('change', onClienteChange);
    } catch (error) {
        console.error('Erro ao carregar pedidos cadastrados:', error);
    }
}

// Quando seleciona cliente, carrega ordens desse cliente
function onClienteChange(e) {
    const cliente = e.target.value;

    const selectOrdem = document.getElementById('inputOrdem');
    const selectData = document.getElementById('inputDataEntrega');
    const inputMaquina = document.getElementById('inputMaquinaPedido');
    const selectProduto = document.getElementById('inputProduto');

    if (!cliente) {
        selectOrdem.innerHTML = '<option value="">Selecione cliente primeiro</option>';
        selectOrdem.disabled = true;
        selectData.innerHTML = '<option value="">Selecione ordem primeiro</option>';
        selectData.disabled = true;
        inputMaquina.value = '';
        selectProduto.innerHTML = '<option value="">Selecione pedido completo primeiro</option>';
        selectProduto.disabled = true;
        return;
    }

    // Filtra pedidos do cliente
    const pedidosCliente = pedidosCadastradosGlobal.filter(p => p.CLIENTE === cliente);

    // Ordens únicas
    const ordens = [...new Set(pedidosCliente.map(p => p['ORDEM DE COMPRA']))].filter(o => o);

    selectOrdem.innerHTML = '<option value="">Selecione...</option>';
    ordens.forEach(ordem => {
        selectOrdem.innerHTML += `<option value="${ordem}">${ordem}</option>`;
    });
    selectOrdem.disabled = false;

    // Reseta data
    selectData.innerHTML = '<option value="">Selecione ordem primeiro</option>';
    selectData.disabled = true;

    // Reseta máquina e produto
    inputMaquina.value = '';
    selectProduto.innerHTML = '<option value="">Selecione pedido completo primeiro</option>';
    selectProduto.disabled = true;

    // Event listener para ordem (remove anteriores)
    selectOrdem.removeEventListener('change', onOrdemChange);
    selectOrdem.addEventListener('change', onOrdemChange);
}

// Quando seleciona ordem, carrega datas dessa ordem
function onOrdemChange(e) {
    const cliente = document.getElementById('inputCliente').value;
    const ordem = e.target.value;

    const selectData = document.getElementById('inputDataEntrega');
    const inputMaquina = document.getElementById('inputMaquinaPedido');
    const selectProduto = document.getElementById('inputProduto');

    if (!ordem) {
        selectData.innerHTML = '<option value="">Selecione ordem primeiro</option>';
        selectData.disabled = true;
        inputMaquina.value = '';
        selectProduto.innerHTML = '<option value="">Selecione pedido completo primeiro</option>';
        selectProduto.disabled = true;
        return;
    }

    // Filtra pedidos do cliente e ordem
    const pedidosFiltrados = pedidosCadastradosGlobal.filter(
        p => p.CLIENTE === cliente && p['ORDEM DE COMPRA'] === ordem
    );

    // Datas únicas
    const datas = [...new Set(pedidosFiltrados.map(p => p['DATA DE ENTREGA']))].filter(d => d);

    selectData.innerHTML = '<option value="">Selecione...</option>';
    datas.forEach(data => {
        selectData.innerHTML += `<option value="${data}">${data}</option>`;
    });
    selectData.disabled = false;

    // Reseta máquina e produto
    inputMaquina.value = '';
    selectProduto.innerHTML = '<option value="">Selecione pedido completo primeiro</option>';
    selectProduto.disabled = true;

    // Event listener para data (remove anteriores)
    selectData.removeEventListener('change', onDataChange);
    selectData.addEventListener('change', onDataChange);
}

// Quando seleciona data, preenche máquina e carrega produtos
async function onDataChange(e) {
    const cliente = document.getElementById('inputCliente').value;
    const ordem = document.getElementById('inputOrdem').value;
    const dataEntrega = e.target.value;

    const inputMaquina = document.getElementById('inputMaquinaPedido');
    const selectProduto = document.getElementById('inputProduto');

    if (!dataEntrega) {
        inputMaquina.value = '';
        selectProduto.innerHTML = '<option value="">Selecione pedido completo primeiro</option>';
        selectProduto.disabled = true;
        return;
    }

    // Encontra o pedido específico
    const pedido = pedidosCadastradosGlobal.find(
        p => p.CLIENTE === cliente &&
             p['ORDEM DE COMPRA'] === ordem &&
             p['DATA DE ENTREGA'] === dataEntrega
    );

    if (!pedido) {
        alert('Pedido não encontrado');
        return;
    }

    // Preenche máquina
    const maquina = pedido.MAQUINAS;
    inputMaquina.value = maquina;

    // Carrega produtos da máquina (usando REFERÊNCIAS/MÁQUINA)
    try {
        const response = await fetch(API_URL + '/produtos/' + encodeURIComponent(maquina));
        const data = await response.json();

        selectProduto.innerHTML = '<option value="">Selecione...</option>';

        data.produtos.forEach(prod => {
            // Usa REFERÊNCIAS/MÁQUINA como referência principal
            const refMaquina = prod['REFERÊNCIAS/MÁQUINA'] || prod['REFERENCIA'] || '';
            if (refMaquina) {
                selectProduto.innerHTML += `<option value="${refMaquina}">${refMaquina}</option>`;
            }
        });

        selectProduto.disabled = false;
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
        alert('Erro ao carregar produtos da máquina');
    }
}

// ========================================
// PRODUTOS
// ========================================

async function loadProdutos(maquina) {
    try {
        const response = await fetch(API_URL + '/produtos/' + encodeURIComponent(maquina));
        const data = await response.json();

        const select = document.getElementById('inputProduto');
        select.innerHTML = '<option value="">Selecione...</option>';

        data.produtos.forEach(prod => {
            const refMaquina = prod['REFERÊNCIAS/MÁQUINA'] || prod['REFERENCIA'] || '';
            if (refMaquina) {
                select.innerHTML += '<option value="' + refMaquina + '">' + refMaquina + '</option>';
            }
        });

    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
    }
}

async function loadProdutosCadastrados(maquina) {
    try {
        const response = await fetch(API_URL + '/produtos/' + encodeURIComponent(maquina));
        const data = await response.json();

        const container = document.getElementById('listaProdutos');

        if (data.produtos.length === 0) {
            container.innerHTML = '<p class="info-text">Nenhum produto cadastrado</p>';
            return;
        }

        let html = '<table><thead><tr><th>Referência/Máquina</th><th>Tempo Prod</th><th>Tempo Mont</th><th>Cor</th></tr></thead><tbody>';

        data.produtos.forEach(prod => {
            const refMaquina = prod['REFERÊNCIAS/MÁQUINA'] || prod['REFERENCIA'] || '-';
            html += '<tr>';
            html += '<td><strong>' + refMaquina + '</strong></td>';
            html += '<td>' + (prod['TEMPO DE PRODUÇÃO'] || 0) + 'min</td>';
            html += '<td>' + (prod['TEMPO DE MONTAGEM'] || 0) + 'min</td>';
            html += '<td><div style="width: 30px; height: 30px; background: ' + (prod.COR || '#ccc') + '; border-radius: 5px;"></div></td>';
            html += '</tr>';
        });

        html += '</tbody></table>';
        container.innerHTML = html;

    } catch (error) {
        console.error('Erro ao carregar produtos cadastrados:', error);
    }
}

// ========================================
// FORMULÁRIOS
// ========================================

function setupForms() {
    // Form cadastro produto
    document.getElementById('formCadastro').addEventListener('submit', async (e) => {
        e.preventDefault();

        const produto = {
            maquina: document.getElementById('inputMaquina').value,
            referenciaMaquina: document.getElementById('inputReferencia').value,
            referencia: document.getElementById('inputReferencia').value,
            tempoProducao: parseFloat(document.getElementById('inputTempoProducao').value),
            tempoMontagem: parseFloat(document.getElementById('inputTempoMontagem').value),
            voltasEspula: 0,
            producaoPorMinuto: 0,
            cor: document.getElementById('inputCor').value,
            largura: 0,
            montagem2x2: document.getElementById('inputMontagem2x2').value,
            tempoMontagem2x2: 0
        };

        try {
            const response = await fetch(API_URL + '/produtos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(produto)
            });

            const data = await response.json();

            if (data.success) {
                alert('✅ Produto cadastrado com sucesso!');
                e.target.reset();
                loadProdutosCadastrados(produto.maquina);
            }
        } catch (error) {
            alert('❌ Erro ao cadastrar produto');
            console.error(error);
        }
    });

    // Form pedido
    document.getElementById('formPedido').addEventListener('submit', (e) => {
        e.preventDefault();
        adicionarPedido();
    });
}

// ========================================
// PEDIDOS
// ========================================

async function adicionarPedido() {
    const maquina = document.getElementById('inputMaquinaPedido').value;
    const produtoRef = document.getElementById('inputProduto').value;

    if (!maquina) {
        alert('Por favor, selecione um pedido completo (cliente, ordem e data)');
        return;
    }

    if (!produtoRef) {
        alert('Por favor, selecione um produto');
        return;
    }

    // Busca dados completos do produto usando REFERÊNCIAS/MÁQUINA
    try {
        const response = await fetch(API_URL + '/produtos/' + encodeURIComponent(maquina));
        const data = await response.json();

        // Busca pelo produto usando REFERÊNCIAS/MÁQUINA
        const produtoInfo = data.produtos.find(p =>
            (p['REFERÊNCIAS/MÁQUINA'] === produtoRef) || (p['REFERENCIA'] === produtoRef)
        );

        if (!produtoInfo) {
            alert('Produto não encontrado na máquina');
            return;
        }

        const pedido = {
            cliente: document.getElementById('inputCliente').value,
            ordem_compra: document.getElementById('inputOrdem').value,
            data_entrega: document.getElementById('inputDataEntrega').value,
            maquina: maquina,
            bocas: parseInt(document.getElementById('inputBocas').value),
            produto: produtoRef,
            quantidade: parseInt(document.getElementById('inputQuantidade').value),
            tempo_producao: parseFloat(produtoInfo['TEMPO DE PRODUÇÃO'] || 0),
            tempo_montagem: parseFloat(produtoInfo['TEMPO DE MONTAGEM'] || 0),
            montagem_2x2: produtoInfo['MONTAGEM 2X2'] === 'Sim',
            tempo_montagem_2x2: parseFloat(produtoInfo['TEMPO MONTAGEM 2X2'] || 0)
        };

        pedidosTemporarios.push(pedido);

        atualizarListaPedidos();
        atualizarStatsOtimizacao();

        // Reseta form mas mantém carregado loadPedidosCadastrados
        document.getElementById('inputCliente').value = '';
        document.getElementById('inputOrdem').innerHTML = '<option value="">Selecione cliente primeiro</option>';
        document.getElementById('inputOrdem').disabled = true;
        document.getElementById('inputDataEntrega').innerHTML = '<option value="">Selecione ordem primeiro</option>';
        document.getElementById('inputDataEntrega').disabled = true;
        document.getElementById('inputMaquinaPedido').value = '';
        document.getElementById('inputProduto').innerHTML = '<option value="">Selecione pedido completo primeiro</option>';
        document.getElementById('inputProduto').disabled = true;
        document.getElementById('inputBocas').value = 1;
        document.getElementById('inputQuantidade').value = 1;

        alert('✅ Pedido adicionado! Total: ' + pedidosTemporarios.length);
    } catch (error) {
        console.error('Erro ao adicionar pedido:', error);
        alert('Erro ao adicionar pedido');
    }
}

function atualizarListaPedidos() {
    const container = document.getElementById('listaPedidos');

    if (pedidosTemporarios.length === 0) {
        container.innerHTML = '<p class="info-text">Nenhum pedido adicionado</p>';
        return;
    }

    let html = '<table><thead><tr><th>Cliente</th><th>Produto</th><th>Máquina</th><th>Qtd</th><th>Entrega</th></tr></thead><tbody>';

    pedidosTemporarios.forEach(p => {
        html += '<tr>';
        html += '<td><strong>' + p.cliente + '</strong></td>';
        html += '<td>' + p.produto + '</td>';
        html += '<td>' + p.maquina + '</td>';
        html += '<td>' + p.quantidade + '</td>';
        html += '<td>' + p.data_entrega + '</td>';
        html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

function limparPedidos() {
    if (confirm('Deseja limpar todos os pedidos?')) {
        pedidosTemporarios = [];
        atualizarListaPedidos();
        atualizarStatsOtimizacao();
    }
}

// ========================================
// PLANEJAMENTO
// ========================================

async function gerarPlanejamento() {
    if (pedidosTemporarios.length === 0) {
        alert('❌ Adicione pedidos primeiro!');
        return;
    }

    try {
        const response = await fetch(API_URL + '/planejamento/gerar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pedidos: pedidosTemporarios })
        });

        const data = await response.json();

        if (data.success) {
            sequenciaGerada = data.sequencia;
            mostrarPlanejamento(data);
            showPage('planejamento');
            alert('✅ Planejamento gerado com sucesso!');
        }
    } catch (error) {
        alert('❌ Erro ao gerar planejamento');
        console.error(error);
    }
}

function mostrarPlanejamento(data) {
    const container = document.getElementById('resultadoPlanejamento');

    let html = '<div class="card"><h3>📊 Sequência de Produção</h3>';
    html += '<table><thead><tr><th>#</th><th>Cliente</th><th>Produto</th><th>Máquina</th><th>Qtd</th><th>Tempo</th><th>Entrega</th></tr></thead><tbody>';

    data.sequencia.forEach(item => {
        const urgenciaClass = item.dias_para_entrega <= 7 ? 'badge-critico' :
                              item.dias_para_entrega <= 15 ? 'badge-atencao' : 'badge-ok';

        html += '<tr>';
        html += '<td><strong>' + item.ordem + '</strong></td>';
        html += '<td>' + item.cliente + '</td>';
        html += '<td>' + item.produto + '</td>';
        html += '<td>' + item.maquina + '</td>';
        html += '<td>' + item.quantidade + '</td>';
        html += '<td>' + (item.tempo_total / 60).toFixed(1) + 'h</td>';
        html += '<td><span class="badge ' + urgenciaClass + '">' + item.dias_para_entrega + ' dias</span></td>';
        html += '</tr>';
    });

    html += '</tbody></table></div>';

    // Stats
    html += '<div class="stats-grid">';
    html += '<div class="stat-card"><div class="stat-value">' + data.stats.total_pedidos + '</div><div class="stat-label">Pedidos</div></div>';
    html += '<div class="stat-card"><div class="stat-value">' + data.stats.total_pecas + '</div><div class="stat-label">Peças</div></div>';
    html += '<div class="stat-card"><div class="stat-value">' + data.stats.tempo_total_horas.toFixed(1) + 'h</div><div class="stat-label">Tempo Total</div></div>';
    html += '</div>';

    container.innerHTML = html;
}

// ========================================
// OTIMIZAÇÃO (PRINCIPAL!)
// ========================================

function atualizarStatsOtimizacao() {
    document.getElementById('statPedidos').textContent = pedidosTemporarios.length;

    const totalPecas = pedidosTemporarios.reduce((sum, p) => sum + p.quantidade, 0);
    document.getElementById('statPecas').textContent = totalPecas;

    const maquinasUnicas = new Set(pedidosTemporarios.map(p => p.maquina));
    document.getElementById('statMaquinas').textContent = maquinasUnicas.size;
}

async function otimizarDistribuicao() {
    if (pedidosTemporarios.length === 0) {
        alert('❌ Adicione pedidos primeiro!');
        return;
    }

    const container = document.getElementById('resultadoOtimizacao');
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p>🧠 Analisando e otimizando...</p></div>';

    try {
        const response = await fetch(API_URL + '/otimizacao/analisar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pedidos: pedidosTemporarios })
        });

        const resultado = await response.json();

        if (resultado.sucesso) {
            mostrarResultadoOtimizacao(resultado);
        } else {
            container.innerHTML = '<p class="info-text">❌ Erro na otimização</p>';
        }
    } catch (error) {
        console.error('Erro na otimização:', error);
        container.innerHTML = '<p class="info-text">❌ Erro ao otimizar</p>';
    }
}

function mostrarResultadoOtimizacao(resultado) {
    const container = document.getElementById('resultadoOtimizacao');

    let html = '<div class="card"><h3>📈 RESULTADO DA OTIMIZAÇÃO</h3>';

    // Métricas
    html += '<div class="stats-grid">';
    html += '<div class="stat-card"><div class="stat-value">' + resultado.metricas.tempo_total_horas.toFixed(1) + 'h</div><div class="stat-label">Tempo Total</div></div>';
    html += '<div class="stat-card"><div class="stat-value">' + resultado.metricas.pedidos_criticos + '</div><div class="stat-label">🔴 Críticos</div></div>';
    html += '<div class="stat-card"><div class="stat-value">' + resultado.metricas.pedidos_atenção + '</div><div class="stat-label">🟡 Atenção</div></div>';
    html += '<div class="stat-card"><div class="stat-value">' + resultado.metricas.eficiencia_geral + '%</div><div class="stat-label">Eficiência</div></div>';
    html += '</div>';

    // Alertas
    if (resultado.alertas && resultado.alertas.length > 0) {
        html += '<div class="card" style="background: #fee2e2;"><h4>⚠️ ALERTAS</h4>';
        resultado.alertas.forEach(alerta => {
            const emoji = alerta.tipo === 'critico' ? '🔴' : '⚠️';
            html += '<p>' + emoji + ' ' + alerta.mensagem + '</p>';
        });
        html += '</div>';
    }

    // Distribuição por máquina
    html += '<h3 style="margin-top: 2rem;">🎯 DISTRIBUIÇÃO OTIMIZADA</h3>';

    for (const [maquina, distribuicao] of Object.entries(resultado.sugestoes)) {
        html += '<div class="card">';
        html += '<h4>🔧 ' + maquina + ' (' + distribuicao.length + ' pedidos)</h4>';

        distribuicao.forEach(item => {
            const badgeClass = item.nivel_urgencia === 'CRÍTICO' ? 'badge-critico' :
                               item.nivel_urgencia === 'ATENÇÃO' ? 'badge-atencao' : 'badge-ok';

            html += '<div style="background: white; padding: 1rem; margin: 1rem 0; border-left: 5px solid ' + item.cor + '; border-radius: 10px;">';
            html += '<strong>[' + item.ordem + '] ' + item.cliente + ' - ' + item.produto + '</strong>';
            html += '<span class="badge ' + badgeClass + '">' + item.nivel_urgencia + '</span>';
            html += '<br><br>';
            html += '📦 Qtd: ' + item.quantidade + ' | ';
            html += '⏱️ Tempo: ' + item.tempo_total_horas.toFixed(1) + 'h | ';
            html += '📅 Entrega: ' + item.data_entrega;
            html += '<br>';
            html += '<small>Distribuição: ' + item.bocas_distribuicao.length + ' bocas</small>';
            html += '</div>';
        });

        html += '</div>';
    }

    html += '</div>';

    container.innerHTML = html;
}

// ========================================
// CALENDÁRIO DE TRABALHO
// ========================================

// Carrega resumo do calendário
async function carregarResumoCalendario() {
    try {
        const response = await fetch(API_URL + '/calendario/summary');
        const data = await response.json();

        // Atualiza stats
        document.getElementById('totalHolidays').textContent = data.total_holidays || 0;
        document.getElementById('workSaturday').textContent = data.weekend_config.work_saturday_by_default ? 'Sim' : 'Não';
        document.getElementById('workSunday').textContent = data.weekend_config.work_sunday_by_default ? 'Sim' : 'Não';

        // Atualiza checkboxes
        document.getElementById('checkWorkSaturday').checked = data.weekend_config.work_saturday_by_default;
        document.getElementById('checkWorkSunday').checked = data.weekend_config.work_sunday_by_default;

        // Atualiza lista de feriados
        await carregarListaFeriados();
    } catch (error) {
        console.error('Erro ao carregar resumo:', error);
        alert('Erro ao carregar resumo do calendário');
    }
}

// Salva configuração de fins de semana
async function salvarConfiguracaoFimDeSemana() {
    const workSaturday = document.getElementById('checkWorkSaturday').checked;
    const workSunday = document.getElementById('checkWorkSunday').checked;

    try {
        const response = await fetch(API_URL + '/calendario/fins-de-semana/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                work_saturday: workSaturday,
                work_sunday: workSunday
            })
        });

        const result = await response.json();
        if (result.success) {
            alert('✅ Configuração salva com sucesso!');
            carregarResumoCalendario();
        }
    } catch (error) {
        console.error('Erro ao salvar configuração:', error);
        alert('Erro ao salvar configuração');
    }
}

// Adiciona feriados
async function adicionarFeriados() {
    const input = document.getElementById('inputFeriados');
    const text = input.value.trim();

    if (!text) {
        alert('Digite as datas dos feriados');
        return;
    }

    // Separa por linhas
    const dates = text.split('\n')
        .map(d => d.trim())
        .filter(d => d);

    try {
        const response = await fetch(API_URL + '/calendario/feriados', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dates })
        });

        const result = await response.json();

        let message = `✅ ${result.added.length} feriado(s) adicionado(s)`;
        if (result.invalid.length > 0) {
            message += `\n⚠️ ${result.invalid.length} data(s) inválida(s): ${result.invalid.join(', ')}`;
        }

        alert(message);
        input.value = '';
        carregarResumoCalendario();
    } catch (error) {
        console.error('Erro ao adicionar feriados:', error);
        alert('Erro ao adicionar feriados');
    }
}

// Carrega lista de feriados
async function carregarListaFeriados() {
    try {
        const response = await fetch(API_URL + '/calendario/feriados');
        const data = await response.json();

        const container = document.getElementById('listaFeriados');

        if (!data.holidays || data.holidays.length === 0) {
            container.innerHTML = '<p class="info-text">Nenhum feriado cadastrado</p>';
            return;
        }

        let html = '<div class="holiday-list">';
        data.holidays.forEach(date => {
            html += `
                <div class="holiday-item">
                    <span class="holiday-date">${date}</span>
                    <button class="holiday-remove" onclick="removerFeriado('${date}')">Remover</button>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;
    } catch (error) {
        console.error('Erro ao carregar feriados:', error);
    }
}

// Remove feriado
async function removerFeriado(date) {
    if (!confirm(`Deseja remover o feriado ${date}?`)) return;

    try {
        const response = await fetch(API_URL + '/calendario/feriados', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dates: [date] })
        });

        const result = await response.json();
        if (result.success) {
            alert('✅ Feriado removido!');
            carregarResumoCalendario();
        }
    } catch (error) {
        console.error('Erro ao remover feriado:', error);
        alert('Erro ao remover feriado');
    }
}

// Carrega fins de semana de um ano
async function carregarFinsDeSemana() {
    const year = parseInt(document.getElementById('inputAno').value);

    try {
        const response = await fetch(API_URL + `/calendario/fins-de-semana/${year}`);
        const data = await response.json();

        const container = document.getElementById('finsDeSemanaContainer');

        let html = '<div class="weekend-grid">';

        // Sábados
        html += '<div class="weekend-column">';
        html += `<h4>Sábados de ${year}</h4>`;
        html += '<div class="weekend-items">';
        data.saturdays.forEach(item => {
            html += `
                <div class="weekend-item">
                    <input type="checkbox" id="sat_${item.date.replace(/\//g, '_')}"
                           ${item.working ? 'checked' : ''}>
                    <label for="sat_${item.date.replace(/\//g, '_')}">${item.date}</label>
                </div>
            `;
        });
        html += '</div></div>';

        // Domingos
        html += '<div class="weekend-column">';
        html += `<h4>Domingos de ${year}</h4>`;
        html += '<div class="weekend-items">';
        data.sundays.forEach(item => {
            html += `
                <div class="weekend-item">
                    <input type="checkbox" id="sun_${item.date.replace(/\//g, '_')}"
                           ${item.working ? 'checked' : ''}>
                    <label for="sun_${item.date.replace(/\//g, '_')}">${item.date}</label>
                </div>
            `;
        });
        html += '</div></div>';

        html += '</div>';

        container.innerHTML = html;
        document.getElementById('btnSalvarFinsDeSemana').style.display = 'block';

        // Guarda os dados para salvar depois
        window.weekendData = data;
    } catch (error) {
        console.error('Erro ao carregar fins de semana:', error);
        alert('Erro ao carregar fins de semana');
    }
}

// Salva seleção de fins de semana
async function salvarFinsDeSemana() {
    if (!window.weekendData) return;

    const saturdays = [];
    const sundays = [];

    // Coleta sábados selecionados
    window.weekendData.saturdays.forEach(item => {
        const checkbox = document.getElementById(`sat_${item.date.replace(/\//g, '_')}`);
        if (checkbox && checkbox.checked) {
            saturdays.push(item.date);
        }
    });

    // Coleta domingos selecionados
    window.weekendData.sundays.forEach(item => {
        const checkbox = document.getElementById(`sun_${item.date.replace(/\//g, '_')}`);
        if (checkbox && checkbox.checked) {
            sundays.push(item.date);
        }
    });

    try {
        const response = await fetch(API_URL + '/calendario/fins-de-semana/datas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ saturdays, sundays })
        });

        const result = await response.json();
        if (result.success) {
            alert('✅ Seleção salva com sucesso!');
        }
    } catch (error) {
        console.error('Erro ao salvar fins de semana:', error);
        alert('Erro ao salvar seleção');
    }
}

// Limpa calendário
async function limparCalendario() {
    if (!confirm('Deseja limpar TODAS as configurações do calendário?')) return;

    try {
        const response = await fetch(API_URL + '/calendario/limpar', {
            method: 'POST'
        });

        const result = await response.json();
        if (result.success) {
            alert('✅ Calendário limpo!');
            carregarResumoCalendario();
            document.getElementById('finsDeSemanaContainer').innerHTML = '';
            document.getElementById('btnSalvarFinsDeSemana').style.display = 'none';
        }
    } catch (error) {
        console.error('Erro ao limpar calendário:', error);
        alert('Erro ao limpar calendário');
    }
}

// ========================================
// PLANEJAMENTO DINÂMICO
// ========================================

let planejamentoAtual = null;

// Gera planejamento dinâmico
async function gerarPlanejamentoDinamico() {
    if (pedidosTemporarios.length === 0) {
        alert('Adicione pedidos primeiro!');
        return;
    }

    const dataInicio = document.getElementById('inputDataInicioPlan').value || null;

    // Prepara pedidos com IDs únicos
    const orders = pedidosTemporarios.map((p, idx) => ({
        id: `order_${Date.now()}_${idx}`,
        cliente: p.cliente,
        ordem_compra: p.ordem_compra,
        data_entrega: p.data_entrega,
        maquina: p.maquina,
        bocas: p.bocas,
        produto: p.produto,
        quantidade: p.quantidade,
        tempo_producao: p.tempo_producao || 0,
        tempo_montagem: p.tempo_montagem || 0,
        montagem_2x2: p.montagem_2x2 || false,
        tempo_montagem_2x2: p.tempo_montagem_2x2 || 0
    }));

    try {
        const response = await fetch(API_URL + '/planejamento/dinamico/criar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                orders: orders,
                start_date: dataInicio
            })
        });

        const plan = await response.json();

        if (plan.success) {
            planejamentoAtual = plan;
            mostrarPlanejamentoDinamico(plan);
            alert('✅ Planejamento gerado com sucesso!');
        } else {
            alert('Erro ao gerar planejamento: ' + (plan.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro ao gerar planejamento:', error);
        alert('Erro ao gerar planejamento');
    }
}

// Mostra planejamento dinâmico
function mostrarPlanejamentoDinamico(plan) {
    // Mostra botões
    document.getElementById('btnSalvarPlano').style.display = 'inline-block';
    document.getElementById('btnCarregarPlano').style.display = 'inline-block';

    // Mostra card de resumo
    document.getElementById('cardResumoPlano').style.display = 'block';

    // Atualiza stats
    document.getElementById('statTotalPedidos').textContent = plan.summary.total_orders;
    document.getElementById('statTotalHoras').textContent = plan.summary.total_hours.toFixed(1) + 'h';
    document.getElementById('statCriticos').textContent = plan.summary.critical_orders;
    document.getElementById('statAtenção').textContent = plan.summary.warning_orders;

    // Mostra alertas
    mostrarAlertas(plan.alerts);

    // Mostra planejamento por máquina
    mostrarPlanejamentoPorMaquina(plan.machine_plans);

    // Esconde mensagem de info
    document.getElementById('resultadoPlanejamento').innerHTML = '';
}

// Mostra alertas
function mostrarAlertas(alerts) {
    const container = document.getElementById('alertasPlano');

    if (!alerts || alerts.length === 0) {
        container.innerHTML = '';
        return;
    }

    let html = '<div class="card"><h3>⚠️ Alertas</h3><div class="alerts-container">';

    alerts.forEach(alert => {
        const alertClass = alert.tipo === 'CRITICO' ? 'critical' : 'warning';
        const icon = alert.tipo === 'CRITICO' ? '🔴' : '⚠️';

        html += `
            <div class="alert ${alertClass}">
                <div class="alert-icon">${icon}</div>
                <div class="alert-content">
                    <div class="alert-title">${alert.cliente} - ${alert.produto}</div>
                    <div class="alert-message">${alert.mensagem}</div>
                    <div class="alert-message"><small>Entrega: ${alert.data_entrega} | Término: ${alert.data_fim}</small></div>
                </div>
            </div>
        `;
    });

    html += '</div></div>';
    container.innerHTML = html;
}

// Mostra planejamento por máquina
function mostrarPlanejamentoPorMaquina(machinePlans) {
    const container = document.getElementById('planejamentoPorMaquina');

    let html = '';

    for (const [machine, plan] of Object.entries(machinePlans)) {
        html += `
            <div class="card machine-plan">
                <div class="machine-header">
                    <div class="machine-name">🔧 ${plan.maquina}</div>
                    <div class="machine-availability">
                        ${plan.availability_hours}h/dia | ${plan.total_orders} pedidos | ${plan.total_hours.toFixed(1)}h total
                    </div>
                </div>
                <div class="orders-timeline" id="timeline_${machine.replace(/\s+/g, '_')}">
                    ${renderOrdersList(plan.orders, machine)}
                </div>
            </div>
        `;
    }

    container.innerHTML = html;

    // Adiciona drag and drop
    setupDragAndDrop();
}

// Renderiza lista de pedidos
function renderOrdersList(orders, machine) {
    if (!orders || orders.length === 0) {
        return '<div class="empty-state"><div class="empty-state-icon">📭</div><div class="empty-state-text">Nenhum pedido para esta máquina</div></div>';
    }

    let html = '';

    orders.forEach((order, index) => {
        // Determina badge
        let badgeClass = 'ok';
        let badgeText = 'OK';

        if (order.data_fim && order.data_entrega) {
            try {
                const [dF, mF, yF] = order.data_fim.split('/');
                const [dE, mE, yE] = order.data_entrega.split('/');
                const dataFim = new Date(yF, mF - 1, dF);
                const dataEntrega = new Date(yE, mE - 1, dE);

                if (dataFim > dataEntrega) {
                    badgeClass = 'critical';
                    badgeText = 'ATRASADO';
                } else {
                    const diff = Math.floor((dataEntrega - dataFim) / (1000 * 60 * 60 * 24));
                    if (diff <= 3) {
                        badgeClass = 'warning';
                        badgeText = 'ATENÇÃO';
                    }
                }
            } catch (e) {
                console.error('Erro ao comparar datas:', e);
            }
        }

        html += `
            <div class="order-item" draggable="true"
                 data-order-id="${order.id}"
                 data-machine="${machine}"
                 data-position="${index}">
                <div class="drag-handle"></div>
                <div class="order-header">
                    <div class="order-info">
                        <div class="order-title">${order.cliente} - ${order.produto}</div>
                        <div class="order-subtitle">OC: ${order.ordem_compra} | ${order.quantidade} peças | ${order.bocas} bocas</div>
                    </div>
                    <div class="order-badge ${badgeClass}">${badgeText}</div>
                </div>
                <div class="order-details">
                    <div class="order-detail">
                        <div class="detail-label">Início</div>
                        <div class="detail-value highlight">${order.data_inicio || 'N/A'}</div>
                    </div>
                    <div class="order-detail">
                        <div class="detail-label">Término</div>
                        <div class="detail-value highlight">${order.data_fim || 'N/A'}</div>
                    </div>
                    <div class="order-detail">
                        <div class="detail-label">Entrega</div>
                        <div class="detail-value">${order.data_entrega}</div>
                    </div>
                    <div class="order-detail">
                        <div class="detail-label">Dias Úteis</div>
                        <div class="detail-value">${order.dias_uteis || 0}</div>
                    </div>
                    <div class="order-detail">
                        <div class="detail-label">Horas Total</div>
                        <div class="detail-value">${order.tempo_total_horas.toFixed(1)}h</div>
                    </div>
                </div>
            </div>
        `;
    });

    return html;
}

// Configura drag and drop
function setupDragAndDrop() {
    const orderItems = document.querySelectorAll('.order-item');

    orderItems.forEach(item => {
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragend', handleDragEnd);
        item.addEventListener('dragover', handleDragOver);
        item.addEventListener('drop', handleDrop);
        item.addEventListener('dragenter', handleDragEnter);
        item.addEventListener('dragleave', handleDragLeave);
    });
}

let draggedElement = null;

function handleDragStart(e) {
    draggedElement = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    document.querySelectorAll('.order-item').forEach(item => {
        item.classList.remove('drag-over');
    });
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    if (this !== draggedElement) {
        this.classList.add('drag-over');
    }
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

async function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }

    this.classList.remove('drag-over');

    if (draggedElement !== this) {
        const fromMachine = draggedElement.dataset.machine;
        const toMachine = this.dataset.machine;

        // Só permite reordenar na mesma máquina
        if (fromMachine !== toMachine) {
            alert('Só é possível reordenar pedidos da mesma máquina');
            return false;
        }

        const fromPosition = parseInt(draggedElement.dataset.position);
        const toPosition = parseInt(this.dataset.position);
        const orderId = draggedElement.dataset.orderId;

        // Recalcula planejamento
        await reordenarPedido(orderId, fromPosition, toPosition, fromMachine);
    }

    return false;
}

// Reordena pedido e recalcula
async function reordenarPedido(orderId, fromPosition, toPosition, machine) {
    if (!planejamentoAtual) return;

    try {
        const response = await fetch(API_URL + '/planejamento/dinamico/mover', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                order_id: orderId,
                from_position: fromPosition,
                to_position: toPosition,
                machine: machine,
                all_orders: planejamentoAtual.all_orders,
                start_date: planejamentoAtual.start_date
            })
        });

        const newPlan = await response.json();

        if (newPlan.success) {
            planejamentoAtual = newPlan;
            mostrarPlanejamentoDinamico(newPlan);
        }
    } catch (error) {
        console.error('Erro ao reordenar:', error);
        alert('Erro ao reordenar pedido');
    }
}

// Salva plano
async function salvarPlano() {
    if (!planejamentoAtual) {
        alert('Nenhum plano para salvar');
        return;
    }

    const planName = prompt('Nome do plano:');
    if (!planName) return;

    try {
        const response = await fetch(API_URL + '/planejamento/dinamico/salvar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                plan_name: planName,
                plan: planejamentoAtual
            })
        });

        const result = await response.json();
        if (result.success) {
            alert('✅ Plano salvo com sucesso!');
        }
    } catch (error) {
        console.error('Erro ao salvar plano:', error);
        alert('Erro ao salvar plano');
    }
}

// Carrega plano
async function carregarPlano() {
    try {
        // Lista planos salvos
        const response = await fetch(API_URL + '/planejamento/dinamico/listar');
        const data = await response.json();

        if (!data.plans || data.plans.length === 0) {
            alert('Nenhum plano salvo');
            return;
        }

        // Mostra opções
        let options = 'Selecione um plano:\n\n';
        data.plans.forEach((p, idx) => {
            options += `${idx + 1}. ${p.name} (${p.total_orders} pedidos, ${p.total_hours}h)\n`;
        });

        const choice = prompt(options + '\nDigite o número do plano:');
        if (!choice) return;

        const index = parseInt(choice) - 1;
        if (index < 0 || index >= data.plans.length) {
            alert('Opção inválida');
            return;
        }

        const planName = data.plans[index].name;

        // Carrega o plano
        const loadResponse = await fetch(API_URL + `/planejamento/dinamico/carregar/${planName}`);
        const plan = await loadResponse.json();

        planejamentoAtual = plan;
        mostrarPlanejamentoDinamico(plan);
        alert('✅ Plano carregado!');
    } catch (error) {
        console.error('Erro ao carregar plano:', error);
        alert('Erro ao carregar plano');
    }
}

// ========================================
// OTIMIZAÇÃO DE MÁQUINAS
// ========================================

let sugestoesAtivas = null;

// Otimiza distribuição de máquinas
async function otimizarMaquinas() {
    if (pedidosTemporarios.length === 0) {
        alert('Adicione pedidos primeiro!');
        return;
    }

    try {
        const response = await fetch(API_URL + '/otimizacao/sugerir-maquinas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                orders: pedidosTemporarios,
                start_date: null
            })
        });

        const result = await response.json();

        if (result.success) {
            sugestoesAtivas = result;
            mostrarSugestoes(result);
        } else {
            alert('Erro ao otimizar: ' + (result.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro ao otimizar máquinas:', error);
        alert('Erro ao otimizar máquinas');
    }
}

// Mostra sugestões de otimização
function mostrarSugestoes(result) {
    const cardSugestoes = document.getElementById('cardSugestoes');
    const statsContainer = document.getElementById('sugestoesStats');
    const listaContainer = document.getElementById('sugestoesLista');

    // Mostra card
    cardSugestoes.style.display = 'block';

    // Scroll suave até o card
    cardSugestoes.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Estatísticas
    const stats = result.statistics;
    let statsHtml = '<div class="optimization-stats">';
    statsHtml += `
        <div class="opt-stat-card">
            <div class="opt-stat-value">${stats.total_orders}</div>
            <div class="opt-stat-label">Total de Pedidos</div>
        </div>
        <div class="opt-stat-card" style="background: linear-gradient(135deg, var(--danger), #dc2626);">
            <div class="opt-stat-value">${stats.critical_changes}</div>
            <div class="opt-stat-label">Mudanças Críticas</div>
        </div>
        <div class="opt-stat-card" style="background: linear-gradient(135deg, var(--warning), #ea580c);">
            <div class="opt-stat-value">${stats.improvements}</div>
            <div class="opt-stat-label">Melhorias Possíveis</div>
        </div>
        <div class="opt-stat-card" style="background: linear-gradient(135deg, var(--success), #059669);">
            <div class="opt-stat-value">${stats.efficiency_gain}%</div>
            <div class="opt-stat-label">Ganho de Eficiência</div>
        </div>
    `;
    statsHtml += '</div>';
    statsContainer.innerHTML = statsHtml;

    // Lista de sugestões
    let listaHtml = '';

    result.suggestions.forEach((suggestion, index) => {
        const order = suggestion.order;
        const statusClass = suggestion.status;
        const statusText = {
            'critical': 'CRÍTICO',
            'improve': 'MELHORIA',
            'keep': 'MANTER'
        }[statusClass] || 'INFO';

        listaHtml += `
            <div class="suggestion-card ${statusClass}">
                <div class="suggestion-header">
                    <div class="suggestion-title">
                        ${order.cliente} - ${order.produto}
                        <div style="font-size: 0.85rem; font-weight: 400; color: #64748b; margin-top: 0.25rem;">
                            ${order.quantidade} peças | Entrega: ${order.data_entrega}
                        </div>
                    </div>
                    <div class="suggestion-status ${statusClass}">${statusText}</div>
                </div>

                <div class="suggestion-machines">
                    <div class="machine-box">
                        <div class="machine-label">Máquina Atual</div>
                        <div class="machine-name">${suggestion.current_machine || 'Não definida'}</div>
                    </div>
                    <div class="machine-arrow">→</div>
                    <div class="machine-box" style="background: ${suggestion.current_machine === suggestion.suggested_machine ? '#f0fdf4' : '#fffbeb'};">
                        <div class="machine-label">Máquina Sugerida</div>
                        <div class="machine-name">${suggestion.suggested_machine}</div>
                    </div>
                </div>

                <div class="suggestion-reason">
                    <strong>Motivo:</strong> ${suggestion.reason}
                </div>

                ${suggestion.time_improvement && suggestion.time_improvement.has_improvement ? `
                    <div style="margin-top: 0.75rem; padding: 0.5rem; background: #f0fdf4; border-radius: 6px; font-size: 0.9rem;">
                        💡 <strong>Economia de tempo:</strong> ${suggestion.time_improvement.time_saved_hours}h (${suggestion.time_improvement.percentage}%)
                    </div>
                ` : ''}

                ${suggestion.options && suggestion.options.length > 0 ? `
                    <details style="margin-top: 1rem;">
                        <summary style="cursor: pointer; font-weight: 600; color: var(--primary);">
                            Ver todas as opções (${suggestion.options.length})
                        </summary>
                        <div class="suggestion-options">
                            ${suggestion.options.map(opt => `
                                <div class="option-item ${opt.is_current ? 'current' : ''} ${opt.is_suggested ? 'suggested' : ''}">
                                    <div class="option-machine">${opt.maquina}</div>
                                    <div class="option-time">${opt.tempo_total_horas}h ${opt.viavel ? '✅' : '⚠️'}</div>
                                    ${opt.is_current ? '<span class="option-badge current">ATUAL</span>' : ''}
                                    ${opt.is_suggested ? '<span class="option-badge suggested">SUGERIDA</span>' : ''}
                                </div>
                            `).join('')}
                        </div>
                    </details>
                ` : ''}
            </div>
        `;
    });

    listaContainer.innerHTML = listaHtml || '<p class="info-text">Nenhuma sugestão disponível</p>';
}

// Aplica sugestões de otimização
async function aplicarSugestoes() {
    if (!sugestoesAtivas) {
        alert('Nenhuma sugestão para aplicar');
        return;
    }

    if (!confirm(`Deseja aplicar as ${sugestoesAtivas.statistics.total_changes_suggested} mudanças sugeridas?`)) {
        return;
    }

    try {
        const response = await fetch(API_URL + '/otimizacao/aplicar-sugestoes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                orders: pedidosTemporarios,
                suggestions: sugestoesAtivas.suggestions
            })
        });

        const result = await response.json();

        if (result.success) {
            // Atualiza pedidos temporários com otimizações
            pedidosTemporarios = result.optimized_orders;

            // Atualiza lista
            atualizarListaPedidos();

            alert(`✅ ${result.total_changed} pedido(s) otimizado(s) com sucesso!`);

            // Fecha sugestões
            fecharSugestoes();
        }
    } catch (error) {
        console.error('Erro ao aplicar sugestões:', error);
        alert('Erro ao aplicar sugestões');
    }
}

// Fecha card de sugestões
function fecharSugestoes() {
    document.getElementById('cardSugestoes').style.display = 'none';
    sugestoesAtivas = null;
}

// Inicializa calendário quando a página for mostrada
document.addEventListener('DOMContentLoaded', () => {
    // Carrega resumo do calendário ao carregar a página
    setTimeout(() => {
        carregarResumoCalendario();
    }, 1000);
});
