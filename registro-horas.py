import streamlit as st
import pandas as pd
import os

# Arquivo de dados
ARQUIVO_DADOS = "registro_horas.csv"

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
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS) and os.path.getsize(ARQUIVO_DADOS) > 0:

        dados = pd.read_csv(ARQUIVO_DADOS, parse_dates=["Data"])
        dados = dados.dropna(subset=["Data"])
        dados["Data"] = pd.to_datetime(dados["Data"], format="%Y-%m-%d", errors="coerce")

        return dados
    else:
        return pd.DataFrame(columns=["Data", "Atividade", "Horas Totais"])

# Função para salvar os dados
def salvar_dados(dados):
    dados.to_csv(ARQUIVO_DADOS, index=False)  

# Carrega os dados existentes
dados = carregar_dados()

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

            st.success("Registro salvo com sucesso!")
        else:
            
            st.error("Por favor, preencha todos os campos corretamente.")

st.sidebar.info("App beta desenvolvido para registrar e monitorar as horas totais dedicadas ao projeto 'TideSat - Streamlit'.")            