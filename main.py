import argparse
from scripts.scraping_hltv import main as scrape_hltv_news, get_news_content, user_interaction
from scripts.scraping_dust2 import main as scrape_dust2_news
from scripts.script_generation import generate_script
from scripts.upload_to_notion import create_and_update_script
import os
from dotenv import load_dotenv
from scripts.database_helper import create_database, mark_news_as_sent, is_news_sent
from scripts.config import get_env_variable
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)

def format_uuid(uuid: str) -> str:
    """Formata um UUID removendo hífens."""
    return uuid.replace("-", "")

def main():
    """Função principal do script."""
    load_dotenv()
    create_database(db_name='news_sent.db', db_dir='./databases')

    parser = argparse.ArgumentParser(description="Script para coletar notícias e criar scripts para Notion.")
    parser.add_argument("--source", "--src", choices=["hltv", "dust2", "all"], required=True, help="Fonte das notícias: 'hltv', 'dust2' ou 'all'")
    parser.add_argument("--process", "--proc", choices=["all"], help="Processar todas as notícias automaticamente")
    args = parser.parse_args()

    try:
        token = os.getenv("NOTION_TOKEN")
        database_id = os.getenv("NOTION_DATABASE_ID")

        if not token or not database_id:
            raise EnvironmentError("As variáveis NOTION_TOKEN e NOTION_DATABASE_ID devem estar definidas para usar o Notion.")

        token = get_env_variable("NOTION_TOKEN", "Digite seu token de integração do Notion: ") if not token else token
        database_id = format_uuid(get_env_variable("NOTION_DATABASE_ID", "Digite o ID da base de dados do Notion: ")) if not database_id else format_uuid(database_id)

        if args.source in ['hltv', 'all']:
            news_data_hltv = scrape_hltv_news()
            process_news(news_data_hltv, token, database_id, args.process == "all")

        if args.source in ['dust2', 'all']:
            news_data_dust2 = scrape_dust2_news()
            process_news(news_data_dust2, token, database_id, args.process == "all")

    except Exception as e:
        logging.error(f"Erro durante a execução do script: {e}")
        print("Ocorreu um erro. Execute 'python main.py --help' para mais informações sobre como usar o script.")

def process_news(news_data, token, database_id, process_all=False):
    logging.info(f"Notícias coletadas: {len(news_data)} itens")
    
    if process_all:
        selected_news = news_data  # Processa todas as notícias automaticamente
    else:
        selected_news = user_interaction(news_data)  # Permite interação do usuário para selecionar as notícias

    for news in selected_news:
        if is_news_sent(news['guid'], db_name='news_sent.db', db_dir='./databases'):
            logging.info(f"Notícia '{news['title']}' já foi enviada para o Notion.")
            continue

        news['content'] = get_news_content(news['link'])
        script = generate_script(news['content'])
        logging.info(f"Script gerado para '{news['title']}':\n{script}")
        logging.info("="*50)

        create_and_update_script(token, database_id, script)
        mark_news_as_sent(news['guid'], db_name='news_sent.db', db_dir='./databases')

if __name__ == "__main__":
    main()
