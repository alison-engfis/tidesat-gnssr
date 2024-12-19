import streamlit as st
import pandas as pd
import plotly.express as px
import os

from registrohoras import ARQUIVO_DADOS

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

menu = st.sidebar.selectbox("Menu", ["Análises Gráficas", "Visualizar Dados", ])

# Exibição breve de alguns resumos estatísticos na barra lateral
st.sidebar.markdown("## Resumo Atual")
st.sidebar.metric("Horas no Mês Atual", f"{resumos['total_mes']:.2f} h")
st.sidebar.metric("Horas na Semana Atual", f"{resumos['total_semana']:.2f} h")
st.sidebar.metric("Média de Horas Diárias", f"{resumos['media_diaria']:.2f} h")
st.sidebar.metric("Média de Horas Semanais", f"{resumos['media_semanal']:.2f} h")
st.sidebar.metric("Média de Horas Mensais", f"{resumos['media_mensal']:.2f} h")

if not dados.empty:

    if menu == "Análises Gráficas":

        st.header("Análises Gráficas")

        st.markdown("<br>", unsafe_allow_html=True)

        dados_diarios = dados.groupby(dados["Data"].dt.date)["Horas Totais"].sum().reset_index()

        fig = px.bar(dados_diarios, x='Data', y='Horas Totais', labels={'Data': 'Data', 'Horas Totais': 'Horas'})
        fig.update_layout(title="Horas por Dia", xaxis_title="Data", yaxis_title="Horas")
        st.plotly_chart(fig)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico de Horas por Tipo de Atividade
        horas_por_atividade = dados.groupby("Atividade")["Horas Totais"].sum().reset_index()

        fig = px.bar(horas_por_atividade, x='Atividade', y='Horas Totais', labels={'Atividade': 'Tipo de Atividade', 'Horas Totais': 'Horas'})
        fig.update_layout(title="Horas por Tipo de Atividade", xaxis_title="Atividade", yaxis_title="Horas")
        st.plotly_chart(fig)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico Contínuo de Linha
        fig = px.line(dados_diarios, x='Data', y='Horas Totais', labels={'Data': 'Data', 'Horas Totais': 'Horas'})
        fig.update_layout(title="Horas Acumuladas por Data", xaxis_title="Data", yaxis_title="Horas")
        st.plotly_chart(fig)

    elif menu == "Visualizar Dados":
        st.header("Dados")

        if not dados.empty:
            st.dataframe(dados)
            
            # Botão para download do CSV
            csv = dados.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar dados como CSV",
                data=csv,
                file_name="horas_totais.csv",
                mime="text/csv",
            )
        else:
            st.info("Nenhum dado registrado ainda.")

st.sidebar.info("App beta desenvolvido para registrar e monitorar as horas totais dedicadas ao projeto 'TideSat - Streamlit'.")