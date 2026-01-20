"""
Módulo de gerenciamento de dados do Google Sheets
"""
import streamlit as st
import requests
import pandas as pd
from typing import Dict, List, Optional
import yaml
from pathlib import Path


class GoogleSheetsManager:
    """Gerencia a conexão e operações com Google Sheets via Apps Script"""

    def __init__(self):
        """Inicializa o manager carregando configurações"""
        self.config = self._load_config()
        self.base_url = self.config['google_apps_script_url']

    @staticmethod
    def _load_config() -> Dict:
        """Carrega configurações do arquivo YAML"""
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @st.cache_data(ttl=300)
    def get_all_data(_self) -> Dict:
        """
        Obtém todos os dados de todas as abas da planilha

        Returns:
            Dict com dados de todas as abas
        """
        try:
            response = requests.get(f"{_self.base_url}?action=getAll", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
            return {}

    @st.cache_data(ttl=300)
    def get_sheet_data(_self, sheet_name: str) -> List[Dict]:
        """
        Obtém dados de uma aba específica

        Args:
            sheet_name: Nome da aba

        Returns:
            Lista de dicionários com os dados
        """
        try:
            response = requests.get(
                f"{_self.base_url}?action=getSheet&sheetName={sheet_name}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao carregar dados da aba {sheet_name}: {str(e)}")
            return []

    @st.cache_data(ttl=300)
    def get_maquinas(_self) -> List[str]:
        """
        Obtém lista de máquinas disponíveis

        Returns:
            Lista de nomes de máquinas
        """
        try:
            response = requests.get(f"{_self.base_url}?action=getMaquinas", timeout=10)
            response.raise_for_status()
            maquinas = response.json()
            # Filtra valores vazios
            return [m for m in maquinas if m and str(m).strip()]
        except Exception as e:
            st.error(f"Erro ao carregar máquinas: {str(e)}")
            return []

    @st.cache_data(ttl=300)
    def get_clientes(_self) -> List[str]:
        """
        Obtém lista de clientes

        Returns:
            Lista de nomes de clientes
        """
        try:
            response = requests.get(f"{_self.base_url}?action=getClientes", timeout=10)
            response.raise_for_status()
            clientes = response.json()
            return [c for c in clientes if c and str(c).strip()]
        except Exception as e:
            st.error(f"Erro ao carregar clientes: {str(e)}")
            return []

    @st.cache_data(ttl=300)
    def get_ordens(_self) -> List[str]:
        """
        Obtém lista de ordens de compra

        Returns:
            Lista de ordens de compra
        """
        try:
            response = requests.get(f"{_self.base_url}?action=getOrdens", timeout=10)
            response.raise_for_status()
            ordens = response.json()
            return [o for o in ordens if o and str(o).strip()]
        except Exception as e:
            st.error(f"Erro ao carregar ordens: {str(e)}")
            return []

    @st.cache_data(ttl=300)
    def get_datas_entrega(_self) -> List[str]:
        """
        Obtém lista de datas de entrega

        Returns:
            Lista de datas de entrega
        """
        try:
            response = requests.get(f"{_self.base_url}?action=getDatas", timeout=10)
            response.raise_for_status()
            datas = response.json()
            return [d for d in datas if d and str(d).strip()]
        except Exception as e:
            st.error(f"Erro ao carregar datas: {str(e)}")
            return []

    def get_produtos_por_maquina(self, maquina: str) -> pd.DataFrame:
        """
        Obtém produtos de uma máquina específica

        Args:
            maquina: Nome da máquina

        Returns:
            DataFrame com produtos da máquina
        """
        # Normaliza o nome da aba
        sheet_name = f"DADOS_{maquina.replace(' ', '_').upper()}"

        try:
            data = self.get_sheet_data(sheet_name)

            if not data:
                # Retorna DataFrame vazio com colunas esperadas
                return pd.DataFrame(columns=[
                    'REFERÊNCIAS/MÁQUINA', 'TEMPO DE PRODUÇÃO', 'TEMPO DE MONTAGEM',
                    'VOLTAS NA ESPULA', 'PRODUÇÃO POR MINUTO', 'COR', 'REFERENCIA',
                    'LARGURA', 'MONTAGEM 2X2', 'TEMPO MONTAGEM 2X2'
                ])

            df = pd.DataFrame(data)

            # Garante que colunas numéricas sejam do tipo correto
            numeric_cols = ['TEMPO DE PRODUÇÃO', 'TEMPO DE MONTAGEM', 'VOLTAS NA ESPULA',
                          'PRODUÇÃO POR MINUTO', 'LARGURA', 'TEMPO MONTAGEM 2X2']

            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            return df

        except Exception as e:
            st.error(f"Erro ao carregar produtos da máquina {maquina}: {str(e)}")
            return pd.DataFrame()

    def add_produto(self, produto_data: Dict) -> bool:
        """
        Adiciona novo produto à planilha

        Args:
            produto_data: Dicionário com dados do produto

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            payload = {
                'action': 'addProduto',
                **produto_data
            }

            response = requests.post(
                self.base_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            if result.get('success'):
                # Limpa cache para forçar atualização
                st.cache_data.clear()
                return True
            else:
                st.error(f"Erro: {result.get('error', 'Erro desconhecido')}")
                return False

        except Exception as e:
            st.error(f"Erro ao adicionar produto: {str(e)}")
            return False

    def add_pedido(self, pedido_data: Dict) -> bool:
        """
        Adiciona novo pedido à planilha

        Args:
            pedido_data: Dicionário com dados do pedido

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            payload = {
                'action': 'addPedido',
                **pedido_data
            }

            response = requests.post(
                self.base_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            if result.get('success'):
                # Limpa cache para forçar atualização
                st.cache_data.clear()
                return True
            else:
                st.error(f"Erro: {result.get('error', 'Erro desconhecido')}")
                return False

        except Exception as e:
            st.error(f"Erro ao adicionar pedido: {str(e)}")
            return False

    def limpar_cache(self):
        """Limpa o cache de dados"""
        st.cache_data.clear()
