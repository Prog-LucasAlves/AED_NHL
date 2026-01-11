"""
App Streamlit para visualização de dados da NHL.
"""
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="NHL Data Dashboard",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #1E88E5;
    }
    .team-logo {
        max-width: 50px;
        max-height: 50px;
    }
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

class NHLDataApp:
    def __init__(self):
        self.data_dir = Path("data/teams")

    def load_data(self):
        """Carrega os dados dos times."""

        data_files = list(self.data_dir.glob("nhl_standings_*.csv"))
        all_data = {}

        for file_path in data_files:
            try:
                seasson = file_path.stem.replace('nhl_standings_', '')
                df = pd.read_csv(file_path, sep=';')
                all_data[seasson] = df
            except Exception as e:
                print(f"Erro ao carregar {file_path}: {e}")

        return all_data

def main():
    """Função principal para executar a aplicação Streamlit."""

    # Inicializa a aplicação
    app = NHLDataApp()

    # Título principal
    st.markdown("<h1 class='main-header'>🏒 NHL Data Dashboard</h1>", unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://media.d3.nhle.com/image/private/t_q-best/prd/assets/nhl/logos/nhl_shield_wm_on_dark_fqkbph", width=20)
        st.markdown("---")

        st.markdown("### 📊 Menu de Navegação")
