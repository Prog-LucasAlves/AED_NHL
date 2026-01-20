"""
Sistema de Extração de Dados da NHL com estruturas de dados personalidades.

API Base: https://api-web.nhle.com/v1
"""
import requests
import pandas as pd
import time
from datetime import datetime
from pathlib import Path

class SimpleNHLExtractor:
    def __init__(self):
        self.base_url = "https://api-web.nhle.com/v1"
        self.session = requests.Session()

    def fetch_season_data(self, date):
        """Busca dados de uma temporada específica."""

        url = f"{self.base_url}/standings/{date}"

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Erro ao buscar dados para a data {date}: {e}")
        return None

    def process_team_data(self, team):
        """processa dados de um time"""

        return {
            'team_logo': team.get('teamLogo'),
            'team_name': team.get('teamName', {}).get('default'),
            'gamesPlayed': team.get('gamesPlayed'),
            'wins': team.get('wins'),
            'losses': team.get('losses'),
            'otLosses' :team.get('otLosses'),
            'team_points': team.get('points'),
            'pointPctg': team.get('pointPctg'),
            'goalFor': team.get('goalFor'),
            'goalAgainst': team.get('goalAgainst'),
            #
            'homeGamesPlayed': team.get('homeGamesPlayed'),
            'homeWins': team.get('homeWins'),
            'homeLosses': team.get('homeLosses'),
            'homeOtLosses': team.get('homeOtLosses'),
            'homeGoalsFor': team.get('homeGoalsFor'),
            #
            'roadGamesPlayed': team.get('roadGamesPlayed'),
            'roadWins': team.get('roadWins'),
            'roadLosses': team.get('roadLosses'),
            'roadOtLosses': team.get('roadOtLosses'),
            'roadGoalsFor': team.get('roadGoalsFor'),

        }

    def save_data(self, data, season_id):
        """Salva os dados em um arquivo CSV."""

        if not data:
            print(f"Sem dados para salvar da temporada {season_id}")
            return

        df = pd.DataFrame(data)
        filename = f"nhl_standings_{season_id}.csv"
        filepath = Path("data/teams") / filename

        # Cria o diretório se não existir
        filepath.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(filepath, index=False, sep=';')
        print(f"✔️ {filepath} salvo ({len(data)} times).")

def main():
    """Função principal para executar a extração."""

    print("🏒 Extraindo dados da NHL...")

    dates = ['2022-05-01', '2023-04-14', '2024-04-18', '2025-04-17', datetime.now().strftime('%Y-%m-%d')]

    extractor = SimpleNHLExtractor()

    for date in dates:
        print(f"📅 Processando dados para a data: {date}")

        data = extractor.fetch_season_data(date)
        if not data:
            continue

        standings = data.get('standings', [])
        if not standings:
            print(f"Sem dados para a data: {date}")
            continue

        season_id = standings[0].get('seasonId', 'unknown')

        all_teams = []
        for team in standings:
            team_data = extractor.process_team_data(team)
            all_teams.append(team_data)

        # Salva os dados
        extractor.save_data(all_teams, season_id)

        time.sleep(1)  # Respeita o limite da API


if __name__ == "__main__":
    main()
