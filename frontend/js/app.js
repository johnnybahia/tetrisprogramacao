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

async function loadMaquinas() {
    try {
        const response = await fetch(API_URL + '/maquinas');
        const data = await response.json();

        const selectCadastro = document.getElementById('inputMaquina');
        const selectPedido = document.getElementById('inputMaquinaPedido');

        selectCadastro.innerHTML = '<option value="">Selecione...</option>';
        selectPedido.innerHTML = '<option value="">Selecione...</option>';

        data.maquinas.forEach(maq => {
            selectCadastro.innerHTML += '<option value="' + maq + '">' + maq + '</option>';
            selectPedido.innerHTML += '<option value="' + maq + '">' + maq + '</option>';
        });

        // Event listener para carregar produtos quando selecionar máquina
        selectPedido.addEventListener('change', (e) => {
            if (e.target.value) {
                loadProdutos(e.target.value);
            }
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
// PRODUTOS
// ========================================

async function loadProdutos(maquina) {
    try {
        const response = await fetch(API_URL + '/produtos/' + encodeURIComponent(maquina));
        const data = await response.json();

        const select = document.getElementById('inputProduto');
        select.innerHTML = '<option value="">Selecione...</option>';

        data.produtos.forEach(prod => {
            select.innerHTML += '<option value="' + prod.REFERENCIA + '">' + prod.REFERENCIA + '</option>';
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

        let html = '<table><thead><tr><th>Referência</th><th>Tempo Prod</th><th>Tempo Mont</th><th>Cor</th></tr></thead><tbody>';

        data.produtos.forEach(prod => {
            html += '<tr>';
            html += '<td><strong>' + prod.REFERENCIA + '</strong></td>';
            html += '<td>' + prod['TEMPO DE PRODUÇÃO'] + 'min</td>';
            html += '<td>' + prod['TEMPO DE MONTAGEM'] + 'min</td>';
            html += '<td><div style="width: 30px; height: 30px; background: ' + prod.COR + '; border-radius: 5px;"></div></td>';
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

function adicionarPedido() {
    const pedido = {
        cliente: document.getElementById('inputCliente').value,
        ordem_compra: document.getElementById('inputOrdem').value,
        data_entrega: document.getElementById('inputDataEntrega').value,
        maquina: document.getElementById('inputMaquinaPedido').value,
        bocas: parseInt(document.getElementById('inputBocas').value),
        produto: document.getElementById('inputProduto').value,
        quantidade: parseInt(document.getElementById('inputQuantidade').value)
    };

    pedidosTemporarios.push(pedido);

    atualizarListaPedidos();
    atualizarStatsOtimizacao();

    document.getElementById('formPedido').reset();

    alert('✅ Pedido adicionado! Total: ' + pedidosTemporarios.length);
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
