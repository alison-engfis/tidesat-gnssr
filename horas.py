import streamlit as st
import pandas as pd
import os
import plotly.express as px
import requests

# Configuração da página
st.set_page_config(
    page_title="Registro de Horas", 
    layout="centered", 
    initial_sidebar_state="collapsed",
    menu_items={
        'Get help': None,  # Remove o item de ajuda
        'Report a Bug': None,  # Remove a opção "Reportar um bug"
        'About': None  # Remove a opção "Sobre"
    }
)

# Reduz a margem superior da página
st.markdown(
    """
    <style>
        .main {
            margin-top: -69px;
        }
    </style>
    """,
    unsafe_allow_html=True)

# Arquivo de dados
DATA_FILE = "registro_horas.csv"

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

    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:

        try:
            # Carrega os dados e garante que a coluna "Data" seja interpretada corretamente
            dados = pd.read_csv(DATA_FILE, parse_dates=["Data"])

            # Remove as possíveis linhas com data em branco
            dados = dados.dropna(subset=["Data"])

            # Garante que as datas sejam convertidas corretamente
            dados["Data"] = pd.to_datetime(dados["Data"], format="%Y-%m-%d", errors="coerce")

            return dados
        
        except pd.errors.EmptyDataError:

            st.warning(f"O arquivo {DATA_FILE} está vazio.")

            return pd.DataFrame(columns=["Data", "Atividade", "Horas Totais"])
    else:
        return pd.DataFrame(columns=["Data", "Atividade", "Horas Totais"])

# Função para salvar os dados
def salvar_dados(dados):
    dados.to_csv(DATA_FILE, index=False)

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


menu = st.sidebar.selectbox("Menu", ["Registrar Horas", "Visualizar Dados", "Análises Gráficas"])

# Exibição breve de alguns resumos estatísticos na barra lateral
st.sidebar.markdown("## Resumo Atual")
st.sidebar.metric("Horas no Mês Atual", f"{resumos['total_mes']:.2f} h")
st.sidebar.metric("Horas na Semana Atual", f"{resumos['total_semana']:.2f} h")
st.sidebar.metric("Média de Horas Diárias", f"{resumos['media_diaria']:.2f} h")
st.sidebar.metric("Média de Horas Semanais", f"{resumos['media_semanal']:.2f} h")
st.sidebar.metric("Média de Horas Mensais", f"{resumos['media_mensal']:.2f} h")

if menu == "Registrar Horas":
    st.header("Registro de Horas Totais")

    # Formulário para registrar horas totais

    with st.form("register_form"):

        data = st.date_input("Data")
        atividade = st.selectbox("Atividade", atividades_recentes)
        horas = st.number_input("Horas Totais", min_value=0.0, step=0.5)
        registrar = st.form_submit_button("Registrar")

        if registrar:
            if atividade and horas > 0:
                
                nova_entrada = pd.DataFrame({
                    "Data": [pd.to_datetime(data, format="%Y-%m-%d")],  # Garante o formato correto (tive problemas nisso)
                    "Atividade": [atividade],
                    "Horas Totais": [horas]
                })
                
                dados = pd.concat([dados, nova_entrada], ignore_index=True)

                # Salva os dados atualizados no CSV
                salvar_dados(dados)

                # Força o Streamlit a recalcular as métricas

                st.rerun()  # Isso faz o app "reiniciar", atualizando então as métricas

                st.success("Registro salvo com sucesso!")
            else:
                st.error("Por favor, preencha todos os campos corretamente.")

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

elif menu == "Análises Gráficas":

    st.header("Análises Gráficas")

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico de Horas por Dia
    if not dados.empty:
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

st.sidebar.info("App beta desenvolvido para registrar e monitorar as horas totais dedicadas ao projeto 'TideSat - Streamlit'.")