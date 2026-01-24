"""
Módulo de Calendário de Trabalho
Gerencia dias úteis, feriados e fins de semana para cálculo de datas de produção
"""

from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional, Tuple
import json
import os
from pathlib import Path


class WorkdayCalendar:
    """Gerencia o calendário de trabalho com feriados e fins de semana"""

    def __init__(self, config_file: str = "config/workday_calendar.json"):
        """
        Inicializa o calendário de trabalho

        Args:
            config_file: Caminho para o arquivo de configuração JSON
        """
        self.config_file = config_file
        self.holidays: Set[str] = set()  # Formato: "DD/MM/YYYY"
        self.working_saturdays: Set[str] = set()  # Sábados que são dias de trabalho
        self.working_sundays: Set[str] = set()  # Domingos que são dias de trabalho
        self.work_by_default_saturday: bool = False  # Trabalha aos sábados por padrão
        self.work_by_default_sunday: bool = False  # Trabalha aos domingos por padrão

        self._ensure_config_dir()
        self._load_config()

    def _ensure_config_dir(self):
        """Garante que o diretório de configuração existe"""
        config_dir = os.path.dirname(self.config_file)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)

    def _load_config(self):
        """Carrega configuração do arquivo JSON"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.holidays = set(data.get('holidays', []))
                    self.working_saturdays = set(data.get('working_saturdays', []))
                    self.working_sundays = set(data.get('working_sundays', []))
                    self.work_by_default_saturday = data.get('work_by_default_saturday', False)
                    self.work_by_default_sunday = data.get('work_by_default_sunday', False)
            except Exception as e:
                print(f"Erro ao carregar calendário: {e}")
                self._create_default_config()
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Cria configuração padrão"""
        self.holidays = set()
        self.working_saturdays = set()
        self.working_sundays = set()
        self.work_by_default_saturday = False
        self.work_by_default_sunday = False
        self._save_config()

    def _save_config(self):
        """Salva configuração no arquivo JSON"""
        data = {
            'holidays': list(self.holidays),
            'working_saturdays': list(self.working_saturdays),
            'working_sundays': list(self.working_sundays),
            'work_by_default_saturday': self.work_by_default_saturday,
            'work_by_default_sunday': self.work_by_default_sunday
        }

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_holidays(self, dates: List[str]) -> Dict[str, any]:
        """
        Adiciona feriados ao calendário

        Args:
            dates: Lista de datas no formato DD/MM/YYYY

        Returns:
            Dicionário com resultado da operação
        """
        added = []
        invalid = []

        for date_str in dates:
            try:
                # Valida formato da data
                datetime.strptime(date_str, "%d/%m/%Y")
                self.holidays.add(date_str)
                added.append(date_str)
            except ValueError:
                invalid.append(date_str)

        if added:
            self._save_config()

        return {
            'success': True,
            'added': added,
            'invalid': invalid,
            'total_holidays': len(self.holidays)
        }

    def remove_holidays(self, dates: List[str]) -> Dict[str, any]:
        """
        Remove feriados do calendário

        Args:
            dates: Lista de datas no formato DD/MM/YYYY

        Returns:
            Dicionário com resultado da operação
        """
        removed = []
        not_found = []

        for date_str in dates:
            if date_str in self.holidays:
                self.holidays.remove(date_str)
                removed.append(date_str)
            else:
                not_found.append(date_str)

        if removed:
            self._save_config()

        return {
            'success': True,
            'removed': removed,
            'not_found': not_found,
            'total_holidays': len(self.holidays)
        }

    def get_holidays(self) -> List[str]:
        """Retorna lista de feriados cadastrados"""
        return sorted(list(self.holidays), key=lambda x: datetime.strptime(x, "%d/%m/%Y"))

    def set_weekend_working(self, work_saturday: bool, work_sunday: bool):
        """
        Define se trabalha aos fins de semana por padrão

        Args:
            work_saturday: True se trabalha aos sábados
            work_sunday: True se trabalha aos domingos
        """
        self.work_by_default_saturday = work_saturday
        self.work_by_default_sunday = work_sunday
        self._save_config()

    def get_weekend_config(self) -> Dict[str, bool]:
        """Retorna configuração de fins de semana"""
        return {
            'work_saturday': self.work_by_default_saturday,
            'work_sunday': self.work_by_default_sunday
        }

    def get_weekends_in_year(self, year: int) -> Dict[str, List[str]]:
        """
        Retorna todos os sábados e domingos de um ano

        Args:
            year: Ano para gerar a lista

        Returns:
            Dicionário com listas de sábados e domingos
        """
        saturdays = []
        sundays = []

        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%d/%m/%Y")

            if current_date.weekday() == 5:  # Sábado
                saturdays.append({
                    'date': date_str,
                    'working': date_str in self.working_saturdays or self.work_by_default_saturday
                })
            elif current_date.weekday() == 6:  # Domingo
                sundays.append({
                    'date': date_str,
                    'working': date_str in self.working_sundays or self.work_by_default_sunday
                })

            current_date += timedelta(days=1)

        return {
            'year': year,
            'saturdays': saturdays,
            'sundays': sundays
        }

    def set_working_weekend_dates(self, saturdays: List[str], sundays: List[str]):
        """
        Define datas específicas de fins de semana como dias de trabalho

        Args:
            saturdays: Lista de sábados que são dias de trabalho (DD/MM/YYYY)
            sundays: Lista de domingos que são dias de trabalho (DD/MM/YYYY)
        """
        self.working_saturdays = set(saturdays)
        self.working_sundays = set(sundays)
        self._save_config()

    def is_workday(self, date: datetime) -> bool:
        """
        Verifica se uma data é dia de trabalho

        Args:
            date: Data para verificar

        Returns:
            True se é dia de trabalho, False caso contrário
        """
        date_str = date.strftime("%d/%m/%Y")

        # Verifica se é feriado
        if date_str in self.holidays:
            return False

        weekday = date.weekday()

        # Verifica sábado (weekday = 5)
        if weekday == 5:
            # Se está na lista de sábados que trabalha, é dia de trabalho
            if date_str in self.working_saturdays:
                return True
            # Se não está na lista, verifica o padrão
            return self.work_by_default_saturday

        # Verifica domingo (weekday = 6)
        if weekday == 6:
            # Se está na lista de domingos que trabalha, é dia de trabalho
            if date_str in self.working_sundays:
                return True
            # Se não está na lista, verifica o padrão
            return self.work_by_default_sunday

        # Segunda a sexta são dias de trabalho
        return True

    def get_next_workday(self, date: datetime) -> datetime:
        """
        Retorna o próximo dia útil após a data informada

        Args:
            date: Data de referência

        Returns:
            Próximo dia útil
        """
        next_day = date + timedelta(days=1)

        # Procura até encontrar um dia útil (máximo 365 dias)
        for _ in range(365):
            if self.is_workday(next_day):
                return next_day
            next_day += timedelta(days=1)

        # Se não encontrou em 1 ano, retorna a data original (erro)
        return date

    def calculate_end_date(
        self,
        start_date: datetime,
        hours_needed: float,
        hours_per_day: float
    ) -> Tuple[datetime, Dict[str, any]]:
        """
        Calcula a data de finalização considerando apenas dias úteis

        Args:
            start_date: Data de início da produção
            hours_needed: Horas totais necessárias para produção
            hours_per_day: Horas disponíveis por dia

        Returns:
            Tupla com (data_final, detalhes)
        """
        if hours_per_day <= 0:
            raise ValueError("Horas por dia deve ser maior que zero")

        current_date = start_date
        hours_remaining = hours_needed
        days_used = 0

        # Se a data de início não for dia útil, começa no próximo dia útil
        if not self.is_workday(current_date):
            current_date = self.get_next_workday(current_date)

        # Calcula dia a dia
        while hours_remaining > 0:
            if self.is_workday(current_date):
                # Desconta as horas disponíveis do dia
                if hours_remaining >= hours_per_day:
                    hours_remaining -= hours_per_day
                    days_used += 1

                    # Se ainda sobrou tempo, vai para o próximo dia útil
                    if hours_remaining > 0:
                        current_date = self.get_next_workday(current_date)
                else:
                    # Último dia parcial
                    days_used += 1
                    hours_remaining = 0
            else:
                # Pula para o próximo dia útil
                current_date = self.get_next_workday(current_date)

        details = {
            'start_date': start_date.strftime("%d/%m/%Y"),
            'end_date': current_date.strftime("%d/%m/%Y"),
            'hours_needed': round(hours_needed, 2),
            'hours_per_day': hours_per_day,
            'workdays_used': days_used,
            'total_days': (current_date - start_date).days + 1
        }

        return current_date, details

    def count_workdays_between(self, start_date: datetime, end_date: datetime) -> int:
        """
        Conta quantos dias úteis existem entre duas datas

        Args:
            start_date: Data inicial
            end_date: Data final

        Returns:
            Número de dias úteis
        """
        if start_date > end_date:
            return 0

        workdays = 0
        current_date = start_date

        while current_date <= end_date:
            if self.is_workday(current_date):
                workdays += 1
            current_date += timedelta(days=1)

        return workdays

    def get_summary(self) -> Dict[str, any]:
        """Retorna resumo da configuração do calendário"""
        current_year = datetime.now().year

        return {
            'total_holidays': len(self.holidays),
            'holidays': self.get_holidays(),
            'weekend_config': {
                'work_saturday_by_default': self.work_by_default_saturday,
                'work_sunday_by_default': self.work_by_default_sunday,
                'working_saturdays_count': len(self.working_saturdays),
                'working_sundays_count': len(self.working_sundays)
            },
            'current_year': current_year
        }

    def clear_all(self):
        """Limpa todas as configurações do calendário"""
        self.holidays = set()
        self.working_saturdays = set()
        self.working_sundays = set()
        self.work_by_default_saturday = False
        self.work_by_default_sunday = False
        self._save_config()


# Instância global do calendário
_calendar_instance = None


def get_calendar() -> WorkdayCalendar:
    """Retorna a instância global do calendário"""
    global _calendar_instance
    if _calendar_instance is None:
        _calendar_instance = WorkdayCalendar()
    return _calendar_instance
