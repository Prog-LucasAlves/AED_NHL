"""
App Streamlit para visualização de dados da NHL a partir de arquivos CSV.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import base64

# Configuração da página
st.set_page_config(
    page_title="NHL Data Dashboard",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


class NHLDataAnalyzer:
    def __init__(self):
        self.data_dir_team = Path("data/teams")
        self.data_dir_team.mkdir(parents=True, exist_ok=True)

        self.data_dir_player = Path("data/player")
        self.data_dir_player.mkdir(parents=True, exist_ok=True)

    def load_all_data_team(self):
        """Carrega todos os dados dos arquivos CSV."""
        data_files = list(self.data_dir_team.glob("nhl_standings_*.csv"))
        all_data = {}

        for file_path in data_files:
            try:
                season = file_path.stem.replace("nhl_standings_", "")
                df = pd.read_csv(file_path, sep=";")

                # Adicionar coluna de temporada se não existir
                if "season" not in df.columns:
                    df["season"] = season

                all_data[season] = df

            except Exception as e:
                print(f"Erro ao carregar {file_path}: {e}")

        return all_data

    def load_all_data_player(self):
        """Carrega todos os dados dos arquivos CSV."""
        data_files = self.data_dir_player.glob("nhl_player_*.csv")

        for file_path in data_files:
            try:
                df = pd.read_csv(file_path, sep=";")
            except Exception as e:
                print(f"Erro ao carregar {file_path}: {e}")

        return df

    def get_latest_season_data(self):
        """Obtém os dados da temporada mais recente."""

        all_data = self.load_all_data_team()
        if not all_data:
            return None

        # Ordenar temporadas e pegar a mais recente
        sorted_seasons = sorted(all_data.keys(), reverse=True)
        return all_data[sorted_seasons[0]]

    def merge_all_seasons(self):
        """Combina dados de todas as temporadas."""

        all_data = self.load_all_data_team()
        if not all_data:
            return pd.DataFrame()

        merged_df = pd.DataFrame()
        for season, df in all_data.items():
            df_copy = df.copy()
            df_copy["season"] = season
            merged_df = pd.concat([merged_df, df_copy], ignore_index=True)

        return merged_df


def create_download_link(df, filename):
    """Cria um link para download do DataFrame."""

    csv = df.to_csv(index=False, sep=";").encode("utf-8")
    b64 = base64.b64encode(csv).decode()
    href = (
        f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Baixar CSV</a>'
    )
    return href


def main():
    """Aplicativo principal Streamlit."""

    # Inicializar analisador
    analyzer = NHLDataAnalyzer()

    # Título principal
    st.markdown(
        "<h1 class='main-header'>🏒 NHL Data Dashboard | Temporada Regular</h1>",
        unsafe_allow_html=True,
    )

    # Sidebar com informações
    with st.sidebar:
        st.image(
            "https://media.d3.nhle.com/image/private/t_q-best/prd/assets/nhl/logos/nhl_shield_wm_on_dark_fqkbph",
            width=200,
        )
        st.markdown("---")

        st.markdown("### 📊 Menu de Navegação")
        page = st.radio("Selecione a página:", ["📋 Dados Completos", "🏒 Jogadores"])

        st.markdown("---")
        st.markdown("### 📁 Dados Carregados")

        # Carregar dados na sidebar
        with st.spinner("Carregando dados..."):
            all_data = analyzer.load_all_data_team()

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
        st.markdown(
            f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )

    # Página: Dados Completos
    if page == "📋 Dados Completos":
        show_complete_data(analyzer)

    # Página: Dados Jogadores
    elif page == "🏒 Jogadores":
        show_player_data(analyzer)


def show_complete_data(analyzer):
    """Mostra todos os dados disponíveis."""

    st.markdown(
        "<h2 class='sub-header'>📋 Dados Completos das Temporadas</h2>",
        unsafe_allow_html=True,
    )

    all_data = analyzer.load_all_data_team()

    if not all_data:
        st.warning("Nenhum dado disponível. Verifique os arquivos CSV.")
        return

    # Seletor de temporada
    seasons = sorted(all_data.keys(), reverse=True)

    # seasons = [f"{season[:4]} - {season[4:]}" for season in seasons]
    st.markdown(
        """
    <style>
    .stSelectbox > div[data-baseweb="select"] > div {
        width: 200px;  /* ajuste a largura */
    }
    </style>
