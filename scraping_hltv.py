from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import feedparser

def accept_cookies(driver):
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'))
        )
        cookie_button.click()
    except Exception as e:
        print(f"Erro ao aceitar cookies: {e}")

def get_news_content(news_url):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(news_url)
    
    try:
        accept_cookies(driver)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'p'))
        )
        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
        content = ' '.join([p.text for p in paragraphs])
        content = content.encode('ascii', 'ignore').decode('ascii')
    except Exception as e:
        print(f"Erro ao coletar conteúdo da notícia: {e}")
        content = "N/A"
    
    driver.quit()
    return content

def fetch_hltv_news():
    rss_url = "https://www.hltv.org/rss/news"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    for entry in feed.entries:
        news_item = {
            "title": entry.title,
            "description": entry.description,
            "link": entry.link,
            "guid": entry.guid,
            "pubDate": entry.published,
            "media_content": entry.get('media_content', [{}])[0].get('url', None)
        }
        news_items.append(news_item)
    
    return news_items

def user_interaction(news_links):
    print("Links das notícias disponíveis:")
    for i, news in enumerate(news_links):
        print(f"{i + 1}. {news['title']} ({news['pubDate']}) - {news['link']}")
    
    choice = input("Digite o número da notícia que você deseja coletar (ou 'all' para todas): ")
    
    if choice.lower() == 'all':
        return news_links
    else:
        selected_indices = [int(i) - 1 for i in choice.split()]
        return [news_links[i] for i in selected_indices]

def main():
    news_list = fetch_hltv_news()
    return news_list