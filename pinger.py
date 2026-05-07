import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    "https://tidesat-imbituba.streamlit.app/",
    "https://tidesat-veleiros.streamlit.app/",
    "https://tidesat-guaiba.streamlit.app/"
]

def setup_stealth_driver():
    """Configura Chrome com técnicas anti-detecção"""
    chrome_options = Options()
    
    # Modo headless (necessário para CI)
    chrome_options.add_argument("--headless=new")
    
    # Configurações básicas de segurança
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Desabilita detecção de automação
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent realista
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # Configurações de janela
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    
    # Desabilita recursos que podem denunciar automação
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--disable-software-rasterizer")
    
    # Aceita certificados inseguros (evita erros SSL)
    chrome_options.add_argument("--ignore-certificate-errors")
    
    # Configurações de linguagem e localização
    chrome_options.add_argument("--lang=pt-BR")
    chrome_options.add_experimental_option('prefs', {
        'intl.accept_languages': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    })
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(90)
    
    # Injeta script para mascarar webdriver
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Mascara outras propriedades de detecção
            window.navigator.chrome = {
                runtime: {}
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
            
            // Simula permissões
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        '''
    })
    
    return driver
    
# Delay com padrão mais humano
def human_like_delay(min_sec=1, max_sec=3):
    
    time.sleep(random.uniform(min_sec, max_sec))
    
# Simula comportamento humano: scroll, movimento do mouse, etc
def simulate_human_behavior(driver):
    
    try:
        
        # Scroll suave e aleatório
        scroll_positions = [300, 500, 800, 400, 200]
        
        for position in random.sample(scroll_positions, k=random.randint(2, 4)):
            driver.execute_script(f"window.scrollTo(0, {position});")
            human_like_delay(0.3, 0.8)
        
        # Volta ao topo
        driver.execute_script("window.scrollTo(0, 0);")
        human_like_delay(0.5, 1.2)
        
        # Simula movimento do mouse (move para elemento aleatório)
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, "div, button, input")
            if elements:
                target = random.choice(elements[:10])  # Pega um dos 10 primeiros
                actions = ActionChains(driver)
                actions.move_to_element(target).perform()
                human_like_delay(0.2, 0.5)
        except:
            pass
            
    except Exception as e:
        print(f"  ⚠️  Erro ao simular comportamento: {e}")

def wait_for_streamlit(driver, timeout=45):
    """Aguarda o Streamlit carregar completamente"""
    try:
        # Aguarda body carregar
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Aguarda elementos específicos do Streamlit
        human_like_delay(2, 4)
        
        # Tenta detectar se o app carregou verificando por elementos comuns
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stAppViewContainer'], .main, .stApp"))
            )
            print("  ✓ Container do Streamlit detectado")
        except:
            print("  ⚠️  Container não detectado, mas prosseguindo...")
        
        return True
    except Exception as e:
        print(f"  ❌ Timeout aguardando Streamlit: {e}")
        return False

# Tenta interagir com elementos do app
def interact_with_app(driver):
    
    try:
        # Procura por botões do Streamlit
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[kind='primary'], button[kind='secondary'], .stButton button")
        if buttons and random.random() < 0.3:  # 30% de chance de clicar
            btn = random.choice(buttons[:3])
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                human_like_delay(0.3, 0.7)
                btn.click()
                print("  🖱️  Clicou em um botão")
                human_like_delay(1, 2)
            except:
                pass
        
        # Procura por inputs/selectbox
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea, select")
        if inputs and random.random() < 0.2:  # 20% de chance
            print(f"  👀 Encontrou {len(inputs)} inputs")
            
    except Exception as e:
        print(f"  ⚠️  Erro ao interagir: {e}")

# Visita um app e simula comportamento humano
def ping_app(driver, url, index, total):
    
    print(f"\n{'='*60}")
    print(f"🔗 [{index}/{total}] Acessando: {url}")
    print(f"{'='*60}")
    
    try:
        # Carrega a página
        driver.get(url)
        
        # Aguarda carregar
        if not wait_for_streamlit(driver):
            return False
        
        # Tempo de "leitura" da página
        reading_time = random.randint(8, 18)
        print(f"  📖 Simulando leitura por {reading_time}s...")
        
        for i in range(reading_time):
            if i % 4 == 0:  # A cada 4 segundos faz algo
                if random.random() < 0.6:
                    simulate_human_behavior(driver)
                elif random.random() < 0.3:
                    interact_with_app(driver)
            time.sleep(1)
        
        # Captura título para confirmar
        try:
            title = driver.title
            print(f"  📄 Título: {title[:50]}...")
        except:
            pass
        
        print(f"  ✅ Visita concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao acessar: {e}")
        return False

def main():
    print("🤖 Iniciando Bot Fantasma Streamlit v2.0")
    print(f"⏰ Hora de início: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Delay inicial aleatório (evita padrão fixo)
    initial_delay = random.randint(10, 120)
    print(f"⏳ Delay inicial de {initial_delay}s para parecer mais natural...")
    time.sleep(initial_delay)
    
    # Randomiza ordem dos apps
    shuffled_urls = URLS.copy()
    random.shuffle(shuffled_urls)
    
    failed = []
    driver = None
    
    try:
        driver = setup_stealth_driver()
        print("✓ Driver configurado com anti-detecção ativada\n")
        
        total = len(shuffled_urls)
        
        for idx, url in enumerate(shuffled_urls, 1):
            success = ping_app(driver, url, idx, total)
            
            if not success:
                failed.append(url)
            
            # Pausa entre apps (exceto no último)
            if idx < total:
                pause = random.randint(25, 50)
                print(f"\n⏸️  Pausando {pause}s antes do próximo app...")
                time.sleep(pause)
        
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        raise
    
    finally:
        if driver:
            driver.quit()
            print("\n🚪 Driver fechado")
    
    print(f"\n{'='*60}")
    print(f"⏰ Hora de término: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed:
        print(f"⚠️  {len(failed)} apps falharam:")
        for url in failed:
            print(f"  - {url}")
        raise SystemExit(f"🚨 {len(failed)} apps não responderam")
    
    print("✅ Bot Fantasma finalizado - Todos os apps visitados!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
