import argparse
from scripts.scraping_hltv import main as scrape_hltv_news, get_news_content, user_interaction
from scripts.scraping_dust2 import main as scrape_dust2_news
from scripts.script_generation import generate_script
from scripts.upload_to_notion import create_and_update_script
from scripts.twitch_clips import fetch_cs2_clips, search_games, fetch_and_download_top_clip, download_clip
import os
from dotenv import load_dotenv
from scripts.database_helper import create_database, mark_news_as_sent, is_news_sent, add_used_game_id, get_used_game_ids
from scripts.config import get_env_variable
import logging
from typing import Dict, List
import asyncio
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('app.log')

# Set levels for handlers
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.INFO)

# Create formatter and add it to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Get the logger and add the handlers
logger = logging.getLogger()
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def format_uuid(uuid: str) -> str:
    """Formata um UUID removendo hífens."""
    return uuid.replace("-", "")

def get_started_at(period: str) -> str:
    """Retorna a data de início baseada no período."""
    now = datetime.utcnow()
    if period == "day":
        start = now - timedelta(days=1)
    elif period == "week":
        start = now - timedelta(weeks=1)
    elif period == "month":
        start = now - timedelta(days=30)
    elif period == "year":
        start = now - timedelta(days=365)
    elif period == "all":
        return None
    else:
        raise ValueError("Período inválido.")
    return start.isoformat() + 'Z'

