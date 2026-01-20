"""
Sistema de Extração de Dados da NHL com estruturas de dados personalizadas.
API Base: https://api-web.nhle.com/v1
"""
import requests
import pandas as pd
import time
from pathlib import Path
import os
from tqdm import tqdm

class SimpleNHLExtractor:
    def __init__(self):
        self.base_url = "https://api-web.nhle.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_player_data(self, player_id):
        """Busca dados de um jogador específico."""
        url = f"{self.base_url}/player/{player_id}/landing"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao buscar dados para o jogador {player_id}: {e}")
            return None

    def process_player_complete_data(self, player_data):
        """Processa todos os dados do jogador em uma única estrutura."""
        if not player_data:
            return []

        # Extraindo mais informações do jogador
        player_info = {
            'playerId': player_data.get('playerId'),
            'headshot': player_data.get('headshot'),
            'firstName': player_data.get('firstName', {}).get('default'),
            'lastName': player_data.get('lastName', {}).get('default'),
            'sweaterNumber': player_data.get('sweaterNumber'),
            'fullTeamName': player_data.get('fullTeamName', {}).get('default'),
            'currentTeamAbbrev': player_data.get('currentTeamAbbrev'),
            'teamLogo': player_data.get('teamLogo'),
            'position': player_data.get('position'),
            'season': player_data.get('featuredStats', {}).get('season'),
            'gamesPlayed': player_data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {}).get('gamesPlayed'),
            'points': player_data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {}).get('points'),
            'goals': player_data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {}).get('goals'),
            'assists': player_data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {}).get('assists'),
            'shots': player_data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {}).get('shots'),
            'shootingPctg': player_data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {}).get('shootingPctg'),
            'powerPlayGoals': player_data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {}).get('powerPlayGoals'),
            'powerPlayPoints': player_data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {}).get('powerPlayPoints')
        }

        return [player_info]

    def save_data(self, data, player_id):
        """Salva os dados em um arquivo CSV."""
        if not data:
            print(f"⚠️ Sem dados para salvar do jogador {player_id}")
            return

        df = pd.DataFrame(data)
        filename = f"nhl_player_{player_id}.csv"
        filepath = Path("data/player") / filename

        # Cria o diretório se não existir
        filepath.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(filepath, index=False, sep=';')
        print(f"✔️ Arquivo {filename} salvo com sucesso!")

    def combine_and_clean_player_csv(self, player_ids):
        """Combina os arquivos CSV dos jogadores e apaga os arquivos individuais."""
        df_list = []
        individual_files = []

        for player_id in player_ids:
            filepath = Path("data/player") / f"nhl_player_{player_id}.csv"

            if filepath.exists():
                try:
                    df = pd.read_csv(filepath, sep=';')
                    df_list.append(df)
                    individual_files.append(filepath)
                    print(f"📁 Arquivo {filepath.name} carregado para combinação.")
                except Exception as e:
                    print(f"❌ Erro ao ler {filepath}: {e}")
            else:
                print(f"⚠️ Arquivo {filepath.name} não encontrado.")

        if df_list:
            # Salva o arquivo combinado
            combined_df = pd.concat(df_list, ignore_index=True)
            combined_filepath = Path("data/player") / "nhl_player_all.csv"
            combined_df.to_csv(combined_filepath, index=False, sep=';')

            # Apaga os arquivos individuais
            files_deleted = 0
            for filepath in individual_files:
                try:
                    os.remove(filepath)
                    print(f"🗑️  Arquivo {filepath.name} removido.")
                    files_deleted += 1
                except Exception as e:
                    print(f"⚠️ Não foi possível remover {filepath.name}: {e}")

            print(f"\n✅ Arquivo combinado salvo como: {combined_filepath}")
            print(f"📊 Total de jogadores combinados: {len(df_list)}")
            print(f"🗑️  Arquivos individuais removidos: {files_deleted}/{len(individual_files)}")
        else:
            print("⚠️ Nenhum arquivo encontrado para combinar.")

def main():
    """Função principal para executar a extração."""
    print("=" * 50)
    print("🏒 NHL Data Extractor")
    print("=" * 50)

    # Lista de IDs dos jogadores

    IDS = pd.read_csv('data/player_id/nhl_standings_players_20252026_id.csv', sep=';')['playerId']

    player_ids = IDS.to_list()

    extractor = SimpleNHLExtractor()

    # Criar diretório de saída
    Path("data/player").mkdir(parents=True, exist_ok=True)

    # Extrair dados de cada jogador
    for player_id in tqdm(player_ids):
        print(f"\n📊 Processando jogador ID: {player_id}")
        print("-" * 30)

        data = extractor.fetch_player_data(player_id)
        if not data:
            continue

        player_records = extractor.process_player_complete_data(data)

        # Salva os dados individuais
        extractor.save_data(player_records, player_id)

        time.sleep(2)  # Respeita o limite da API

    # Combina todos os arquivos e remove os individuais
    print("\n" + "=" * 50)
    print("🔄 Combinando e limpando arquivos CSV...")
    print("=" * 50)
    extractor.combine_and_clean_player_csv(player_ids)

    print("\n" + "=" * 50)
    print("✅ Extração concluída com sucesso!")
    print("=" * 50)
    print(f"📍 Arquivo final: data/player/nhl_player_all.csv")
    print(f"📊 Total de jogadores: {len(player_ids)}")

if __name__ == "__main__":
    main()
