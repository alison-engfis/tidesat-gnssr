import pandas as pd
import streamlit as st
import requests
from io import StringIO
import plotly.express as px

# URL do arquivo CSV com os dados
url = "https://app.tidesatglobal.com/sph4/sph4_out.csv"

# Função para carregar os dados do link
@st.cache_data(ttl= 600)  # Cache por t = 10 min
def load_data():
    # Teste de request
    response = requests.get(url, verify= False, timeout= 10)
    
    if response.status_code == 200:
        dados_nivel = StringIO(response.text)
        df = pd.read_csv(dados_nivel, sep=',')
        
        df.rename(columns= {'% year': 'year', ' month': 'month', ' day': 'day', ' hour': 'hour', 
                           ' minute': 'minute', ' second (GMT/UTC)': 'second',
                           ' water level (meters)': 'water_level(m)'}, inplace= True)

        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])

        return df
    else:
        st.error("Erro ao acessar os dados.")
        return None

# Logo TideSat
st.image("TideSat_logo.webp", width= 200)

# Título
st.markdown("<h1 style= 'text-align: center; font-size: 30px;'>Monitore o nível da água onde quiser,acesse de onde estiver!</h1>", unsafe_allow_html= True)

# Carregar os dados
dados = load_data()

# Verificando se os dados foram carregados com êxito
if dados is not None:
    
    # Plot interativo
    fig = px.line(dados, x= 'datetime', y= 'water_level(m)', title= 'Dados da estação (SPH4) - Guaíba')
    fig.update_xaxes(title_text= 'Data')
    fig.update_yaxes(title_text= 'Nível (m)')

    # Tamanho das fontes
    fig.update_layout(
        title= {'font': {'size': 25}, 'x': 0.5, 'xanchor': 'center'},
        xaxis_title= {'font': {'size': 20}},
        yaxis_title= {'font': {'size': 20}},
        font= {'size': 18})

    # Gráfico interativo no Streamlit app
    st.plotly_chart(fig, use_container_width= True)
else:
    st.write("Falha ao carregar os dados.")