async def main():
    """Função principal do script."""
    logger.info("Iniciando a função main")
    load_dotenv()
    logger.info("Variáveis de ambiente carregadas")
    create_database(db_name='news_sent.db', db_dir='./databases')
    logger.info("Banco de dados verificado/criado")

    parser = argparse.ArgumentParser(description="Script para coletar notícias e criar scripts para Notion.")
    parser.add_argument("--source", "--src", choices=["hltv", "dust2", "all"], help="Fonte das notícias: 'hltv', 'dust2' ou 'all'")
    parser.add_argument("--process", "--proc", choices=["all"], help="Processar todas as notícias automaticamente")
    parser.add_argument("--fetch-clips", action='store_true', help="Busca os clipes mais populares de CS2 na Twitch")
    parser.add_argument("--fetch-top-clip", action='store_true', help="Busca e baixa o clipe mais famoso de CS2 na Twitch")
    parser.add_argument("--game-id", type=str, help="ID do jogo na Twitch")
    parser.add_argument("--period", choices=["day", "week", "month", "year", "all"], default="week", help="Período dos clipes: 'day', 'week', 'month', 'year'")
    parser.add_argument("--min-duration", type=int, default=40, help="Duração mínima dos clipes em segundos")
    parser.add_argument("--max-duration", type=int, default=90, help="Duração máxima dos clipes em segundos")
    parser.add_argument("--search-game", type=str, help="Busca o ID de um jogo na Twitch")
    parser.add_argument("--list-games", action='store_true', help="Lista os IDs de jogos usados anteriormente")
    args = parser.parse_args()

    if not args.search_game and not args.source and not args.fetch_clips and not args.fetch_top_clip and not args.list_games:
        parser.error("A opção --source/--src é obrigatória, a menos que --search-game, --list-games, --fetch-clips ou --fetch-top-clip seja usado.")

    logger.info(f"Argumentos recebidos: {args}")

    try:
        token = os.getenv("NOTION_TOKEN")
        database_id = os.getenv("NOTION_DATABASE_ID")

        if not token or not database_id:
            raise EnvironmentError("As variáveis NOTION_TOKEN e NOTION_DATABASE_ID devem estar definidas para usar o Notion.")

        token = get_env_variable("NOTION_TOKEN", "Digite seu token de integração do Notion: ") if not token else token
        database_id = format_uuid(get_env_variable("NOTION_DATABASE_ID", "Digite o ID da base de dados do Notion: ")) if not database_id else format_uuid(database_id)

        client_id = os.getenv("TWITCH_CLIENT_ID")
        client_secret = os.getenv("TWITCH_CLIENT_SECRET")

        if args.search_game:
            logger.info(f"Buscando ID do jogo: {args.search_game}")
            games = await search_games(client_id, client_secret, args.search_game)
            logger.info(f"Resultados da busca: {games}")
            for game in games:
                print(f"ID: {game['id']}, Nome: {game['name']}")
                add_used_game_id(game['id'], game['name'])
            return

        if args.list_games:
            used_game_ids = get_used_game_ids()
            logger.info("Listando IDs de jogos usados anteriormente:")
            for game in used_game_ids:
                print(f"ID: {game['game_id']}, Nome: {game['game_name']}")
            return

        if args.fetch_clips:
            if not args.game_id:
                raise ValueError("O ID do jogo deve ser fornecido para buscar clipes.")
            started_at = get_started_at(args.period)
            logger.info("Iniciando a busca de clipes de CS2")
            clips = await fetch_cs2_clips(client_id, client_secret, args.game_id, period=args.period, num_clips=10, min_duration=args.min_duration, max_duration=args.max_duration, started_at=started_at)
            logger.info(f"{len(clips)} clipes de CS2 coletados")
            for i, clip in enumerate(clips, start=1):
                logger.info(f"Clip {i}: {clip['title']} - {clip['url']} - {clip['duration']}s - {clip['view_count']} views")
                print(f"{i}. {clip['title']} - {clip['url']} - {clip['duration']}s - {clip['view_count']} views")
            download_choice = input("Digite o número do clipe que deseja baixar ou 'all' para baixar todos: ")
            if download_choice.lower() == 'all':
                for clip in clips:
                    await download_clip(clip['id'], clip['title'], client_id, client_secret)
            else:
                try:
                    selected_index = int(download_choice) - 1
                    if 0 <= selected_index < len(clips):
                        selected_clip = clips[selected_index]
                        await download_clip(selected_clip['id'], selected_clip['title'], client_id, client_secret)
                    else:
                        logger.error("Número do clipe inválido.")
                except ValueError:
                    logger.error("Entrada inválida.")
            return

        if args.fetch_top_clip:
            if not args.game_id:
                raise ValueError("O ID do jogo deve ser fornecido para buscar clipes.")
            logger.info("Iniciando a busca do clipe mais famoso de CS2")
            await fetch_and_download_top_clip(client_id, client_secret, args.game_id, period=args.period, min_duration=args.min_duration, max_duration=args.max_duration)
            return

        if args.source in ['hltv', 'all']:
            logger.info("Coletando notícias do HLTV")
            news_data_hltv = scrape_hltv_news()
            process_news(news_data_hltv, token, database_id, args.process == "all")

        if args.source in ['dust2', 'all']:
            logger.info("Coletando notícias do Dust2")
            news_data_dust2 = scrape_dust2_news()
            process_news(news_data_dust2, token, database_id, args.process == "all")

    except Exception as e:
        logger.error(f"Erro durante a execução do script: {e}")
        print("Ocorreu um erro. Execute 'python main.py --help' para mais informações sobre como usar o script.")

def process_news(news_data, token, database_id, process_all=False):
    logger.info(f"Notícias coletadas: {len(news_data)} itens")
    
    if process_all:
        selected_news = news_data  # Processa todas as notícias automaticamente
    else:
        selected_news = user_interaction(news_data)  # Permite interação do usuário para selecionar as notícias

    for news in selected_news:
        if is_news_sent(news['guid'], db_name='news_sent.db', db_dir='./databases'):
            logger.info(f"Notícia '{news['title']}' já foi enviada para o Notion.")
            continue

        news['content'] = get_news_content(news['link'])
        script = generate_script(news['content'])
        logger.info(f"Script gerado para '{news['title']}':\n{script}")
        logger.info("="*50)

        create_and_update_script(token, database_id, script)
        mark_news_as_sent(news['guid'], db_name='news_sent.db', db_dir='./databases')

if __name__ == "__main__":
    logger.info("Executando o script principal diretamente")
    asyncio.run(main())