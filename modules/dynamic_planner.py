"""
Módulo de Planejamento Dinâmico de Produção
Gerencia o planejamento de produção com reordenação automática e cálculo de datas
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import json
import os

from modules.workday_calendar import get_calendar
from modules.database_manager import GoogleSheetsManager


@dataclass
class OrderItem:
    """Representa um item de pedido no planejamento"""
    id: str
    cliente: str
    ordem_compra: str
    data_entrega: str  # DD/MM/YYYY
    maquina: str
    bocas: int
    produto: str
    quantidade: int
    tempo_producao: float  # minutos
    tempo_montagem: float  # minutos
    montagem_2x2: bool = False
    tempo_montagem_2x2: float = 0.0  # minutos
    ordem: int = 0  # Posição na sequência

    # Campos calculados
    tempo_total_minutos: float = 0.0
    tempo_total_horas: float = 0.0
    data_inicio: Optional[str] = None  # DD/MM/YYYY
    data_fim: Optional[str] = None  # DD/MM/YYYY
    dias_uteis: int = 0

    def __post_init__(self):
        """Calcula campos derivados após inicialização"""
        self.calculate_times()

    def calculate_times(self):
        """Calcula os tempos totais de produção"""
        base_time = self.tempo_producao + self.tempo_montagem

        if self.montagem_2x2:
            base_time += self.tempo_montagem_2x2

        # Tempo total considerando bocas
        self.tempo_total_minutos = base_time * self.quantidade / max(self.bocas, 1)
        self.tempo_total_horas = self.tempo_total_minutos / 60.0

    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'cliente': self.cliente,
            'ordem_compra': self.ordem_compra,
            'data_entrega': self.data_entrega,
            'maquina': self.maquina,
            'bocas': self.bocas,
            'produto': self.produto,
            'quantidade': self.quantidade,
            'tempo_producao': self.tempo_producao,
            'tempo_montagem': self.tempo_montagem,
            'montagem_2x2': self.montagem_2x2,
            'tempo_montagem_2x2': self.tempo_montagem_2x2,
            'ordem': self.ordem,
            'tempo_total_minutos': round(self.tempo_total_minutos, 2),
            'tempo_total_horas': round(self.tempo_total_horas, 2),
            'data_inicio': self.data_inicio,
            'data_fim': self.data_fim,
            'dias_uteis': self.dias_uteis
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'OrderItem':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data.get('id', ''),
            cliente=data.get('cliente', ''),
            ordem_compra=data.get('ordem_compra', ''),
            data_entrega=data.get('data_entrega', ''),
            maquina=data.get('maquina', ''),
            bocas=data.get('bocas', 1),
            produto=data.get('produto', ''),
            quantidade=data.get('quantidade', 0),
            tempo_producao=data.get('tempo_producao', 0.0),
            tempo_montagem=data.get('tempo_montagem', 0.0),
            montagem_2x2=data.get('montagem_2x2', False),
            tempo_montagem_2x2=data.get('tempo_montagem_2x2', 0.0),
            ordem=data.get('ordem', 0),
            data_inicio=data.get('data_inicio'),
            data_fim=data.get('data_fim'),
            dias_uteis=data.get('dias_uteis', 0)
        )


class DynamicPlanner:
    """Gerenciador de planejamento dinâmico de produção"""

    def __init__(self):
        """Inicializa o planejador"""
        self.calendar = get_calendar()
        self.db_manager = GoogleSheetsManager()
        self.plans_file = "config/production_plans.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Garante que o diretório de configuração existe"""
        config_dir = os.path.dirname(self.plans_file)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)

    def create_plan(
        self,
        orders: List[Dict],
        start_date: Optional[datetime] = None
    ) -> Dict:
        """
        Cria um plano de produção completo

        Args:
            orders: Lista de pedidos
            start_date: Data de início (default: hoje)

        Returns:
            Dicionário com plano completo
        """
        if start_date is None:
            start_date = datetime.now()

        # Converte pedidos para OrderItem
        order_items = []
        for idx, order_data in enumerate(orders):
            order_data['ordem'] = idx
            order_item = OrderItem.from_dict(order_data)
            order_items.append(order_item)

        # Agrupa pedidos por máquina
        machines_orders = {}
        for order in order_items:
            if order.maquina not in machines_orders:
                machines_orders[order.maquina] = []
            machines_orders[order.maquina].append(order)

        # Calcula datas para cada máquina
        machine_plans = {}
        all_orders_with_dates = []

        for maquina, machine_orders in machines_orders.items():
            # Obtém disponibilidade da máquina
            availability = self.db_manager.get_machine_availability(maquina)

            # Calcula sequência para esta máquina
            current_date = start_date
            machine_plan_orders = []

            for order in sorted(machine_orders, key=lambda x: x.ordem):
                # Se não for dia útil, avança para o próximo
                if not self.calendar.is_workday(current_date):
                    current_date = self.calendar.get_next_workday(current_date)

                # Calcula data de fim
                end_date, details = self.calendar.calculate_end_date(
                    current_date,
                    order.tempo_total_horas,
                    availability
                )

                # Atualiza o pedido com as datas
                order.data_inicio = current_date.strftime("%d/%m/%Y")
                order.data_fim = end_date.strftime("%d/%m/%Y")
                order.dias_uteis = details['workdays_used']

                machine_plan_orders.append(order)
                all_orders_with_dates.append(order)

                # Próximo pedido começa no dia seguinte ao fim deste
                current_date = self.calendar.get_next_workday(end_date)

            machine_plans[maquina] = {
                'maquina': maquina,
                'availability_hours': availability,
                'orders': [o.to_dict() for o in machine_plan_orders],
                'total_orders': len(machine_plan_orders),
                'total_hours': sum(o.tempo_total_horas for o in machine_plan_orders)
            }

        # Análise geral
        total_hours = sum(o.tempo_total_horas for o in all_orders_with_dates)

        # Verifica alertas (pedidos que terminam após a data de entrega)
        alerts = []
        critical_count = 0
        warning_count = 0

        for order in all_orders_with_dates:
            try:
                data_fim = datetime.strptime(order.data_fim, "%d/%m/%Y")
                data_entrega = datetime.strptime(order.data_entrega, "%d/%m/%Y")

                if data_fim > data_entrega:
                    days_late = (data_fim - data_entrega).days
                    critical_count += 1
                    alerts.append({
                        'tipo': 'CRITICO',
                        'pedido_id': order.id,
                        'cliente': order.cliente,
                        'produto': order.produto,
                        'mensagem': f'Pedido terminará {days_late} dia(s) após a data de entrega',
                        'data_entrega': order.data_entrega,
                        'data_fim': order.data_fim
                    })
                elif (data_entrega - data_fim).days <= 3:
                    warning_count += 1
                    alerts.append({
                        'tipo': 'ATENCAO',
                        'pedido_id': order.id,
                        'cliente': order.cliente,
                        'produto': order.produto,
                        'mensagem': 'Margem de segurança muito pequena (≤ 3 dias)',
                        'data_entrega': order.data_entrega,
                        'data_fim': order.data_fim
                    })
            except:
                pass

        plan = {
            'success': True,
            'start_date': start_date.strftime("%d/%m/%Y"),
            'machine_plans': machine_plans,
            'summary': {
                'total_orders': len(all_orders_with_dates),
                'total_machines': len(machine_plans),
                'total_hours': round(total_hours, 2),
                'total_days': round(total_hours / 8, 1),
                'critical_orders': critical_count,
                'warning_orders': warning_count,
                'ok_orders': len(all_orders_with_dates) - critical_count - warning_count
            },
            'alerts': alerts,
            'all_orders': [o.to_dict() for o in all_orders_with_dates]
        }

        return plan

    def reorder_and_recalculate(
        self,
        machine: str,
        order_ids: List[str],
        all_orders: List[Dict],
        start_date: Optional[datetime] = None
    ) -> Dict:
        """
        Reordena pedidos de uma máquina e recalcula todas as datas

        Args:
            machine: Nome da máquina
            order_ids: Lista de IDs dos pedidos na nova ordem
            all_orders: Lista completa de todos os pedidos
            start_date: Data de início (default: hoje)

        Returns:
            Plano recalculado
        """
        if start_date is None:
            start_date = datetime.now()

        # Filtra e reordena pedidos da máquina
        machine_orders = [o for o in all_orders if o.get('maquina') == machine]
        other_orders = [o for o in all_orders if o.get('maquina') != machine]

        # Cria dicionário para acesso rápido
        orders_dict = {o['id']: o for o in machine_orders}

        # Reordena conforme lista de IDs
        reordered = []
        for idx, order_id in enumerate(order_ids):
            if order_id in orders_dict:
                order = orders_dict[order_id]
                order['ordem'] = idx
                reordered.append(order)

        # Combina com pedidos de outras máquinas
        all_reordered = reordered + other_orders

        # Recalcula o plano
        return self.create_plan(all_reordered, start_date)

    def move_order(
        self,
        order_id: str,
        from_position: int,
        to_position: int,
        machine: str,
        all_orders: List[Dict],
        start_date: Optional[datetime] = None
    ) -> Dict:
        """
        Move um pedido de uma posição para outra

        Args:
            order_id: ID do pedido a mover
            from_position: Posição atual
            to_position: Nova posição
            machine: Máquina do pedido
            all_orders: Lista completa de pedidos
            start_date: Data de início

        Returns:
            Plano recalculado
        """
        # Filtra pedidos da máquina
        machine_orders = [o for o in all_orders if o.get('maquina') == machine]

        # Ordena por ordem atual
        machine_orders.sort(key=lambda x: x.get('ordem', 0))

        # Move o item
        if 0 <= from_position < len(machine_orders) and 0 <= to_position < len(machine_orders):
            item = machine_orders.pop(from_position)
            machine_orders.insert(to_position, item)

            # Atualiza ordens
            for idx, order in enumerate(machine_orders):
                order['ordem'] = idx

            # Cria lista de IDs na nova ordem
            order_ids = [o['id'] for o in machine_orders]

            # Recalcula
            return self.reorder_and_recalculate(machine, order_ids, all_orders, start_date)

        return {'success': False, 'error': 'Posições inválidas'}

    def get_machine_timeline(self, machine: str, plan: Dict) -> Dict:
        """
        Obtém timeline de produção de uma máquina

        Args:
            machine: Nome da máquina
            plan: Plano completo

        Returns:
            Timeline com eventos
        """
        if machine not in plan['machine_plans']:
            return {'success': False, 'error': 'Máquina não encontrada no plano'}

        machine_plan = plan['machine_plans'][machine]
        orders = machine_plan['orders']

        timeline = []
        for order in orders:
            timeline.append({
                'id': order['id'],
                'cliente': order['cliente'],
                'produto': order['produto'],
                'quantidade': order['quantidade'],
                'data_inicio': order['data_inicio'],
                'data_fim': order['data_fim'],
                'dias_uteis': order['dias_uteis'],
                'horas': order['tempo_total_horas']
            })

        return {
            'success': True,
            'machine': machine,
            'timeline': timeline,
            'total_items': len(timeline)
        }

    def save_plan(self, plan_name: str, plan: Dict) -> bool:
        """
        Salva um plano em arquivo

        Args:
            plan_name: Nome do plano
            plan: Dados do plano

        Returns:
            True se salvou com sucesso
        """
        try:
            plans = {}
            if os.path.exists(self.plans_file):
                with open(self.plans_file, 'r', encoding='utf-8') as f:
                    plans = json.load(f)

            plans[plan_name] = {
                'created_at': datetime.now().isoformat(),
                'plan': plan
            }

            with open(self.plans_file, 'w', encoding='utf-8') as f:
                json.dump(plans, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Erro ao salvar plano: {e}")
            return False

    def load_plan(self, plan_name: str) -> Optional[Dict]:
        """
        Carrega um plano salvo

        Args:
            plan_name: Nome do plano

        Returns:
            Dados do plano ou None se não encontrado
        """
        try:
            if not os.path.exists(self.plans_file):
                return None

            with open(self.plans_file, 'r', encoding='utf-8') as f:
                plans = json.load(f)

            if plan_name in plans:
                return plans[plan_name]['plan']

            return None
        except Exception as e:
            print(f"Erro ao carregar plano: {e}")
            return None

    def list_saved_plans(self) -> List[Dict]:
        """
        Lista todos os planos salvos

        Returns:
            Lista de planos salvos com metadados
        """
        try:
            if not os.path.exists(self.plans_file):
                return []

            with open(self.plans_file, 'r', encoding='utf-8') as f:
                plans = json.load(f)

            result = []
            for name, data in plans.items():
                plan_info = {
                    'name': name,
                    'created_at': data['created_at'],
                    'total_orders': data['plan']['summary']['total_orders'],
                    'total_machines': data['plan']['summary']['total_machines'],
                    'total_hours': data['plan']['summary']['total_hours']
                }
                result.append(plan_info)

            return result
        except Exception as e:
            print(f"Erro ao listar planos: {e}")
            return []


# Instância global do planejador
_planner_instance = None


def get_planner() -> DynamicPlanner:
    """Retorna a instância global do planejador"""
    global _planner_instance
    if _planner_instance is None:
        _planner_instance = DynamicPlanner()
    return _planner_instance
