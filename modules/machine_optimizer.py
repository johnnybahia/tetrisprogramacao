"""
Otimizador de Distribuição de Máquinas
Analisa pedidos e sugere a melhor alocação de máquinas para minimizar atrasos
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import copy

from modules.database_manager import GoogleSheetsManager
from modules.workday_calendar import get_calendar


@dataclass
class MachineOption:
    """Representa uma opção de máquina para um pedido"""
    maquina: str
    tempo_producao: float  # minutos
    tempo_montagem: float  # minutos
    tempo_total_horas: float
    disponibilidade_horas: float
    viavel: bool
    prioridade: float  # quanto menor, melhor


class MachineOptimizer:
    """Otimiza a distribuição de pedidos entre máquinas"""

    def __init__(self):
        self.db_manager = GoogleSheetsManager()
        self.calendar = get_calendar()

    def analyze_and_suggest(
        self,
        orders: List[Dict],
        start_date: Optional[datetime] = None
    ) -> Dict:
        """
        Analisa pedidos e sugere melhor distribuição de máquinas

        Args:
            orders: Lista de pedidos
            start_date: Data de início do planejamento

        Returns:
            Dicionário com sugestões de otimização
        """
        if start_date is None:
            start_date = datetime.now()

        # Para cada pedido, encontra todas as máquinas compatíveis
        suggestions = []
        machine_loads = {}  # Rastreia carga de cada máquina

        # Ordena pedidos por urgência (data de entrega)
        sorted_orders = self._sort_by_urgency(orders)

        for order in sorted_orders:
            produto = order['produto']

            # Encontra todas as máquinas que podem produzir este produto
            compatible_machines = self._find_compatible_machines(produto)

            if not compatible_machines:
                suggestions.append({
                    'order': order,
                    'current_machine': order.get('maquina'),
                    'suggested_machine': order.get('maquina'),
                    'reason': 'Nenhuma máquina compatível encontrada',
                    'status': 'error',
                    'options': []
                })
                continue

            # Avalia cada máquina compatível
            options = []
            for machine_name, product_info in compatible_machines.items():
                # Calcula tempo de produção nesta máquina
                tempo_producao = float(product_info.get('TEMPO DE PRODUÇÃO', 0))
                tempo_montagem = float(product_info.get('TEMPO DE MONTAGEM', 0))
                montagem_2x2 = product_info.get('MONTAGEM 2X2') == 'Sim'
                tempo_montagem_2x2 = float(product_info.get('TEMPO MONTAGEM 2X2', 0))

                tempo_base = tempo_producao + tempo_montagem
                if montagem_2x2:
                    tempo_base += tempo_montagem_2x2

                bocas = order.get('bocas', 1)
                quantidade = order.get('quantidade', 1)
                tempo_total_min = (tempo_base * quantidade) / max(bocas, 1)
                tempo_total_horas = tempo_total_min / 60.0

                # Disponibilidade da máquina
                disponibilidade = self.db_manager.get_machine_availability(machine_name)

                # Carga atual da máquina
                current_load = machine_loads.get(machine_name, 0)

                # Calcula prioridade (menor = melhor)
                # Fatores: carga atual, tempo de produção, disponibilidade
                priority = (current_load / disponibilidade) + (tempo_total_horas / disponibilidade)

                # Verifica viabilidade (tempo disponível até entrega)
                try:
                    data_entrega = datetime.strptime(order['data_entrega'], "%d/%m/%Y")
                except:
                    data_entrega = datetime.strptime(order['data_entrega'], "%Y-%m-%d")

                dias_disponiveis = self.calendar.count_workdays_between(start_date, data_entrega)
                horas_disponiveis = dias_disponiveis * disponibilidade
                viavel = horas_disponiveis >= (current_load + tempo_total_horas)

                option = MachineOption(
                    maquina=machine_name,
                    tempo_producao=tempo_producao,
                    tempo_montagem=tempo_montagem,
                    tempo_total_horas=tempo_total_horas,
                    disponibilidade_horas=disponibilidade,
                    viavel=viavel,
                    prioridade=priority
                )

                options.append(option)

            # Ordena opções por prioridade (melhor primeiro)
            options.sort(key=lambda x: (not x.viavel, x.prioridade))

            # Sugestão é a melhor opção
            best_option = options[0] if options else None
            current_machine = order.get('maquina')

            if best_option:
                # Atualiza carga da máquina sugerida
                if best_option.maquina not in machine_loads:
                    machine_loads[best_option.maquina] = 0
                machine_loads[best_option.maquina] += best_option.tempo_total_horas

                # Determina status
                if best_option.maquina == current_machine:
                    status = 'keep'
                    reason = 'Máquina atual já é a melhor opção'
                elif best_option.viavel and not any(opt for opt in options if opt.maquina == current_machine and opt.viavel):
                    status = 'critical'
                    reason = f'Trocar para {best_option.maquina} - Máquina atual inviável'
                elif best_option.prioridade < next((opt.prioridade for opt in options if opt.maquina == current_machine), float('inf')):
                    status = 'improve'
                    reason = f'Trocar para {best_option.maquina} - Reduz tempo em {int((next((opt.prioridade for opt in options if opt.maquina == current_machine), best_option.prioridade) - best_option.prioridade) * 100)}%'
                else:
                    status = 'keep'
                    reason = 'Máquina atual é adequada'

                suggestions.append({
                    'order': order,
                    'current_machine': current_machine,
                    'suggested_machine': best_option.maquina,
                    'reason': reason,
                    'status': status,
                    'options': [
                        {
                            'maquina': opt.maquina,
                            'tempo_total_horas': round(opt.tempo_total_horas, 2),
                            'disponibilidade': opt.disponibilidade_horas,
                            'viavel': opt.viavel,
                            'prioridade': round(opt.prioridade, 2),
                            'is_current': opt.maquina == current_machine,
                            'is_suggested': opt.maquina == best_option.maquina
                        }
                        for opt in options[:5]  # Top 5 opções
                    ],
                    'time_improvement': self._calculate_improvement(
                        current_machine, best_option.maquina, options
                    )
                })

        # Estatísticas gerais
        total_orders = len(suggestions)
        critical_changes = sum(1 for s in suggestions if s['status'] == 'critical')
        improvements = sum(1 for s in suggestions if s['status'] == 'improve')
        keep_same = sum(1 for s in suggestions if s['status'] == 'keep')

        return {
            'success': True,
            'suggestions': suggestions,
            'statistics': {
                'total_orders': total_orders,
                'critical_changes': critical_changes,
                'improvements': improvements,
                'keep_same': keep_same,
                'total_changes_suggested': critical_changes + improvements,
                'efficiency_gain': round((improvements + critical_changes) / max(total_orders, 1) * 100, 1)
            },
            'machine_loads': {
                machine: round(load, 2)
                for machine, load in machine_loads.items()
            }
        }

    def apply_suggestions(
        self,
        orders: List[Dict],
        suggestions: List[Dict]
    ) -> List[Dict]:
        """
        Aplica sugestões de otimização aos pedidos

        Args:
            orders: Lista original de pedidos
            suggestions: Lista de sugestões do analyze_and_suggest

        Returns:
            Lista de pedidos com máquinas otimizadas
        """
        optimized_orders = copy.deepcopy(orders)

        for i, suggestion in enumerate(suggestions):
            if i < len(optimized_orders):
                suggested_machine = suggestion['suggested_machine']

                # Atualiza a máquina do pedido
                optimized_orders[i]['maquina'] = suggested_machine

                # Se houver opções, pega os tempos da máquina sugerida
                if suggestion.get('options'):
                    best_option = next(
                        (opt for opt in suggestion['options'] if opt['is_suggested']),
                        None
                    )

                    if best_option:
                        # Busca dados completos do produto na nova máquina
                        try:
                            produtos = self.db_manager.get_produtos_por_maquina(suggested_machine)
                            produto_ref = optimized_orders[i]['produto']

                            produto_info = produtos[
                                (produtos['REFERÊNCIAS/MÁQUINA'] == produto_ref) |
                                (produtos['REFERENCIA'] == produto_ref)
                            ]

                            if not produto_info.empty:
                                prod_dict = produto_info.iloc[0].to_dict()
                                optimized_orders[i]['tempo_producao'] = float(prod_dict.get('TEMPO DE PRODUÇÃO', 0))
                                optimized_orders[i]['tempo_montagem'] = float(prod_dict.get('TEMPO DE MONTAGEM', 0))
                                optimized_orders[i]['montagem_2x2'] = prod_dict.get('MONTAGEM 2X2') == 'Sim'
                                optimized_orders[i]['tempo_montagem_2x2'] = float(prod_dict.get('TEMPO MONTAGEM 2X2', 0))
                        except Exception as e:
                            print(f"Erro ao atualizar dados do produto: {e}")

        return optimized_orders

    def _find_compatible_machines(self, produto: str) -> Dict[str, Dict]:
        """
        Encontra todas as máquinas que podem produzir um produto

        Args:
            produto: Referência do produto

        Returns:
            Dicionário {nome_maquina: info_produto}
        """
        compatible = {}

        try:
            maquinas = self.db_manager.get_maquinas()

            for maquina in maquinas:
                try:
                    produtos = self.db_manager.get_produtos_por_maquina(maquina)

                    # Busca o produto usando REFERÊNCIAS/MÁQUINA ou REFERENCIA
                    match = produtos[
                        (produtos['REFERÊNCIAS/MÁQUINA'] == produto) |
                        (produtos['REFERENCIA'] == produto)
                    ]

                    if not match.empty:
                        compatible[maquina] = match.iloc[0].to_dict()

                except Exception as e:
                    continue

        except Exception as e:
            print(f"Erro ao buscar máquinas compatíveis: {e}")

        return compatible

    def _sort_by_urgency(self, orders: List[Dict]) -> List[Dict]:
        """Ordena pedidos por urgência (data de entrega mais próxima primeiro)"""
        def get_date(order):
            try:
                return datetime.strptime(order['data_entrega'], "%d/%m/%Y")
            except:
                try:
                    return datetime.strptime(order['data_entrega'], "%Y-%m-%d")
                except:
                    return datetime.max

        return sorted(orders, key=get_date)

    def _calculate_improvement(
        self,
        current_machine: str,
        suggested_machine: str,
        options: List[MachineOption]
    ) -> Dict:
        """Calcula melhoria ao trocar de máquina"""
        current_opt = next((opt for opt in options if opt.maquina == current_machine), None)
        suggested_opt = next((opt for opt in options if opt.maquina == suggested_machine), None)

        if not current_opt or not suggested_opt:
            return {
                'has_improvement': False,
                'time_saved_hours': 0,
                'percentage': 0
            }

        time_saved = current_opt.tempo_total_horas - suggested_opt.tempo_total_horas
        percentage = (time_saved / current_opt.tempo_total_horas * 100) if current_opt.tempo_total_horas > 0 else 0

        return {
            'has_improvement': time_saved > 0,
            'time_saved_hours': round(time_saved, 2),
            'percentage': round(percentage, 1)
        }


# Instância global
_optimizer_instance = None


def get_machine_optimizer() -> MachineOptimizer:
    """Retorna instância global do otimizador"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = MachineOptimizer()
    return _optimizer_instance
