import streamlit as st
import pandas as pd
import os
from datetime import datetime

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

        dados = pd.read_csv(csv, parse_dates=["Data"], dayfirst=True)
        dados = dados.dropna(subset=["Data"])
        dados["Data"] = pd.to_datetime(dados["Data"], format="%d-%m-%Y", errors="coerce")

        return dados
    else:
        return pd.DataFrame(columns=["Data", "Horário Inicial", "Horário Final", "Duração (h)", "Atividade"])

# Função para salvar os dados
def salvar_dados(dados, arquivo_csv):

    # Ajusta o formato da data para DD-MM-YYYY antes de salvar
    dados["Data"] = pd.to_datetime(dados["Data"], dayfirst=True).dt.strftime("%d-%m-%Y")

    dados.to_csv(arquivo_csv, index=False)

# Função para calcular resumos estatísticos
def calcular_resumos(dados):
    if dados.empty:
        return {
            "total_mes": 0,
            "total_semana": 0,
            "media_diaria": 0,
            "media_semanal": 0,
            "media_mensal": 0,
        }

    dados["Data"] = pd.to_datetime(dados["Data"])
    mes_atual = dados["Data"].dt.to_period("M").max()
    semana_atual = dados["Data"].dt.to_period("W").max()

    # Cálculos dos totais
    total_mes = dados[dados["Data"].dt.to_period("M") == mes_atual]["Duração (h)"].sum()
    total_semana = dados[dados["Data"].dt.to_period("W") == semana_atual]["Duração (h)"].sum()

    # Cálculos das médias
    media_diaria = dados.groupby("Data")["Duração (h)"].sum().mean()
    media_semanal = dados.groupby(dados["Data"].dt.to_period("W"))["Duração (h)"].sum().mean()
    media_mensal = dados.groupby(dados["Data"].dt.to_period("M"))["Duração (h)"].sum().mean()

    return {
        "total_mes": total_mes,
        "total_semana": total_semana,
        "media_diaria": media_diaria,
        "media_semanal": media_semanal,
        "media_mensal": media_mensal,
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
    horario_inicial = st.time_input("Horário Inicial")
    horario_final = st.time_input("Horário Final")
    atividade = st.selectbox("Atividade", atividades_recentes)

    registrar = st.form_submit_button("Registrar")
    
    if registrar:
        
        # Validação dos horários
        if horario_inicial >= horario_final:
            st.error("O horário inicial deve ser anterior ao horário final.")

        else:
            # Corrige o cálculo de duração em horas
            horario_inicio = datetime.combine(data, horario_inicial)
            horario_fim = datetime.combine(data, horario_final)

            # Validação: horário inicial deve ser anterior ao horário final
            if horario_inicio >= horario_fim:
                st.error("O horário inicial deve ser anterior ao horário final.")

            else:
                # Calcular a duração em horas
                duracao = (horario_fim - horario_inicio).total_seconds() / 3600

            # Cria nova entrada
            nova_entrada = pd.DataFrame({
                "Data": [data.strftime("%d-%m-%Y")],
                "Horário Inicial": [horario_inicio.strftime("%H:%M")],  # Salva apenas o horário
                "Horário Final": [horario_fim.strftime("%H:%M")],      # Salva apenas o horário
                "Duração (h)": [round(duracao, 2)],
                "Atividade": [atividade],
            })
            dados = pd.concat([dados, nova_entrada], ignore_index=True)
            salvar_dados(dados, ARQUIVO_DADOS)
            st.success("Registro salvo com sucesso!")
            st.rerun()


            st.success("Registro salvo com sucesso!")

# Exibe tabela com dados registrados
st.header("Dados Registrados")

if not dados.empty:
    # Cria uma cópia formatada para exibição
    dados_formatados = dados.copy()
    dados_formatados["Data"] = pd.to_datetime(dados_formatados["Data"], errors="coerce").dt.strftime("%d-%m-%Y")
    dados_formatados["Duração (h)"] = dados_formatados["Duração (h)"].round(2)  # Arredonda duração para 2 casas decimais

    # Exibe os dados formatados
    st.dataframe(dados_formatados)

    # Botão para download do CSV
    csv = dados.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Baixar dados como CSV",
        data=csv,
        file_name="registro_horas.csv",
        mime="text/csv",
    )
else:
    st.info("Nenhum dado registrado ainda.")

st.sidebar.info("App beta desenvolvido para registrar e monitorar as horas totais dedicadas ao projeto 'TideSat - Streamlit'.")            