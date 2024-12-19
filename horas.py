import streamlit as st
import pandas as pd
import os

# Configuração da pagina
st.set_page_config(page_title="Registro de Horas", layout="centered", initial_sidebar_state="collapsed")

# Nome do arquivo de dados
DATA_FILE = "registro_horas.csv"

# Função para carregar os dados
def carregar_dados():
    if os.path.exists(DATA_FILE):

        return pd.read_csv(DATA_FILE)
    
    return pd.DataFrame(columns=["Data", "Atividade", "Horas Totais"])

# Função para salvar os dados
def salvar_dados(dados):
    dados.to_csv(DATA_FILE, index=False)

# Função para calcular resumos estatísticos
def calcular_resumos(dados):
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
    semana_atual = dados["Data"].dt.to_period("S").max()

    total_mes = dados[dados["Data"].dt.to_period("M") == mes_atual]["Horas Totais"].sum()
    total_semana = dados[dados["Data"].dt.to_period("S") == semana_atual]["Horas Totais"].sum()

    media_diaria = dados.groupby("Data")["Horas Totais"].sum().mean()
    media_semanal = dados.groupby(dados["Data"].dt.to_period("S"))["Horas Totais"].sum().mean()
    media_mensal = dados.groupby(dados["Data"].dt.to_period("M"))["Horas Totais"].sum().mean()

    return {
        "total_mes": total_mes,
        "total_semana": total_semana,
        "media_diaria": media_diaria,
        "media_semanal": media_semanal,
        "media_mensal": media_mensal
    }

# Carregar dados existentes
dados = carregar_dados()
resumos = calcular_resumos(dados)

# Aba de navegação
menu = st.sidebar.selectbox("Menu", ["Registrar Horas", "Visualizar Dados", "Análises Gráficas"])

# Exibição breve de resumos estatísticos na barra lateral
st.sidebar.markdown("## Resumo Atual")
st.sidebar.metric("Horas no Mês Atual", f"{resumos['total_mes']:.2f} h")
st.sidebar.metric("Horas na Semana Atual", f"{resumos['total_semana']:.2f} h")
st.sidebar.metric("Média de Horas Diárias", f"{resumos['media_diaria']:.2f} h")
st.sidebar.metric("Média de Horas Semanais", f"{resumos['media_semanal']:.2f} h")
st.sidebar.metric("Média de Horas Mensais", f"{resumos['media_mensal']:.2f} h")

if menu == "Registrar Horas":
    st.header("Registrar Horas Totais")

    # Formulário para registrar horas totais

    with st.form("register_form"):

        data = st.date_input("Data")
        atividade = st.text_input("Atividade")
        horas = st.number_input("Horas Totais", min_value=0.0, step=0.5)
        registrar = st.form_submit_button("Registrar")

        if registrar:
            if atividade and horas > 0:

                nova_entrada = pd.DataFrame({
                    "Data": [data],
                    "Atividade": [atividade],
                    "Horas Totais": [horas]
                })
                data = pd.concat([dados, nova_entrada], ignore_index=True)
                salvar_dados(dados)
                resumos = calcular_resumos(dados)
                st.success("Registro salvo com sucesso!")
            else:
                st.error("Por favor, preencha todos os campos corretamente.")

elif menu == "Visualizar Dados":
    st.header("Visualizar Dados")

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

elif menu == "Análises Gráficas":
    st.header("Análises Gráficas")

    if not dados.empty:
        # Converter "Data" para o formato datetime
        dados["Data"] = pd.to_datetime(dados["Data"])

        # Total de horas por semana
        dados["Semana"] = dados["Data"].dt.to_period("S").astype(str)
        horas_semanais = dados.groupby("Semana")["Horas Totais"].sum()

        # Gráfico de barras
        st.bar_chart(horas_semanais, use_container_width=True)

        # Total acumulado de horas
        horas_totais = dados["Horas Totais"].sum()
        st.metric("Total de Horas Registradas", f"{horas_totais:.2f} horas")
    else:
        st.info("Nenhum dado registrado para análise.")

st.sidebar.info("App beta desenvolvido para registrar e monitorar as horas totais dedicadas ao projeto 'TideSat - Streamlit'.")