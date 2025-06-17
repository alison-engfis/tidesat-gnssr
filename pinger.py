from playwright.sync_api import sync_playwright
import time

urls = [
    "https://tidesat.streamlit.app",
    "https://tidesat-portosrs.streamlit.app",
    "https://tidesat-canoas.streamlit.app",
    "https://tidesat-ipatinga.streamlit.app",
    "https://tidesat-estrela.streamlit.app",
    "https://tidesat-estrela2.streamlit.app",
    "https://tidesat-fundy.streamlit.app"
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    for url in urls:
        try:
            page = context.new_page()
            print(f"🔄 Acessando: {url}")
            page.goto(url, timeout=60000)
            page.wait_for_load_state("load")

            # Verifica se o gráfico está presente (mais confiável que texto)
            page.wait_for_selector(".plotly-graph-div", timeout=30000)

            print(f"✅ Visitado e carregado: {url}")

        except Exception as e:
            print(f"❌ Erro ao acessar {url}: {e}")

        finally:
            page.close()

    browser.close()