""",
        unsafe_allow_html=True,
    )
    selected_season = st.selectbox("Selecione a temporada:", seasons)

    if selected_season in all_data:
        df = all_data[selected_season]

        # Mostrar informações básicas
        col_info1, col_info2, col_info3 = st.columns(3)

        with col_info1:
            st.metric("Total de times:", len(df))

        with col_info2:
            if "gamesPlayed" in df.columns:
                games_played = df["gamesPlayed"].sum() / 2
                st.metric("Total de Jogos", f"{games_played:.0f}")

        with col_info3:
            if "goalFor" in df.columns:
                goals_for = df["goalFor"].sum()
                avg_games_played = (df["gamesPlayed"].mean() * 32) / 2
                avg_goals_for = goals_for / avg_games_played
                st.metric("Média de Gols Marcados", f"{avg_goals_for:.2f}")

        # Filtros interativos
        st.markdown("### 🔍 Filtros Avançados")

        col_filter1, col_filter2, col_filter3 = st.columns(3)

        # Filtrar por colunas especificas
        numeric_cols = [
            "wins",
            "losses",
            "otLosses",
            "team_points",
            "pointPctg",
            "goalFor",
            "goalAgainst",
        ]

        # Mapeamento de nomes legíveis
        display_names = {
            "wins": "Vitórias",
            "losses": "Derrotas",
            "otLosses": "Derrotas em OT",
            "team_points": "Pontos",
            "pointPctg": "Percentual de Pontos",
            "goalFor": "Gols Marcados",
            "goalAgainst": "Gols Sofridos",
        }

        with col_filter1:
            # Seleção de coluna para filtrar
            if numeric_cols:
                options = [display_names[col] for col in numeric_cols]
                selected_display = st.selectbox("Filtrar por:", options)
                filter_col = next(
                    key
                    for key, value in display_names.items()
                    if value == selected_display
                )

        with col_filter2:
            st.markdown(
                """
                <style>
                div[data-testid="stSlider"] {
                    max-width: 300px;
                }
                </style>
            """,
                unsafe_allow_html=True,
            )

            # Slider de valores
            if "filter_col" in locals():
                min_val = int(df[filter_col].min())
                max_val = int(df[filter_col].max())
                filter_range = st.slider(
                    f"Valores de {selected_display}",
                    min_val,
                    max_val,
                    (min_val, max_val),
                )

        with col_filter3:
            # Ordenação
            if numeric_cols:
                sort_options = {col: display_names[col] for col in numeric_cols}
                sort_display = st.selectbox(
                    "Ordenar por:", list(sort_options.values()), index=0
                )
                sort_col = next(
                    key for key, value in sort_options.items() if value == sort_display
                )
                sort_asc = st.checkbox("Ordem Crescente", value=False)

        # Aplicar filtros
        filtered_df = df.copy()

        if "filter_col" in locals() and "filter_range" in locals():
            filtered_df = filtered_df[
                (filtered_df[filter_col] >= filter_range[0])
                & (filtered_df[filter_col] <= filter_range[1])
            ]

        if "sort_col" in locals():
            filtered_df = filtered_df.sort_values(sort_col, ascending=sort_asc)

        # Exibir dados
        st.markdown(f"### 📊 Dados da Temporada {selected_season}")
        st.dataframe(
            filtered_df,
            width="content",
            hide_index=True,
            height=800,
            column_config={
                "team_logo": st.column_config.ImageColumn("Logo", width="small"),
                "team_name": st.column_config.TextColumn("Time", width="medium"),
            },
        )

        # Botões de ação
        col_action1 = st.columns(1)[0]

        with col_action1:
            st.markdown(
                create_download_link(filtered_df, f"nhl_data_{selected_season}.csv"),
                unsafe_allow_html=True,
            )


def show_player_data(analyzer):
    """Mostra dados dos jogadores."""
    # st.markdown("<h2>🥇 Estatísticas de Jogadores</h2>", unsafe_allow_html=True)

    # Carregar dados dos jogadores
    player_data = analyzer.load_all_data_player()

    if "assists" in player_data.columns:
        player_data["assists"] = pd.to_numeric(player_data["assists"], errors="coerce")
        player_data["goals"] = pd.to_numeric(player_data["goals"], errors="coerce")
        player_data["sweaterNumber"] = pd.to_numeric(
            player_data["sweaterNumber"], errors="coerce"
        )

        if not player_data["assists"].isnull().all():
            # Ordenar por assists
            player_data_assists = player_data.sort_values(by="assists", ascending=False)
            player_data_assists = player_data_assists.reset_index(drop=True)
            player_data_assists_top3 = player_data_assists.head(5)

            # Ordenar por goals
            player_data_goals = player_data.sort_values(by="goals", ascending=False)
            player_data_goals = player_data_goals.reset_index(drop=True)
            player_data_goals_top3 = player_data_goals.head(5)

            # Ordenar por points
            player_data_points = player_data.sort_values(by="points", ascending=False)
            player_data_points = player_data_points.reset_index(drop=True)
            player_data_points_top3 = player_data_points.head(5)

            # Layout de análise
            tab1, tab2, tab3 = st.tabs(["📊 2025-2026", "", ""])

            with tab1:
                st.markdown("### 📊 Dados dos Jogadores da Temporada 2025-2026")

                with st.container():
                    col1, col2, col3 = st.columns([1, 1, 1])

                    with col1:
                        st.markdown(
                            "<h2 style='font-size: 25px;'>🏆 ASSISTÊNCIAS</h2>",
                            unsafe_allow_html=True,
                        )

                        # PRIMEIRO LUGAR (🥇)
                        col_assists_img_1, col_assists_info_1 = st.columns([1, 1.5])

                        with col_assists_img_1:
                            st.markdown(
                                f"""
                                <div style="text-align: center;">
                                    <img src='{player_data_assists_top3['headshot'][0]}'
                                    style='width: 600px; height: 400px; border-radius: 8%;
                                    border: 2px solid white; object-fit: cover;'>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        with col_assists_info_1:
                            st.markdown(
                                f"""
                                <div style="padding-left: -20px; margin-bottom: -500px;">
                                <h1 style="margin-top: -30px; margin-bottom: -30px;">🥇</h1>
                                <h1 style='color: white; font-size: 28px; margin-bottom: -10px;'>{player_data_assists_top3['firstName'][0]} {player_data_assists_top3['lastName'][0]}</h1>
                                    <p style='font-size: 20px; margin: 0;'>
                                        <strong>Posição:</strong> {player_data_assists_top3['position'][0]}<br>
                                        <strong>Número:</strong> {player_data_assists_top3['sweaterNumber'][0]:.0f}<br>
                                        <strong>Jogos:</strong> {player_data_assists_top3['gamesPlayed'][0]}<br>
                                        <strong>Time:</strong> {player_data_assists_top3['fullTeamName'][0]}<br>
                                        <strong>Assistências:</strong> {player_data_assists_top3['assists'][0]}<br>
                                        <strong>Chutes:</strong> {player_data_assists_top3['shots'][0]}<br>
                                        <strong>Efficiência:</strong> {player_data_assists_top3['shootingPctg'][0]:.2f}%
                                    </p>
                                </div>
                        """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("<hr>", unsafe_allow_html=True)

                        # SEGUNDO LUGAR (🥈)
                        col_assists_img_2, col_assists_info_2 = st.columns([1, 1.5])

                        with col_assists_img_2:
                            st.markdown(
                                f"""
                                <div style="text-align: center;">
                                    <img src='{player_data_assists_top3['headshot'][1]}'
                                    style='width: 600px; height: 400px; border-radius: 8%;
                                    border: 2px solid white; object-fit: cover;'>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        with col_assists_info_2:
                            st.markdown(
                                f"""
                                <div style="padding-left: -20px; margin-bottom: -500px;">
                                <h1 style="margin-top: -30px; margin-bottom: -30px;">🥈</h1>
                                <h1 style='color: white; font-size: 28px; margin-bottom: -10px;'>{player_data_assists_top3['firstName'][1]} {player_data_assists_top3['lastName'][1]}</h1>
                                    <p style='font-size: 20px; margin: 0;'>
                                        <strong>Posição:</strong> {player_data_assists_top3['position'][1]}<br>
                                        <strong>Número:</strong> {player_data_assists_top3['sweaterNumber'][1]:.0f}<br>
                                        <strong>Jogos:</strong> {player_data_assists_top3['gamesPlayed'][1]}<br>
                                        <strong>Time:</strong> {player_data_assists_top3['fullTeamName'][1]}<br>
                                        <strong>Assistências:</strong> {player_data_assists_top3['assists'][1]}<br>
                                        <strong>Chutes:</strong> {player_data_assists_top3['shots'][1]}<br>
                                    </p>
                                </div>
                        """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("<hr>", unsafe_allow_html=True)

                        # TERCEIRO LUGAR (🥉)
                        col_assists_img_3, col_assists_info_3 = st.columns([1, 1.5])

                        with col_assists_img_3:
                            st.markdown(
                                f"""
                                <div style="text-align: center;">
                                    <img src='{player_data_assists_top3['headshot'][2]}'
                                    style='width: 600px; height: 400px; border-radius: 8%;
                                    border: 2px solid white; object-fit: cover;'>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        with col_assists_info_3:
                            st.markdown(
                                f"""
                                <div style="padding-left: -20px; margin-bottom: -500px;">
                                <h1 style="margin-top: -30px; margin-bottom: -30px;">🥉</h1>
                                <h1 style='color: white; font-size: 28px; margin-bottom: -10px;'>{player_data_assists_top3['firstName'][2]} {player_data_assists_top3['lastName'][2]}</h1>
                                    <p style='font-size: 20px; margin: 0;'>
                                        <strong>Posição:</strong> {player_data_assists_top3['position'][2]}<br>
                                        <strong>Número:</strong> {player_data_assists_top3['sweaterNumber'][2]:.0f}<br>
                                        <strong>Jogos:</strong> {player_data_assists_top3['gamesPlayed'][2]}<br>
                                        <strong>Time:</strong> {player_data_assists_top3['fullTeamName'][2]}<br>
                                        <strong>Assistências:</strong> {player_data_assists_top3['assists'][2]}<br>
                                        <strong>Chutes:</strong> {player_data_assists_top3['shots'][2]}<br>
                                    </p>
                                </div>
                        """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("<hr>", unsafe_allow_html=True)

                    with col2:
                        st.markdown(
                            "<h2 style='font-size: 25px;'>🏆 GOALS</h2>",
                            unsafe_allow_html=True,
                        )

                        # PRIMEIRO LUGAR (🥇)
                        col_goals_img_1, col_goals_info_1 = st.columns([1, 1.5])

                        with col_goals_img_1:
                            st.markdown(
                                f"""
                                <div style="text-align: center;">
                                    <img src='{player_data_goals_top3['headshot'][0]}'
                                    style='width: 600px; height: 400px; border-radius: 8%;
                                    border: 2px solid white; object-fit: cover;'>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        with col_goals_info_1:
                            st.markdown(
                                f"""
                                <div style="padding-left: -20px; margin-bottom: -500px;">
                                <h1 style="margin-top: -30px; margin-bottom: -30px;">🥇</h1>
                                <h1 style='color: white; font-size: 28px; margin-bottom: -10px;'>{player_data_goals_top3['firstName'][0]} {player_data_goals_top3['lastName'][0]}</h1>
                                    <p style='font-size: 20px; margin: 0;'>
                                        <strong>Posição:</strong> {player_data_goals_top3['position'][0]}<br>
                                        <strong>Número:</strong> {player_data_goals_top3['sweaterNumber'][0]:.0f}<br>
                                        <strong>Jogos:</strong> {player_data_goals_top3['gamesPlayed'][0]}<br>
                                        <strong>Time:</strong> {player_data_goals_top3['fullTeamName'][0]}<br>
                                        <strong>Goals:</strong> {player_data_goals_top3['goals'][0]}<br>
                                        <strong>Chutes:</strong> {player_data_goals_top3['shots'][0]}<br>
                                    </p>
                                </div>
                        """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("<hr>", unsafe_allow_html=True)

                        # SEGUNDO LUGAR (🥈)
                        col_goals_img_2, col_goals_info_2 = st.columns([1, 1.5])

                        with col_goals_img_2:
                            st.markdown(
                                f"""
                                <div style="text-align: center;">
                                    <img src='{player_data_goals_top3['headshot'][1]}'
                                    style='width: 600px; height: 400px; border-radius: 8%;
                                    border: 2px solid white; object-fit: cover;'>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        with col_goals_info_2:
                            st.markdown(
                                f"""
                                <div style="padding-left: -20px; margin-bottom: -500px;">
                                <h1 style="margin-top: -30px; margin-bottom: -30px;">🥈</h1>
                                <h1 style='color: white; font-size: 28px; margin-bottom: -10px;'>{player_data_goals_top3['firstName'][1]} {player_data_goals_top3['lastName'][1]}</h1>
                                    <p style='font-size: 20px; margin: 0;'>
                                        <strong>Posição:</strong> {player_data_goals_top3['position'][1]}<br>
                                        <strong>Número:</strong> {player_data_goals_top3['sweaterNumber'][1]:.0f}<br>
                                        <strong>Jogos:</strong> {player_data_goals_top3['gamesPlayed'][1]}<br>
                                        <strong>Time:</strong> {player_data_goals_top3['fullTeamName'][1]}<br>
                                        <strong>Goals:</strong> {player_data_goals_top3['goals'][1]}<br>
                                        <strong>Chutes:</strong> {player_data_goals_top3['shots'][1]}<br>
                                    </p>
                                </div>
                        """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("<hr>", unsafe_allow_html=True)

                        # TERCEIRO LUGAR (🥉)
                        col_goals_img_3, col_goals_info_3 = st.columns([1, 1.5])

                        with col_goals_img_3:
                            st.markdown(
                                f"""
                                <div style="text-align: center;">
                                    <img src='{player_data_goals_top3['headshot'][2]}'
                                    style='width: 600px; height: 400px; border-radius: 8%;
                                    border: 2px solid white; object-fit: cover;'>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        with col_goals_info_3:
                            st.markdown(
                                f"""
                                <div style="padding-left: -20px; margin-bottom: -500px;">
                                <h1 style="margin-top: -30px; margin-bottom: -30px;">🥉</h1>
                                <h1 style='color: white; font-size: 28px; margin-bottom: -10px;'>{player_data_goals_top3['firstName'][2]} {player_data_goals_top3['lastName'][2]}</h1>
                                    <p style='font-size: 20px; margin: 0;'>
                                        <strong>Posição:</strong> {player_data_goals_top3['position'][2]}<br>
                                        <strong>Número:</strong> {player_data_goals_top3['sweaterNumber'][2]:.0f}<br>
                                        <strong>Jogos:</strong> {player_data_goals_top3['gamesPlayed'][2]}<br>
                                        <strong>Time:</strong> {player_data_goals_top3['fullTeamName'][2]}<br>
                                        <strong>Goals:</strong> {player_data_goals_top3['goals'][2]}<br>
                                        <strong>Chutes:</strong> {player_data_goals_top3['shots'][2]}<br>
                                    </p>
                                </div>
                        """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("<hr>", unsafe_allow_html=True)

                    with col3:
                        st.markdown(
                            "<h2 style='font-size: 25px;'>🏆 PONTOS</h2>",
                            unsafe_allow_html=True,
                        )

                        # PRIMEIRO LUGAR (🥇)
                        col_points_img_1, col_points_info_1 = st.columns([1, 1.5])

                        with col_points_img_1:
                            st.markdown(
                                f"""
                                <div style="text-align: center;">
                                    <img src='{player_data_points_top3['headshot'][0]}'
                                    style='width: 600px; height: 400px; border-radius: 8%;
                                    border: 2px solid white; object-fit: cover;'>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        with col_points_info_1:
                            st.markdown(
                                f"""
                                <div style="padding-left: -20px; margin-bottom: -500px;">
                                <h1 style="margin-top: -30px; margin-bottom: -30px;">🥇</h1>
                                <h1 style='color: white; font-size: 28px; margin-bottom: -10px;'>{player_data_points_top3['firstName'][0]} {player_data_points_top3['lastName'][0]}</h1>
                                    <p style='font-size: 20px; margin: 0;'>
                                        <strong>Posição:</strong> {player_data_points_top3['position'][0]}<br>
                                        <strong>Número:</strong> {player_data_points_top3['sweaterNumber'][0]:.0f}<br>
                                        <strong>Jogos:</strong> {player_data_points_top3['gamesPlayed'][0]}<br>
                                        <strong>Time:</strong> {player_data_points_top3['fullTeamName'][0]}<br>
                                        <strong>Pontos:</strong> {player_data_points_top3['points'][0]}<br>
                                        <strong>Chutes:</strong> {player_data_points_top3['shots'][0]}<br>
                                    </p>
                                </div>
                        """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("<hr>", unsafe_allow_html=True)

                        # PRIMEIRO LUGAR (🥈)
                        col_points_img_2, col_points_info_2 = st.columns([1, 1.5])

                        with col_points_img_2:
                            st.markdown(
                                f"""
                                <div style="text-align: center;">
                                    <img src='{player_data_points_top3['headshot'][1]}'
                                    style='width: 600px; height: 400px; border-radius: 8%;
                                    border: 2px solid white; object-fit: cover;'>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        with col_points_info_2:
                            st.markdown(
                                f"""
                                <div style="padding-left: -20px; margin-bottom: -500px;">
                                <h1 style="margin-top: -30px; margin-bottom: -30px;">🥈</h1>
                                <h1 style='color: white; font-size: 28px; margin-bottom: -10px;'>{player_data_points_top3['firstName'][1]} {player_data_points_top3['lastName'][1]}</h1>
                                    <p style='font-size: 20px; margin: 0;'>
                                        <strong>Posição:</strong> {player_data_points_top3['position'][1]}<br>
                                        <strong>Número:</strong> {player_data_points_top3['sweaterNumber'][1]:.0f}<br>
                                        <strong>Jogos:</strong> {player_data_points_top3['gamesPlayed'][1]}<br>
                                        <strong>Time:</strong> {player_data_points_top3['fullTeamName'][1]}<br>
                                        <strong>Pontos:</strong> {player_data_points_top3['points'][1]}<br>
                                        <strong>Chutes:</strong> {player_data_points_top3['shots'][1]}<br>
                                    </p>
                                </div>
                        """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("<hr>", unsafe_allow_html=True)

                        # PRIMEIRO LUGAR (🥉)
                        col_points_img_3, col_points_info_3 = st.columns([1, 1.5])

                        with col_points_img_3:
                            st.markdown(
                                f"""
                                <div style="text-align: center;">
                                    <img src='{player_data_points_top3['headshot'][2]}'
                                    style='width: 600px; height: 400px; border-radius: 8%;
                                    border: 2px solid white; object-fit: cover;'>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        with col_points_info_3:
                            st.markdown(
                                f"""
                                <div style="padding-left: -20px; margin-bottom: -500px;">
                                <h1 style="margin-top: -30px; margin-bottom: -30px;">🥉</h1>
                                <h1 style='color: white; font-size: 28px; margin-bottom: -10px;'>{player_data_points_top3['firstName'][2]} {player_data_points_top3['lastName'][2]}</h1>
                                    <p style='font-size: 20px; margin: 0;'>
                                        <strong>Posição:</strong> {player_data_points_top3['position'][2]}<br>
                                        <strong>Número:</strong> {player_data_points_top3['sweaterNumber'][2]:.0f}<br>
                                        <strong>Jogos:</strong> {player_data_points_top3['gamesPlayed'][2]}<br>
                                        <strong>Time:</strong> {player_data_points_top3['fullTeamName'][2]}<br>
                                        <strong>Pontos:</strong> {player_data_points_top3['points'][2]}<br>
                                        <strong>Chutes:</strong> {player_data_points_top3['shots'][2]}<br>
                                    </p>
                                </div>
                        """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("<hr>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
