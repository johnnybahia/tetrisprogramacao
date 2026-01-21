"""
Módulo de otimização inteligente de distribuição de produção
"""
from typing import List, Dict, Tuple
import pandas as pd
from datetime import datetime, timedelta


class ProductionOptimizer:
    """Otimizador de distribuição de produção nas máquinas"""

    @staticmethod
    def calcular_urgencia(data_entrega_str: str) -> int:
        """
        Calcula score de urgência (0-100)
        Quanto maior o score, mais urgente
        """
        try:
            if '/' in data_entrega_str:
                data_entrega = datetime.strptime(data_entrega_str, '%d/%m/%Y')
            elif '-' in data_entrega_str:
                data_entrega = datetime.strptime(data_entrega_str, '%Y-%m-%d')
            else:
                return 50

            hoje = datetime.now()
            dias_restantes = (data_entrega - hoje).days

            if dias_restantes <= 0:
                return 100  # ATRASADO!
            elif dias_restantes <= 3:
                return 95
            elif dias_restantes <= 7:
                return 85
            elif dias_restantes <= 15:
                return 70
            elif dias_restantes <= 30:
                return 50
            else:
                return 30

        except Exception:
            return 50

    @staticmethod
    def otimizar_distribuicao(
        pedidos: List[Dict],
        produtos_df: pd.DataFrame
    ) -> Dict:
        """
        Algoritmo de otimização de distribuição

        Critérios:
        1. Urgência (prazo de entrega)
        2. Eficiência (minimizar trocas de produto)
        3. Balanceamento (distribuir carga entre bocas)
        4. Viabilidade (verificar se dá tempo)

        Returns:
            Dicionário com sugestão otimizada e análise
        """
        if not pedidos:
            return {
                'sucesso': False,
                'mensagem': 'Nenhum pedido para otimizar'
            }

        # 1. ANÁLISE INICIAL
        analise_inicial = ProductionOptimizer._analisar_pedidos(pedidos, produtos_df)

        # 2. ORDENAÇÃO POR URGÊNCIA
        pedidos_ordenados = sorted(
            pedidos,
            key=lambda x: ProductionOptimizer.calcular_urgencia(x['data_entrega']),
            reverse=True
        )

        # 3. AGRUPAMENTO POR MÁQUINA
        pedidos_por_maquina = {}
        for pedido in pedidos_ordenados:
            maq = pedido['maquina']
            if maq not in pedidos_por_maquina:
                pedidos_por_maquina[maq] = []
            pedidos_por_maquina[maq].append(pedido)

        # 4. OTIMIZAÇÃO POR MÁQUINA
        sugestoes = {}
        alertas = []
        metricas = {
            'tempo_total_horas': 0,
            'pedidos_criticos': 0,
            'pedidos_atenção': 0,
            'pedidos_ok': 0,
            'eficiencia_geral': 0
        }

        for maquina, pedidos_maq in pedidos_por_maquina.items():
            resultado = ProductionOptimizer._otimizar_maquina(
                maquina, pedidos_maq, produtos_df
            )

            sugestoes[maquina] = resultado['distribuicao']
            alertas.extend(resultado['alertas'])

            # Atualiza métricas
            metricas['tempo_total_horas'] += resultado['tempo_total']
            metricas['pedidos_criticos'] += resultado['pedidos_criticos']
            metricas['pedidos_atenção'] += resultado['pedidos_atencao']
            metricas['pedidos_ok'] += resultado['pedidos_ok']

        # 5. CÁLCULO DE EFICIÊNCIA
        total_pedidos = len(pedidos)
        if total_pedidos > 0:
            # Eficiência baseada em pedidos críticos
            eficiencia = 100 - (metricas['pedidos_criticos'] / total_pedidos * 100)
            metricas['eficiencia_geral'] = round(eficiencia, 1)

        return {
            'sucesso': True,
            'sugestoes': sugestoes,
            'alertas': alertas,
            'metricas': metricas,
            'analise_inicial': analise_inicial
        }

    @staticmethod
    def _analisar_pedidos(pedidos: List[Dict], produtos_df: pd.DataFrame) -> Dict:
        """Análise inicial dos pedidos"""
        analise = {
            'total_pedidos': len(pedidos),
            'total_pecas': sum(p['quantidade'] for p in pedidos),
            'maquinas_utilizadas': len(set(p['maquina'] for p in pedidos)),
            'tempo_estimado_total': 0
        }

        return analise

    @staticmethod
    def _otimizar_maquina(
        maquina: str,
        pedidos: List[Dict],
        produtos_df: pd.DataFrame
    ) -> Dict:
        """Otimiza distribuição em uma máquina específica"""

        distribuicao = []
        alertas = []
        tempo_total = 0
        pedidos_criticos = 0
        pedidos_atencao = 0
        pedidos_ok = 0

        # Agrupa pedidos do mesmo produto (eficiência)
        pedidos_agrupados = ProductionOptimizer._agrupar_produtos_similares(pedidos)

        for idx, pedido in enumerate(pedidos_agrupados, 1):
            # Busca informações do produto
            produto_ref = pedido['produto']
            produto_info = produtos_df[produtos_df['REFERENCIA'] == produto_ref]

            if produto_info.empty:
                continue

            prod_dict = produto_info.iloc[0].to_dict()

            # Calcula tempo
            tempo_prod = float(prod_dict.get('TEMPO DE PRODUÇÃO', 0))
            tempo_mont = float(prod_dict.get('TEMPO DE MONTAGEM', 0))

            if prod_dict.get('MONTAGEM 2X2', '').upper() == 'SIM':
                tempo_mont += float(prod_dict.get('TEMPO MONTAGEM 2X2', 0))

            tempo_unitario = tempo_prod + tempo_mont
            tempo_total_pedido = tempo_unitario * pedido['quantidade']
            tempo_total += tempo_total_pedido

            # Calcula distribuição nas bocas
            bocas = pedido['bocas']
            qtd_por_boca = pedido['quantidade'] // bocas
            resto = pedido['quantidade'] % bocas

            bocas_distribuicao = []
            for boca_num in range(1, bocas + 1):
                qtd_boca = qtd_por_boca + (1 if boca_num <= resto else 0)
                tempo_boca = qtd_boca * tempo_unitario

                bocas_distribuicao.append({
                    'boca': boca_num,
                    'quantidade': qtd_boca,
                    'tempo_horas': round(tempo_boca / 60, 2),
                    'tempo_minutos': tempo_boca
                })

            # Análise de urgência
            urgencia = ProductionOptimizer.calcular_urgencia(pedido['data_entrega'])

            if urgencia >= 85:
                nivel_urgencia = 'CRÍTICO'
                pedidos_criticos += 1
                alertas.append({
                    'tipo': 'critico',
                    'cliente': pedido['cliente'],
                    'produto': pedido['produto'],
                    'mensagem': f"Pedido URGENTE! Entrega: {pedido['data_entrega']}"
                })
            elif urgencia >= 70:
                nivel_urgencia = 'ATENÇÃO'
                pedidos_atencao += 1
            else:
                nivel_urgencia = 'OK'
                pedidos_ok += 1

            # Verifica viabilidade
            dias_disponiveis = ProductionOptimizer._calcular_dias_disponiveis(
                pedido['data_entrega']
            )
            horas_disponiveis = dias_disponiveis * 8  # 8h/dia
            horas_necessarias = tempo_total_pedido / 60

            viavel = horas_disponiveis >= horas_necessarias

            if not viavel:
                alertas.append({
                    'tipo': 'inviavel',
                    'cliente': pedido['cliente'],
                    'produto': pedido['produto'],
                    'mensagem': f"ATENÇÃO: Tempo insuficiente! Precisa {horas_necessarias:.1f}h mas tem apenas {horas_disponiveis:.1f}h"
                })

            distribuicao.append({
                'ordem': idx,
                'cliente': pedido['cliente'],
                'produto': pedido['produto'],
                'quantidade': pedido['quantidade'],
                'bocas_distribuicao': bocas_distribuicao,
                'tempo_total_horas': round(tempo_total_pedido / 60, 2),
                'data_entrega': pedido['data_entrega'],
                'urgencia': urgencia,
                'nivel_urgencia': nivel_urgencia,
                'viavel': viavel,
                'cor': prod_dict.get('COR', '#CCCCCC')
            })

        return {
            'distribuicao': distribuicao,
            'alertas': alertas,
            'tempo_total': tempo_total / 60,  # em horas
            'pedidos_criticos': pedidos_criticos,
            'pedidos_atencao': pedidos_atencao,
            'pedidos_ok': pedidos_ok
        }

    @staticmethod
    def _agrupar_produtos_similares(pedidos: List[Dict]) -> List[Dict]:
        """
        Agrupa pedidos do mesmo produto para eficiência
        (minimiza trocas de setup)
        """
        # Por enquanto retorna ordenado por produto
        # No futuro pode implementar lógica mais complexa
        return sorted(pedidos, key=lambda x: x['produto'])

    @staticmethod
    def _calcular_dias_disponiveis(data_entrega_str: str) -> int:
        """Calcula dias úteis disponíveis até a entrega"""
        try:
            if '/' in data_entrega_str:
                data_entrega = datetime.strptime(data_entrega_str, '%d/%m/%Y')
            elif '-' in data_entrega_str:
                data_entrega = datetime.strptime(data_entrega_str, '%Y-%m-%d')
            else:
                return 0

            hoje = datetime.now()
            dias = (data_entrega - hoje).days

            # Considera apenas dias úteis (aproximado: 70% dos dias)
            dias_uteis = int(dias * 0.7)

            return max(0, dias_uteis)

        except Exception:
            return 0

    @staticmethod
    def gerar_relatorio_otimizacao(resultado_otimizacao: Dict) -> str:
        """
        Gera relatório textual da otimização

        Args:
            resultado_otimizacao: Resultado do método otimizar_distribuicao

        Returns:
            String com relatório formatado
        """
        if not resultado_otimizacao.get('sucesso'):
            return "❌ Não foi possível gerar relatório"

        metricas = resultado_otimizacao['metricas']
        alertas = resultado_otimizacao['alertas']

        relatorio = "=" * 60 + "\n"
        relatorio += "📊 RELATÓRIO DE OTIMIZAÇÃO DE PRODUÇÃO\n"
        relatorio += "=" * 60 + "\n\n"

        # Métricas gerais
        relatorio += "🎯 MÉTRICAS GERAIS:\n"
        relatorio += f"   • Tempo Total Estimado: {metricas['tempo_total_horas']:.1f} horas\n"
        relatorio += f"   • Pedidos Críticos: {metricas['pedidos_criticos']}\n"
        relatorio += f"   • Pedidos Atenção: {metricas['pedidos_atenção']}\n"
        relatorio += f"   • Pedidos OK: {metricas['pedidos_ok']}\n"
        relatorio += f"   • Eficiência Geral: {metricas['eficiencia_geral']}%\n\n"

        # Alertas
        if alertas:
            relatorio += "⚠️ ALERTAS IMPORTANTES:\n"
            for alerta in alertas:
                emoji = "🔴" if alerta['tipo'] == 'critico' else "🟡"
                relatorio += f"   {emoji} {alerta['mensagem']}\n"
            relatorio += "\n"

        # Sugestões por máquina
        relatorio += "🔧 DISTRIBUIÇÃO SUGERIDA POR MÁQUINA:\n\n"

        sugestoes = resultado_otimizacao['sugestoes']
        for maquina, distribuicao in sugestoes.items():
            relatorio += f"   {maquina}:\n"
            for item in distribuicao:
                relatorio += f"      [{item['ordem']}] {item['cliente']} - {item['produto']}\n"
                relatorio += f"          Quantidade: {item['quantidade']} | "
                relatorio += f"Tempo: {item['tempo_total_horas']:.1f}h | "
                relatorio += f"Urgência: {item['nivel_urgencia']}\n"
            relatorio += "\n"

        relatorio += "=" * 60 + "\n"

        return relatorio
