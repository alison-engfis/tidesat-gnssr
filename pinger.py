from playwright.sync_api import sync_playwright
import requests, time, random

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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

def http_probe(url: str, attempts: int = 2) -> bool:
    # 1) Raiz
    for _ in range(attempts):
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            if r.status_code < 500:
                print(f"HTTP raiz OK: {url} [{r.status_code}]")
                break
        except Exception as e:
            print(f"HTTP raiz falhou: {url} ({e})")
            time.sleep(3)
    # 2) Health (quando disponível)
    try:
        r = requests.get(url.rstrip("/") + "/_stcore/health", headers=HEADERS, timeout=15)
        print(f"Health: {url}/_stcore/health -> {r.status_code}")
        return r.ok
    except Exception as e:
        print(f"Health falhou: {url} ({e})")
        return False

def browser_wake(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(
            user_agent=HEADERS["User-Agent"],
            ignore_https_errors=True,
            java_script_enabled=True,
            viewport={"width": 1366, "height": 900}
        )
        page = ctx.new_page()
        try:
            # Espera rede ficar ociosa para assegurar handshake do Streamlit
            page.goto(url, wait_until="networkidle", timeout=90000)
            # Interage leve (ajuda apps com tela de senha/landing)
            page.mouse.move(200, 200)
            page.wait_for_timeout(90000)  # ~90 s conectado
            print(f"✅ Ativo: {url}")
        except Exception as e:
            print(f"❌ Falha Playwright em {url}: {e}")
        finally:
            page.close()
            browser.close()

def main():
    random.shuffle(urls)  # espalha a ordem a cada execução
    for url in urls:
        ok = http_probe(url)
        if not ok:
            print(f"⚠️  Health falhou ou ausente para: {url} — seguindo com navegador.")
        browser_wake(url)

if __name__ == "__main__":
    main()
