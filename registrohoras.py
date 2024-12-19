import streamlit as st
import pandas as pd
import os

# Arquivo de dados
ARQUIVO_DADOS = "dados/registro_horas.csv"

atividades_recentes = [
    "Configurações e funções genéricas",
    "Cotas notáveis",
    "Fotos e mapa",
    "Modo claro/escuro",
    "Prévia para compartilhamento",
    "Segregar exibição",
    "TideSat-Estrela",
    "Zoom restrito",
]

# Função para carregar os dados
def carregar_dados(arquivo_csv):

    csv = arquivo_csv

    if os.path.exists(csv) and os.path.getsize(csv) > 0:

        dados = pd.read_csv(csv, parse_dates=["Data"])
        dados = dados.dropna(subset=["Data"])
        dados["Data"] = pd.to_datetime(dados["Data"], format="%Y-%m-%d", errors="coerce")

        return dados
    else:
        return pd.DataFrame(columns=["Data", "Atividade", "Horas Totais"])

# Função para salvar os dados
def salvar_dados(dados):

    dados.to_csv(ARQUIVO_DADOS, index=False)

# Função para calcular resumos estatísticos
def calcular_resumos(dados):

    # Remove as linhas com dados inválidos
    dados = dados.dropna(subset=["Data"])
    
    if dados.empty:
        return {
            "total_mes": 0,
            "total_semana": 0,
            "media_diaria": 0,
            "media_semanal": 0,
            "media_mensal": 0
        }

    dados["Data"] = pd.to_datetime(dados["Data"])

    mes_atual = dados["Data"].dt.to_period("M").max()
    semana_atual = dados["Data"].dt.to_period("W").max()

    total_mes = dados[dados["Data"].dt.to_period("M") == mes_atual]["Horas Totais"].sum()
    total_semana = dados[dados["Data"].dt.to_period("W") == semana_atual]["Horas Totais"].sum()

    media_diaria = dados.groupby("Data")["Horas Totais"].sum().mean()
    media_semanal = dados.groupby(dados["Data"].dt.to_period("W"))["Horas Totais"].sum().mean()
    media_mensal = dados.groupby(dados["Data"].dt.to_period("M"))["Horas Totais"].sum().mean()

    return {
        "total_mes": total_mes,
        "total_semana": total_semana,
        "media_diaria": media_diaria,
        "media_semanal": media_semanal,
        "media_mensal": media_mensal
    }      

# Carrega os dados existentes
dados = carregar_dados(ARQUIVO_DADOS)
resumos = calcular_resumos(dados)

# Exibição breve de alguns resumos estatísticos na barra lateral
st.sidebar.markdown("## Resumo Atual")
st.sidebar.metric("Horas no Mês Atual", f"{resumos['total_mes']:.2f} h")
st.sidebar.metric("Horas na Semana Atual", f"{resumos['total_semana']:.2f} h")
st.sidebar.metric("Média de Horas Diárias", f"{resumos['media_diaria']:.2f} h")
st.sidebar.metric("Média de Horas Semanais", f"{resumos['media_semanal']:.2f} h")
st.sidebar.metric("Média de Horas Mensais", f"{resumos['media_mensal']:.2f} h")

st.title("Registro de Horas Totais")

# Formulário para registrar horas totais
with st.form("register_form"):

    data = st.date_input("Data")
    atividade = st.selectbox("Atividade", atividades_recentes)
    horas = st.number_input("Horas Totais", min_value=0.0, step=0.5)

    registrar = st.form_submit_button("Registrar")
    
    if registrar:

        if atividade and horas > 0:

            nova_entrada = pd.DataFrame({
                "Data": [pd.to_datetime(data, format="%Y-%m-%d")],
                "Atividade": [atividade],
                "Horas Totais": [horas]
            })
            dados = pd.concat([dados, nova_entrada], ignore_index=True)
            salvar_dados(dados)
            st.rerun()

            st.success("Registro salvo com sucesso!")
        else:
            
            st.error("Por favor, preencha todos os campos corretamente.")

st.sidebar.info("App beta desenvolvido para registrar e monitorar as horas totais dedicadas ao projeto 'TideSat - Streamlit'.")            