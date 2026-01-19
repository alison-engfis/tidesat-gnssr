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

random.shuffle(URLS)

failed = []

for url in URLS:
    print(f"🔔 Pingando {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        print(f"↪️  Status {r.status_code} (conta como atividade)")

    except requests.RequestException as e:
        print(f"❌ Falha real ao acessar {url}: {e}")
        failed.append(url)

    sleep_time = random.randint(20, 40)
    print(f"⏳ Aguardando {sleep_time}s")
    time.sleep(sleep_time)

if failed:
    raise SystemExit(
        f"🚨 {len(failed)} apps não responderam:\n" + "\n".join(failed)
    )

print("👻 Bot Fantasma finalizado com sucesso")
