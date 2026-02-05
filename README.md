# TideSat Monitor - Personal Dashboard

Este repositório contém a versão pessoal e modular da plataforma TideSat, desenvolvida para o monitoramento e análise de dados hidrológicos. O projeto aplica o rigor da Engenharia Física em uma arquitetura Full Stack Python, com foco em escalabilidade, automação via DevOps e visualização geoespacial avançada.

## 🚀 Destaques Técnicos
Arquitetura Modular: Separação clara entre lógica de interface (main.py), configurações de instância (main_config.py) e utilitários de backend (tools.py).

- DevOps Ready: Configurado com .devcontainer para ambientes de desenvolvimento padronizados e preparado para deploy via app.yaml.

- Multi-language Support: Sistema de internacionalização integrado via language.py.

- Monitoramento Ativo: Script pinger.py para verificação de conectividade e integridade de fontes de dados.

## 🛠️ Stack Tecnológica
- Frontend: Streamlit (Python)

- Análise de Dados: Pandas, NumPy, SciPy

- Visualização: Plotly, Folium, Pydeck

- Infraestrutura: Docker, Bash, YAML (Google Cloud/App Engine)

## 📂 Estrutura do Projeto
```bash
.
├── .devcontainer/       # Configuração de container para desenvolvimento isolado
├── dados/               # Armazenamento local de datasets (CSV/Parquet)
├── main.py              # Ponto de entrada da aplicação Streamlit
├── main_config.py       # Definições de estações, URLs (CSV) e fuso horário
├── tools.py             # Core: Carregamento (Pandas/Requests), Plotly e Mapas
├── language.py          # Gestão de múltiplos idiomas para a interface
├── pinger.py            # Ferramenta de monitoramento de conectividade
└── requirements.txt     # Dependências do ecossistema Python
