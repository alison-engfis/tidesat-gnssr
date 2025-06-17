from playwright.sync_api import sync_playwright
import time

urls = [
    "https://tidesat.streamlit.app",
    "https://tidesat-portosrs.streamlit.app",
    "https://tidesat-canoas.streamlit.app",
    "https://tidesat-ipatinga.streamlit.app",
    "https://tidesat-estrela.streamlit.app",
    "https://tidesat-fundy.streamlit.app"
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    for url in urls:
        try:
            page = context.new_page()
            page.goto(url, timeout=60000)  # até 60s para carregar

            # Espera por um texto específico do Streamlit (ajustável se necessário)
            page.wait_for_selector("text=Nível recente", timeout=10000)

            print(f"✅ Visitado e carregado: {url}")

        except Exception as e:
            print(f"❌ Erro ao acessar {url}: {e}")

        finally:
            page.close()

    browser.close()
