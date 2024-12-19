import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Arquivo de dados
ARQUIVO_DADOS= "registro_horas.csv"

# Função para carregar os dados
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS) and os.path.getsize(ARQUIVO_DADOS) > 0:

        dados = pd.read_csv(ARQUIVO_DADOS, parse_dates=["Data"])
        dados = dados.dropna(subset=["Data"])
        dados["Data"] = pd.to_datetime(dados["Data"], format="%Y-%m-%d", errors="coerce")

        return dados
    
    else:
        return pd.DataFrame(columns=["Data", "Atividade", "Horas Totais"])
    
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
dados = carregar_dados()

resumos = calcular_resumos(dados)

st.title("Análises Gráficas e Visualização de Dados")

if not dados.empty:

    # Gráfico de Horas por Dia
    dados_diarios = dados.groupby(dados["Data"].dt.date)["Horas Totais"].sum().reset_index()
    fig = px.bar(dados_diarios, x='Data', y='Horas Totais', labels={'Data': 'Data', 'Horas Totais': 'Horas'})
    fig.update_layout(title="Horas por Dia", xaxis_title="Data", yaxis_title="Horas")

    st.plotly_chart(fig)

    # Gráfico de Horas por Tipo de Atividade
    horas_por_atividade = dados.groupby("Atividade")["Horas Totais"].sum().reset_index()
    fig = px.bar(horas_por_atividade, x='Atividade', y='Horas Totais', labels={'Atividade': 'Tipo de Atividade', 'Horas Totais': 'Horas'})
    fig.update_layout(title="Horas por Tipo de Atividade", xaxis_title="Atividade", yaxis_title="Horas")

    st.plotly_chart(fig)

    # Gráfico Contínuo de Linha
    fig = px.line(dados_diarios, x='Data', y='Horas Totais', labels={'Data': 'Data', 'Horas Totais': 'Horas'})
    fig.update_layout(title="Horas Acumuladas por Data", xaxis_title="Data", yaxis_title="Horas")

    st.plotly_chart(fig)
else:
    st.info("Nenhum dado registrado ainda.")

st.sidebar.info("App beta desenvolvido para registrar e monitorar as horas totais dedicadas ao projeto 'TideSat - Streamlit'.")    