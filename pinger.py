from playwright.sync_api import sync_playwright
import time

urls = [
    "https://tidesat.streamlit.app",
    "https://tidesat2.streamlit.app",
    "https://tidesat3.streamlit.app",
    "https://tidesat-all.streamlit.app",
    "https://tidesat-mapa.streamlit.app",
    "https://tidesat-estrela.streamlit.app",
    "https://tidesat-estrela2.streamlit.app",
    "https://tidesat-portosrs.streamlit.app",
    "https://tidesat-canoas.streamlit.app",
    "https://tidesat-ipatinga.streamlit.app",
    "https://tidesat-canada.streamlit.app",
    "https://tidesat-metsul.streamlit.app",
    "https://tidesat-estrela-testes.streamlit.app"  
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    for url in urls:
        try:
            page = context.new_page()
            print(f"🔄 Acessando: {url}")
            page.goto(url, timeout=90000)
            page.wait_for_load_state("load")  # aguarda resposta inicial do servidor

            # Espera manual de 45 segundos para renderizações lentas
            time.sleep(60)

            print(f"✅ Visitado e mantido ativo: {url}")

        except Exception as e:
            print(f"❌ Erro ao acessar {url}: {e}")

        finally:
            page.close()

    browser.close()
