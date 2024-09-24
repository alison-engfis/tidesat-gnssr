import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

@st.cache  # Cache para evitar recarregamento dos dados em cada interação

def load_data():
    
    # Carregar os dados (ajustando o necessário)

    df = pd.read_csv('sph4_out.csv', sep= ',')

    df.rename(columns= {'% year' : 'year', ' month' : 'month', ' day' : 'day', ' hour' : 'hour', ' minute' : 'minute', ' second (GMT/UTC)' : 'second', 
                        ' water level (meters)' : 'water_level(m)'}, inplace= True)
    
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])

    return df

# Título
st.title("Monitoramento do Nível do Rio Guaíba")

# Carregar os dados
data = load_data()

# Tabela contendo os dados
st.write("Dados de Nível de Água:")
st.dataframe(data[['datetime', 'water_level(m)']])

# Plot
st.write("Gráfico do Nível de Água ao Longo do Tempo:")
fig, ax = plt.subplots(figsize= (12, 6))
ax.plot(data['datetime'], data['water_level(m)'], linestyle= '-')
ax.set_xlabel('Data e Hora')
ax.set_ylabel('Nível da Água (metros)')
ax.set_title('Nível do Rio Guaíba ao Longo do Tempo')
plt.xticks(rotation= 45)
plt.grid(True)

# Gráfico no Streamlit
st.pyplot(fig)
