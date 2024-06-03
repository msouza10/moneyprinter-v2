import argparse
from scraping_hltv import main as scrape_hltv_news, get_news_content, user_interaction
from scraping_dust2 import main as scrape_dust2_news
from script_generation import generate_script
from upload_to_notion import create_and_update_script
import os
from dotenv import load_dotenv
from database_helper import create_database, mark_news_as_sent, is_news_sent
from config import get_env_variable
import logging

logging.basicConfig(level=logging.INFO)

def format_uuid(uuid):
    return uuid

def main():
    load_dotenv()
    create_database()

    parser = argparse.ArgumentParser(description="Script para coletar notícias e criar scripts para Notion.")
    parser.add_argument("--source", choices=["hltv", "dust2"], required=True, help="Fonte das notícias: 'hltv' ou 'dust2'")
    args = parser.parse_args()

    token = get_env_variable("NOTION_TOKEN", "Digite seu token de integração do Notion: ")
    database_id = format_uuid(get_env_variable("NOTION_DATABASE_ID", "Digite o ID da base de dados do Notion: "))

    if args.source == 'hltv':
        news_data = scrape_hltv_news()
    elif args.source == 'dust2':
        news_data = scrape_dust2_news()

    logging.info(f"Notícias coletadas: {len(news_data)} itens")

    selected_news = user_interaction(news_data)

    for news in selected_news:
        if is_news_sent(news['guid']):
            logging.info(f"Notícia '{news['title']}' já foi enviada para o Notion.")
            continue

        news['content'] = get_news_content(news['link'])
        script = generate_script(news['content'])
        print(script)
        print("="*50)

        create_and_update_script(token, database_id, script)
        mark_news_as_sent(news['guid'])

if __name__ == "__main__":
    main()
