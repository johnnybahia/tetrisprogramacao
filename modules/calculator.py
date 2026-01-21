"""
Módulo de cálculos de planejamento e sequenciamento
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd


def formatar_data_br(data) -> str:
    """
    Formata data para padrão brasileiro DD/MM/AAAA

    Args:
        data: String ou objeto datetime

    Returns:
        Data formatada em DD/MM/AAAA
    """
    try:
        if isinstance(data, str):
            # Se já está no formato DD/MM/AAAA
            if '/' in data and len(data.split('/')) == 3:
                partes = data.split('/')
                if len(partes[0]) <= 2:
                    return data

            # Se está no formato YYYY-MM-DD
            if '-' in data:
                data_obj = datetime.strptime(data, '%Y-%m-%d')
                return data_obj.strftime('%d/%m/%Y')

        elif isinstance(data, datetime):
            return data.strftime('%d/%m/%Y')

        return str(data)

    except Exception:
        return str(data)


class ProductionCalculator:
    """Realiza cálculos de planejamento de produção"""

    @staticmethod
    def calcular_tempo_total_produto(produto: Dict) -> float:
        """
        Calcula tempo total de produção de um produto

        Args:
            produto: Dicionário com dados do produto

        Returns:
            Tempo total em minutos
        """
        tempo_producao = float(produto.get('TEMPO DE PRODUÇÃO', 0))
        tempo_montagem = float(produto.get('TEMPO DE MONTAGEM', 0))

        # Verifica se tem montagem 2x2
        if produto.get('MONTAGEM 2X2', '').upper() == 'SIM':
            tempo_montagem_2x2 = float(produto.get('TEMPO MONTAGEM 2X2', 0))
            tempo_montagem += tempo_montagem_2x2

        return tempo_producao + tempo_montagem

    @staticmethod
    def calcular_dias_ate_entrega(data_entrega: str) -> int:
        """
        Calcula quantos dias faltam até a data de entrega

        Args:
            data_entrega: Data de entrega no formato YYYY-MM-DD ou DD/MM/YYYY

        Returns:
            Número de dias até a entrega
        """
        try:
            # Tenta parsear diferentes formatos de data
            if '-' in data_entrega:
                data_obj = datetime.strptime(data_entrega, '%Y-%m-%d')
            elif '/' in data_entrega:
                data_obj = datetime.strptime(data_entrega, '%d/%m/%Y')
            else:
                # Se já é um objeto datetime
                data_obj = data_entrega

            hoje = datetime.now()
            delta = data_obj - hoje

            return delta.days

        except Exception as e:
            return 0

    @staticmethod
    def distribuir_em_bocas(
        quantidade: int,
        num_bocas: int,
        tempo_por_unidade: float
    ) -> List[Dict]:
        """
        Distribui a produção entre as bocas disponíveis

        Args:
            quantidade: Quantidade total a produzir
            num_bocas: Número de bocas disponíveis
            tempo_por_unidade: Tempo em minutos para produzir 1 unidade

        Returns:
            Lista com distribuição por boca
        """
        if num_bocas <= 0:
            return []

        # Distribui igualmente
        qtd_por_boca = quantidade // num_bocas
        resto = quantidade % num_bocas

        distribuicao = []

        for i in range(num_bocas):
            qtd_nesta_boca = qtd_por_boca + (1 if i < resto else 0)
            tempo_total = qtd_nesta_boca * tempo_por_unidade

            distribuicao.append({
                'boca': i + 1,
                'quantidade': qtd_nesta_boca,
                'tempo_minutos': tempo_total,
                'tempo_horas': tempo_total / 60
            })

        return distribuicao

    @staticmethod
    def gerar_sequencia_producao(
        pedidos: List[Dict],
        produtos_info: pd.DataFrame
    ) -> List[Dict]:
        """
        Gera sequência de produção otimizada

        Args:
            pedidos: Lista de pedidos
            produtos_info: DataFrame com informações dos produtos

        Returns:
            Lista ordenada com sequência de produção
        """
        sequencia = []

        for pedido in pedidos:
            # Busca informações do produto
            produto_ref = pedido.get('produto')
            produto_info = produtos_info[
                produtos_info['REFERENCIA'] == produto_ref
            ]

            if produto_info.empty:
                continue

            produto_dict = produto_info.iloc[0].to_dict()

            tempo_total = ProductionCalculator.calcular_tempo_total_produto(produto_dict)
            dias_para_entrega = ProductionCalculator.calcular_dias_ate_entrega(
                pedido.get('data_entrega', '')
            )

            # Calcula prioridade (quanto menor o prazo, maior a prioridade)
            prioridade = 1000 - dias_para_entrega

            sequencia.append({
                'ordem': len(sequencia) + 1,
                'cliente': pedido.get('cliente'),
                'ordem_compra': pedido.get('ordem_compra'),
                'produto': produto_ref,
                'maquina': pedido.get('maquina'),
                'quantidade': pedido.get('quantidade', 0),
                'bocas': pedido.get('bocas', 1),
                'tempo_unitario': tempo_total,
                'tempo_total': tempo_total * pedido.get('quantidade', 0),
                'data_entrega': pedido.get('data_entrega'),
                'dias_para_entrega': dias_para_entrega,
                'prioridade': prioridade,
                'cor': produto_dict.get('COR', '#CCCCCC')
            })

        # Ordena por prioridade (urgência)
        sequencia_ordenada = sorted(sequencia, key=lambda x: x['prioridade'], reverse=True)

        # Reordena o campo 'ordem'
        for i, item in enumerate(sequencia_ordenada):
            item['ordem'] = i + 1

        return sequencia_ordenada

    @staticmethod
    def calcular_ocupacao_maquinas(
        sequencia: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        Calcula ocupação por máquina

        Args:
            sequencia: Sequência de produção

        Returns:
            Dicionário com ocupação por máquina
        """
        ocupacao = {}

        for item in sequencia:
            maquina = item['maquina']

            if maquina not in ocupacao:
                ocupacao[maquina] = []

            # Distribui nas bocas
            distribuicao = ProductionCalculator.distribuir_em_bocas(
                quantidade=item['quantidade'],
                num_bocas=item['bocas'],
                tempo_por_unidade=item['tempo_unitario']
            )

            for boca_info in distribuicao:
                ocupacao[maquina].append({
                    'cliente': item['cliente'],
                    'produto': item['produto'],
                    'boca': boca_info['boca'],
                    'quantidade': boca_info['quantidade'],
                    'tempo_horas': boca_info['tempo_horas'],
                    'cor': item['cor'],
                    'data_entrega': item['data_entrega']
                })

        return ocupacao

    @staticmethod
    def gerar_relatorio_tempo(sequencia: List[Dict]) -> Dict:
        """
        Gera relatório consolidado de tempos

        Args:
            sequencia: Sequência de produção

        Returns:
            Dicionário com estatísticas de tempo
        """
        if not sequencia:
            return {
                'tempo_total_minutos': 0,
                'tempo_total_horas': 0,
                'tempo_total_dias': 0,
                'total_pecas': 0,
                'total_pedidos': 0
            }

        tempo_total_min = sum(item['tempo_total'] for item in sequencia)
        total_pecas = sum(item['quantidade'] for item in sequencia)

        return {
            'tempo_total_minutos': tempo_total_min,
            'tempo_total_horas': tempo_total_min / 60,
            'tempo_total_dias': tempo_total_min / (60 * 24),
            'total_pecas': total_pecas,
            'total_pedidos': len(sequencia),
            'tempo_medio_por_peca': tempo_total_min / total_pecas if total_pecas > 0 else 0
        }

    @staticmethod
    def verificar_capacidade_entrega(
        tempo_total_horas: float,
        dias_ate_entrega: int,
        horas_trabalho_dia: int = 8
    ) -> Tuple[bool, str]:
        """
        Verifica se é possível entregar no prazo

        Args:
            tempo_total_horas: Tempo total de produção em horas
            dias_ate_entrega: Dias até a data de entrega
            horas_trabalho_dia: Horas de trabalho por dia

        Returns:
            Tupla (é_possível, mensagem)
        """
        horas_disponiveis = dias_ate_entrega * horas_trabalho_dia

        if horas_disponiveis >= tempo_total_horas:
            folga = horas_disponiveis - tempo_total_horas
            return True, f"✅ Entrega no prazo! Folga de {folga:.1f} horas"
        else:
            deficit = tempo_total_horas - horas_disponiveis
            return False, f"⚠️ ATENÇÃO! Faltam {deficit:.1f} horas de produção"
