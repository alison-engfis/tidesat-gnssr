import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import requests
from io import StringIO

# URL do arquivo CSV com os dados
url = "https://app.tidesatglobal.com/sph4/sph4_out.csv"

# Função para carregar os dados do link externo
@st.cache_data(ttl= 600)  # Cache por t = 10 min
def load_data():
    
    # Teste de request
    response = requests.get(url, verify= False, timeout= 10)
    
    if response.status_code == 200:

        dados_nivel = StringIO(response.text)
        df = pd.read_csv(dados_nivel, sep= ',')
        
        df.rename(columns= {'% year': 'year', ' month': 'month', ' day': 'day', ' hour': 'hour', 
                           ' minute': 'minute', ' second (GMT/UTC)': 'second',
                           ' water level (meters)': 'water_level(m)'}, inplace= True)

        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])

        return df
    else:
        st.error("Erro ao acessar os dados.")
        return None

# Título
st.title("Monitoramento do Nível do Guaíba")

# Carregar os dados
dados = load_data()

# Verificando se os dados foram carregados com êxito
if dados is not None:

    # Tabela de dados
    st.write("Dados de Nível:")
    st.dataframe(dados[['datetime', 'water_level(m)']])

    # Plot
    st.write("Gráfico do Nível da Água ao Longo do Tempo:")
    fig, ax = plt.subplots(figsize= (14, 6))
    ax.plot(dados['datetime'], dados['water_level(m)'], linestyle= '-')
    ax.set_xlabel('Data')
    ax.set_ylabel('Nível (m)')
    ax.set_title('Nível do Guaíba ao Longo do Tempo')
    plt.xticks(rotation= 45)
    plt.grid(True)

    # Gráfico no app Streamlit
    st.pyplot(fig)
else:
    st.write("Falha ao carregar os dados.")
