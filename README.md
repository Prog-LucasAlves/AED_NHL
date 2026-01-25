# 🏒 Análise de Dados da NHL com Estruturas de Dados

![A](https://img.shields.io/badge/python-3.13+-blue.svg) ![B](https://img.shields.io/badge/license-MIT-green.svg) ![C](https://github.com/Prog-LucasAlves/AED_NHL/actions/workflows/extract.yml/badge.svg) ![D](https://img.shields.io/badge/Streamlit-1.52.2-FF4B4B) ![E](https://img.shields.io/badge/Deploy-Render-46B3E6)

![ ](https://github.com/Prog-LucasAlves/AED_NHL/blob/main/image/app.png?raw=true)

### 🚨 ***Projeto em Construção*** 🚨

### 📅 ***[Todo](https://github.com/Prog-LucasAlves/AED_NHL/blob/main/Todo)*** 📅

### ⏰ ***Atualizado em 25/01/2026***

---

## 📋 Índice
  - [📋 Índice](#-índice)
  - [🎯 Visão Geral](#-visão-geral)
  - [📁 Estrutura do Projeto](#-estrutura-do-projeto)
  - [📊 Arquivos Principais](#-arquivos-principais)
  - [🛠️ Configuração do Ambiente](#️-configuração-do-ambiente)
  - [🚀 Instalação Local](#-instalação-local)
  - [🖥️ API da NHL](#-api-da-nhl)
  - [🌐 Deploy na Render](#-deploy-na-render)
  - [🤝 Como Contribuir](#-como-contribuir)
  - [📄 Licença](#-licença)
  - [📚 Referências](#-referências)
  - [✨ Agradecimentos](#-agradecimentos)

## 🎯 Visão Geral

Este projeto realiza a extração, processamento e análise de dados da National Hockey League (NHL) utilizando estruturas de dados avançadas em Python. A aplicação final é uma dashboard interativa desenvolvida com Streamlit e implantada na Render.

## 📁 Estrutura do Projeto

```text
AED_NHL/
├── .gitignore              # Arquivos ignorados pelo git
├── pre.commit-config.yaml  # Configuração de hooks pré-commit
├── python-version          # Versão do Python usada
├── app.py                  # Aplicação principal com Streamlit
├── extract_player_id.py    # Extração de IDs de jogadores
├── extract_player.py       # Extração de dados dos jogadores
├── extract_team.py         # Extração de dados dos times
├── LICENSE                 # Licença MIT do projeto
├── pyproject.toml          # Dependências do projeto
├── README.md               # Descrição do projeto
├── uv.lock                 # Lockfile do UV (gerenciador de pacotes)
```

## 📊 Arquivos Principais

`app.py` - Aplicação Streamlit

Dashboard interativo que consome os dados extraídos e apresenta:

- Visualização de estatísticas de jogadores (Top 3)
- Filtros por temporada

`extract_player_id.py`

Módulo responsável por extrair e gerenciar os IDs únicos dos jogadores da NHL.

```python
def main():
    """Função principal para executar a extração."""

    print("🏒 Extraindo dados da NHL...")

    dates = ['20252026']

    extractor = SimpleNHLExtractor()

    for date in dates:
        print(f"📅 Processando dados para a data: {date}")

        data = extractor.fetch_season_data(date)
        if not data:
            continue

        standings = data.get('data', [])
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
```

`extract_player.py`

Extrai dados detalhados dos jogadores usando seus IDs:

- Informações biográficas
- Histórico de temporadas

`extract_team.py`

Coleta dados do times da NHL.

- Estatísticas do time
- Desempenho histórico

## 🛠️ Configuração do Ambiente

`pyproject.toml` - Dependências

```toml
[project]
name = "aed-nhl"
version = "0.1.0"
description = "Análise de dados da NHL com estruturas de dados"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "pandas>=2.3.3",
    "plotly>=6.5.1",
    "requests>=2.32.5",
    "streamlit>=1.52.2",
    "tqdm>=4.67.1",
]

[dependency-groups]
dev = [
    "pre-commit>=4.5.1",
]

[tool.poetry]
package-mode = false
```

`.gitignore`

Configura quais arquivos não devem ser versionados(Ambiente virtual, dados temporrários, configurações locais).

`pre-commit-config.yaml`

Hooks automatizados que rodam antes de cada commit para garantir a qualidade de código:

- Formatação com Black
- Organização de imports com isort
- Checagem de tipos com mypy

`python-version`

Especifica a versão exata do Python (3.13.5) para garantir consistência entre desenvolvedores.

`LICENSE`

Licença MIT que permite uso, modificação e distribuição do código com atribuição.

## 🚀 Instalação Local

1. Clone o repositório

```bash
git clone https://github.com/Prog-LucasAlves/AED_NHL.git
cd AED_NHL
```

2. Configuração do ambiente com **UV**

- [Getting started - UV](https://docs.astral.sh/uv/)

```bash
# Crie os arquivos iniciais
uv init

# Crie e ative o ambiente virtual
uv venv
source .venv/bin/activate #Linux/Mac
source .venv\Scripts\activate #Windows

# Instale as dependências
uv sync
```

3. Configure o pre-commit

```bash
pre-commit install
```

4. Execute a aplicação

```bash
streamlit run app.py
```

## 🖥️ API da NHL

Os módulos de extração utilizam a API pública da NHL:

- Base URL: **`https://api-web.nhle.com/v1`**

- **`/player/{player_id}/landing`** - Dados do Jogador
- **`/standings/{date}`** - Dados dos Times

## 🌐 Deploy na Render

**Configuração do Deploy**

1. Build Command: **`uv sync`**
2. Start Command: **`streamlit run app`**
3. Python Version(Environmen): **`3.13.5`**

![ ](https://github.com/Prog-LucasAlves/AED_NHL/blob/main/image/render.png?raw=true)

🔗 **Link do Deploy:** [https://aed-nhl.onrender.com/](https://aed-nhl.onrender.com/)

## 🤝 Como Contribuir

1. Faça fork do projeto
2. Crie uma branch: **`git checkout -b feature`**
3. Faça commit: **`git commit -m '...'`**
4. Push: **`git push origin feature`**
5. Abra um Pull Request 🔜 [AQUI](https://github.com/Prog-LucasAlves/AED_NHL/pulls)

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](https://github.com/Prog-LucasAlves/AED_NHL/blob/main/LICENSE) para detalhes.

## 📚 Referências

- [Documentação NHL API](https://github.com/Zmalski/NHL-API-Reference)
- [Documentação Streamli](https://docs.streamlit.io/)
- [Documentação Pandas](https://pandas.pydata.org/docs/)
- [Documentação Render](https://render.com/docs)

## ✨ Agradecimentos

- Dados fornecidos pela NHL API
- Comunidade Streamlit pelo framework incrível
- Render pela hospedagem gratuita para projetos open source

---
