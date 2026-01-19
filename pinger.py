import requests
import time
import random

URLS = [
    "https://tidesat.streamlit.app/",
    "https://tidesat2.streamlit.app/",
    "https://tidesat3.streamlit.app/",
    "https://tidesat-all.streamlit.app/",
    "https://tidesat-mapa.streamlit.app/",
    "https://tidesat-estrela.streamlit.app/",
    "https://tidesat-estrela2.streamlit.app/",
    "https://tidesat-portosrs.streamlit.app/",
    "https://tidesat-canoas.streamlit.app/",
    "https://tidesat-ipatinga.streamlit.app/",
    "https://tidesat-canada.streamlit.app/",
    "https://tidesat-metsul.streamlit.app/",
    "https://tidesat-estrela-testes.streamlit.app/",
    "https://tidesat-muc-temp.streamlit.app/",
    "https://tidesat-imbituba.streamlit.app/"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Embaralha para evitar padrão fixo diário
random.shuffle(URLS)

for url in URLS:
    print(f"🔔 Pingando {url}")
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    print(f"✅ OK {url} -> {response.status_code}")

    # Espaçamento humano entre acessos
    sleep_time = random.randint(20, 40)
    print(f"⏳ Aguardando {sleep_time}s")
    time.sleep(sleep_time)

print("👻 Bot Fantasma finalizado com sucesso")
