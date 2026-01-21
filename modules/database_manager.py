"""
Módulo de gerenciamento de dados do Google Sheets
"""
import requests
import pandas as pd
from typing import Dict, List, Optional
import yaml
from pathlib import Path
from functools import lru_cache
import time

# Importa streamlit apenas se disponível
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


class GoogleSheetsManager:
    """Gerencia a conexão e operações com Google Sheets via Apps Script"""

    def __init__(self):
        """Inicializa o manager carregando configurações"""
        self.config = self._load_config()
        self.base_url = self.config['google_apps_script_url']
        self._cache = {}  # Cache simples para FastAPI
        self._cache_time = {}

    @staticmethod
    def _load_config() -> Dict:
        """Carrega configurações do arquivo YAML"""
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _is_cache_valid(self, key: str, ttl: int = 300) -> bool:
        """Verifica se o cache ainda é válido"""
        if key not in self._cache_time:
            return False
        return (time.time() - self._cache_time[key]) < ttl

    def _get_from_cache(self, key: str):
        """Obtém valor do cache"""
        return self._cache.get(key)

    def _set_cache(self, key: str, value):
        """Armazena valor no cache"""
        self._cache[key] = value
        self._cache_time[key] = time.time()

    def get_all_data(self) -> Dict:
        """
        Obtém todos os dados de todas as abas da planilha

        Returns:
            Dict com dados de todas as abas
        """
        cache_key = "all_data"

        # Verifica cache
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)

        try:
            response = requests.get(f"{self.base_url}?action=getAll", timeout=10)
            response.raise_for_status()
            data = response.json()
            self._set_cache(cache_key, data)
            return data
        except Exception as e:
            error_msg = f"Erro ao carregar dados: {str(e)}"
            if HAS_STREAMLIT:
                st.error(error_msg)
            else:
                print(error_msg)
            return {}

    def get_sheet_data(self, sheet_name: str) -> List[Dict]:
        """
        Obtém dados de uma aba específica

        Args:
            sheet_name: Nome da aba

        Returns:
            Lista de dicionários com os dados
        """
        cache_key = f"sheet_{sheet_name}"

        # Verifica cache
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)

        try:
            response = requests.get(
                f"{self.base_url}?action=getSheet&sheetName={sheet_name}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self._set_cache(cache_key, data)
            return data
        except Exception as e:
            error_msg = f"Erro ao carregar dados da aba {sheet_name}: {str(e)}"
            if HAS_STREAMLIT:
                st.error(error_msg)
            else:
                print(error_msg)
            return []

    def get_maquinas(self) -> List[str]:
        """
        Obtém lista de máquinas disponíveis

        Returns:
            Lista de nomes de máquinas
        """
        cache_key = "maquinas"

        # Verifica cache
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)

        try:
            response = requests.get(f"{self.base_url}?action=getMaquinas", timeout=10)
            response.raise_for_status()
            maquinas = response.json()
            # Filtra valores vazios
            maquinas_filtradas = [m for m in maquinas if m and str(m).strip()]
            self._set_cache(cache_key, maquinas_filtradas)
            return maquinas_filtradas
        except Exception as e:
            error_msg = f"Erro ao carregar máquinas: {str(e)}"
            if HAS_STREAMLIT:
                st.error(error_msg)
            else:
                print(error_msg)
            return []

    def get_clientes(self) -> List[str]:
        """
        Obtém lista de clientes

        Returns:
            Lista de nomes de clientes
        """
        cache_key = "clientes"

        # Verifica cache
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)

        try:
            response = requests.get(f"{self.base_url}?action=getClientes", timeout=10)
            response.raise_for_status()
            clientes = response.json()
            clientes_filtrados = [c for c in clientes if c and str(c).strip()]
            self._set_cache(cache_key, clientes_filtrados)
            return clientes_filtrados
        except Exception as e:
            error_msg = f"Erro ao carregar clientes: {str(e)}"
            if HAS_STREAMLIT:
                st.error(error_msg)
            else:
                print(error_msg)
            return []

    def get_ordens(self) -> List[str]:
        """
        Obtém lista de ordens de compra

        Returns:
            Lista de ordens de compra
        """
        cache_key = "ordens"

        # Verifica cache
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)

        try:
            response = requests.get(f"{self.base_url}?action=getOrdens", timeout=10)
            response.raise_for_status()
            ordens = response.json()
            ordens_filtradas = [o for o in ordens if o and str(o).strip()]
            self._set_cache(cache_key, ordens_filtradas)
            return ordens_filtradas
        except Exception as e:
            error_msg = f"Erro ao carregar ordens: {str(e)}"
            if HAS_STREAMLIT:
                st.error(error_msg)
            else:
                print(error_msg)
            return []

    def get_datas_entrega(self) -> List[str]:
        """
        Obtém lista de datas de entrega

        Returns:
            Lista de datas de entrega
        """
        cache_key = "datas"

        # Verifica cache
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)

        try:
            response = requests.get(f"{self.base_url}?action=getDatas", timeout=10)
            response.raise_for_status()
            datas = response.json()
            datas_filtradas = [d for d in datas if d and str(d).strip()]
            self._set_cache(cache_key, datas_filtradas)
            return datas_filtradas
        except Exception as e:
            error_msg = f"Erro ao carregar datas: {str(e)}"
            if HAS_STREAMLIT:
                st.error(error_msg)
            else:
                print(error_msg)
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
            error_msg = f"Erro ao carregar produtos da máquina {maquina}: {str(e)}"
            if HAS_STREAMLIT:
                st.error(error_msg)
            else:
                print(error_msg)
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
                self.limpar_cache()
                return True
            else:
                error_msg = f"Erro: {result.get('error', 'Erro desconhecido')}"
                if HAS_STREAMLIT:
                    st.error(error_msg)
                else:
                    print(error_msg)
                return False

        except Exception as e:
            error_msg = f"Erro ao adicionar produto: {str(e)}"
            if HAS_STREAMLIT:
                st.error(error_msg)
            else:
                print(error_msg)
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
                self.limpar_cache()
                return True
            else:
                error_msg = f"Erro: {result.get('error', 'Erro desconhecido')}"
                if HAS_STREAMLIT:
                    st.error(error_msg)
                else:
                    print(error_msg)
                return False

        except Exception as e:
            error_msg = f"Erro ao adicionar pedido: {str(e)}"
            if HAS_STREAMLIT:
                st.error(error_msg)
            else:
                print(error_msg)
            return False

    def limpar_cache(self):
        """Limpa o cache de dados"""
        self._cache = {}
        self._cache_time = {}
        if HAS_STREAMLIT:
            st.cache_data.clear()
