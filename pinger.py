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
    for url in urls:
        page = browser.new_page()
        page.goto(url)
        print(f"✅ Visitado: {url}")
        time.sleep(10)
        page.close()
    browser.close()
