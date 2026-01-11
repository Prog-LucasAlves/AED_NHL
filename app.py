"""
App Streamlit para visualização de dados da NHL a partir de arquivos CSV.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64
from io import BytesIO

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
        margin-bottom: 10px;
    }
    .team-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px;
        color: white;
        margin-bottom: 10px;
    }
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .logo-img {
        max-width: 40px;
        max-height: 40px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

class NHLDataAnalyzer:
    def __init__(self):
        self.data_dir = Path("data/teams")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_all_data(self):
        """Carrega todos os dados dos arquivos CSV."""
        data_files = list(self.data_dir.glob("nhl_standings_*.csv"))
        all_data = {}

        for file_path in data_files:
            try:
                season = file_path.stem.replace("nhl_standings_", "")
                df = pd.read_csv(file_path, sep=';')

                # Adicionar coluna de temporada se não existir
                if 'season' not in df.columns:
                    df['season'] = season

                all_data[season] = df

            except Exception as e:
                print(f"Erro ao carregar {file_path}: {e}")


        return all_data

    def get_latest_season_data(self):
        """Obtém os dados da temporada mais recente."""

        all_data = self.load_all_data()
        if not all_data:
            return None

        # Ordenar temporadas e pegar a mais recente
        sorted_seasons = sorted(all_data.keys(), reverse=True)
        return all_data[sorted_seasons[0]]

    def merge_all_seasons(self):
        """Combina dados de todas as temporadas."""

        all_data = self.load_all_data()
        if not all_data:
            return pd.DataFrame()

        merged_df = pd.DataFrame()
        for season, df in all_data.items():
            df_copy = df.copy()
            df_copy['season'] = season
            merged_df = pd.concat([merged_df, df_copy], ignore_index=True)

        return merged_df

def create_download_link(df, filename):
    """Cria um link para download do DataFrame."""

    csv = df.to_csv(index=False, sep=';').encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Baixar CSV</a>'
    return href

def main():
    """Aplicativo principal Streamlit."""

    # Inicializar analisador
    analyzer = NHLDataAnalyzer()

    # Título principal
    st.markdown("<h1 class='main-header'>🏒 NHL Data Dashboard</h1>", unsafe_allow_html=True)

    # Sidebar com informações
    with st.sidebar:
        st.image("https://media.d3.nhle.com/image/private/t_q-best/prd/assets/nhl/logos/nhl_shield_wm_on_dark_fqkbph", width=200)
        st.markdown("---")

        st.markdown("### 📊 Menu de Navegação")
        page = st.radio(
            "Selecione a página:",
            ["🏠 Dashboard", "📋 Dados Completos", "📈 Análise Comparativa", "🔍 Detalhes dos Times"]
        )

        st.markdown("---")
        st.markdown("### 📁 Dados Carregados")

        # Carregar dados na sidebar
        with st.spinner("Carregando dados..."):
            all_data = analyzer.load_all_data()

        if all_data:
            total_teams = sum(len(df) for df in all_data.values())
            total_seasons = len(all_data)
            st.metric("Temporadas", total_seasons)
            st.metric("Registros", total_teams)

            # Listar arquivos
            with st.expander("Ver arquivos"):
                for season in sorted(all_data.keys(), reverse=True):
                    st.info(f"**{season}**: {len(all_data[season])} times")
        else:
            st.warning("Nenhum dado encontrado!")
            st.info("""
            Certifique-se de que existam arquivos no formato:
            `data/teams/nhl_standings_YYYYMMDD.csv`
            """)

        st.markdown("---")
        st.markdown(f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Página: Dashboard
    if page == "🏠 Dashboard":
        show_dashboard(analyzer)

    # Página: Dados Completos
    # elif page == "📋 Dados Completos":
        # show_complete_data(analyzer)

    # Página: Análise Comparativa
    # elif page == "📈 Análise Comparativa":
        # show_comparative_analysis(analyzer)

    # Página: Detalhes dos Times
    # elif page == "🔍 Detalhes dos Times":
        # show_team_details(analyzer)

def show_dashboard(analyzer):
    """Mostra o dashboard principal."""

    # carregar dados da temporada mais recente
    latest_data = analyzer.get_latest_season_data()

    if latest_data is None or latest_data.empty:
        st.warning("Nenhum dado disponível. Verifique os arquivos CSV.")
        return

    # Layout do dashboard
    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        st.markdown("<h2 class='sub-header'>📊 Classificação Atual</h2>", unsafe_allow_html=True)

        # Preparar dados para exibição
        display_df = latest_data.copy()

        # Ordernar por pontos
        if 'team_points' in display_df.columns:
            display_df.sort_values(by='team_points', ascending=False)

        # Resetar índice para posição
        display_df = display_df.reset_index(drop=True)
        display_df["posição"] = display_df.index + 1

        # Selecionar colunas para exibir
        columns_to_show = ['posição']

        # Adicionar colunas disponíveis
        for col in ['team_name']:
            if col in display_df.columns:
                columns_to_show.append(col)
                break

        # Adicionar colunas de estatísticas
        stat_cols = ['team_points']
        for col in stat_cols:
            if col in display_df.columns:
                columns_to_show.append(col)

        # Exibir tabela
        st.dataframe(
            display_df[columns_to_show],
            use_container_width=True,
            hide_index=True,
            column_config={
                'team_logo': st.column_config.ImageColumn("Logo", width="small")
            }
        )

if __name__ == "__main__":
    main()
