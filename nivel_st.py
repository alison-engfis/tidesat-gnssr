import pandas as pd
import streamlit as st
import requests
from io import StringIO
import plotly.express as px
from datetime import datetime, timedelta

# Dicionário de URLs das estações
urls = {
    "SPH4 - Guaíba (Mauá)": "https://app.tidesatglobal.com/sph4/sph4_out.csv",
    "VDS1 - Guaíba (Vila Assunção)": "https://app.tidesatglobal.com/vds1/vds1_out.csv",
    "IDP1 - Guaíba (Arquipélago)": "https://app.tidesatglobal.com/idp1/idp1_out.csv",
    "ITA1 - Guaíba (Farol de Itapuã)": "https://app.tidesatglobal.com/ita1/ita1_out.csv"
}

# Função para carregar os dados dos links
@st.cache_data(ttl=600)  # Cache por 10 minutos
def load_data(url):
    resposta = requests.get(url, verify=False, timeout=10)
    
    if resposta.status_code == 200:
        dados_nivel = StringIO(resposta.text)
        df = pd.read_csv(dados_nivel, sep=',')
        
        # Renomeando as colunas
        df.rename(columns={
            '% year': 'year', ' month': 'month', ' day': 'day', 
            ' hour': 'hour', ' minute': 'minute', ' second (GMT/UTC)': 'second',
            ' water level (meters)': 'water_level(m)'}, inplace=True)

        # Criando a coluna datetime
        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])

        return df
    else:
        st.error("Erro ao acessar os dados.")
        return None

# Função para filtrar os dados pelo período selecionado
def filtrar_dados(df, dados_inicio, dados_fim):
    dados_inicio = pd.to_datetime(dados_inicio)
    dados_fim = pd.to_datetime(dados_fim) + timedelta(days=1)  # Incluso o fim do dia selecionado
    mascara = (df['datetime'] >= dados_inicio) & (df['datetime'] < dados_fim)
    return df.loc[mascara]

# Logo TideSat
st.image("TideSat_logo.webp", width=200)

# Título
st.markdown("<h1 style='text-align: center; font-size: 25px;'>Monitore o nível da água onde quiser, acesse de onde estiver!</h1>", unsafe_allow_html=True)

# Espaços (deve ter um jeito mais eficiente)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Seletor de estações
estacao_selecionada = st.selectbox("Selecione a estação de medição", list(urls.keys()))

st.markdown("<br>", unsafe_allow_html=True)

# URL da estação selecionada
url_estacao = urls[estacao_selecionada]

# Carregando os dados da estação selecionada
dados = load_data(url_estacao)

# Verificando se os dados foram carregados com êxito
if dados is not None:

    st.write(f"FILTRO DE PERÍODO: {estacao_selecionada}")

    # Dividindo a tela em duas colunas para os seletores de período
    col1, col2 = st.columns([1, 1])  # Proporção ajustada para os seletores

    with col1:
        dados_inicio = st.date_input("Data de início", datetime.now().date() - timedelta(days=7))
    
    with col2:
        dados_fim = st.date_input("Data de fim", datetime.now().date())

    # Criando colunas para os botões
    col3, col4, col5 = st.columns([1, 1, 1])  # Três colunas com espaço igual

    with col3:
        if st.button("Período completo"):
            dados_inicio = dados['datetime'].min().date()
            dados_fim = dados['datetime'].max().date()

    with col4:
        if st.button("Últimos 7 dias"):
            dados_inicio = datetime.now().date() - timedelta(days=7)
            dados_fim = datetime.now().date()

    with col5:
        if st.button("Dia atual"):
            dados_inicio = datetime.now().date()
            dados_fim = datetime.now().date()

    # Espaços
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Filtrar os dados de acordo com o período selecionado
    dados_filtrados = filtrar_dados(dados, dados_inicio, dados_fim)

    # Gráfico interativo
    if not dados_filtrados.empty:
        fig = px.line(dados_filtrados, x='datetime', y='water_level(m)', title=f'Dados da estação {estacao_selecionada}')
        fig.update_xaxes(title_text='Data')
        fig.update_yaxes(title_text='Nível (m)')

        # Tamanho das fontes e margens
        fig.update_layout(
            title={'text': f'Dados da estação {estacao_selecionada}', 'font': {'size': 25}, 'xanchor': 'center', 'x': 0.5},  # Título centralizado
            xaxis_title={'font': {'size': 20}},
            yaxis_title={'font': {'size': 20}},
            font={'size': 18},
            height=450,
            width=1000,
            margin=dict(l=40, r=0.1, t=40, b=40)  # Margens
        )

        # Gráfico em largura máxima
        st.plotly_chart(fig, use_container_width=True)

        # Nível atual e data/hora da medição
        nivel_atual = dados_filtrados.iloc[-1]['water_level(m)']
        data_hora_atual = dados_filtrados.iloc[-1]['datetime'].strftime('%Y-%m-%d %H:%M:%S')
        
        st.markdown(f"<h3 style='text-align: center;'>Nível atual: <span style='color: lightblue;'>{nivel_atual:.2f} m</span></h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: white;'>Medido em: {data_hora_atual}</h4>", unsafe_allow_html=True)

    else:
        st.write(f"Nenhum dado encontrado para o período selecionado na estação {estacao_selecionada}.")
else:
    st.write(f"Falha ao carregar os dados da estação {estacao_selecionada}.")
