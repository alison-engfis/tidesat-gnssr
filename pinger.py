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

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA}

def http_probe(url: str) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code >= 500:
            return False
    except Exception:
        return False
    # tentar health do Streamlit (quando existir)
    try:
        r = requests.get(url.rstrip("/") + "/_stcore/health", headers=HEADERS, timeout=8)
        return r.ok
    except Exception:
        return True  # se não existir, considerar ok
       
def browser_wake(url: str, keepalive_ms: int = 45000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(ignore_https_errors=True, user_agent=UA,
                                  viewport={"width": 1366, "height": 900})
        page = ctx.new_page()
        try:
            print(f"🔄 Acessando: {url}")
            page.goto(url, wait_until="networkidle", timeout=120000)
            page.mouse.move(200, 200)
            page.wait_for_timeout(keepalive_ms)  # ~45 s
            print(f"✅ Visitado e mantido ativo: {url}")
        except Exception as e:
            print(f"❌ Erro ao acessar {url}: {e}")
        finally:
            page.close()
            browser.close()

def main():
    random.shuffle(urls)
    time.sleep(random.randint(0, 30))  # jitter leve
    for url in urls:
        ok = http_probe(url)
        if not ok:
            print(f"⚠️  Probe falhou, abrindo navegador: {url}")
        # Mesmo com OK, ainda fazemos um wake curto para garantir WS
        browser_wake(url, keepalive_ms=45000)

if __name__ == "__main__":
    main()
