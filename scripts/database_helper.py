import sqlite3
import logging
import os
from typing import Dict, List

logging.basicConfig(level=logging.INFO)

def create_database(db_name: str = 'news_sent.db', db_dir: str = './databases'):
    """Cria ou verifica se o banco de dados SQLite já existe."""
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, db_name)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS news_sent
                              (id INTEGER PRIMARY KEY, guid TEXT UNIQUE)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS used_game_ids
                              (id INTEGER PRIMARY KEY, game_id TEXT UNIQUE, game_name TEXT)''')
            conn.commit()
        logging.info(f"Banco de dados criado ou verificado com sucesso: {db_path}")
    except Exception as e:
        logging.error(f"Erro ao criar/verificar o banco de dados: {e}")

def mark_news_as_sent(guid: str, db_name: str = 'news_sent.db', db_dir: str = './databases'):
    """Marca a notícia com o GUID fornecido como enviada no banco de dados."""
    db_path = os.path.join(db_dir, db_name)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO news_sent (guid) VALUES (?)", (guid,))
            conn.commit()
        logging.info(f"Notícia com GUID {guid} marcada como enviada.")
    except Exception as e:
        logging.error(f"Erro ao marcar notícia como enviada: {e}")

def is_news_sent(guid: str, db_name: str = 'news_sent.db', db_dir: str = './databases') -> bool:
    """Verifica se a notícia com o GUID fornecido já foi enviada."""
    db_path = os.path.join(db_dir, db_name)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM news_sent WHERE guid=?", (guid,))
            result = cursor.fetchone()
        return result is not None
    except Exception as e:
        logging.error(f"Erro ao verificar se a notícia foi enviada: {e}")
        return False

def add_used_game_id(game_id: str, game_name: str, db_name: str = 'news_sent.db', db_dir: str = './databases'):
    """Adiciona um ID de jogo usado ao banco de dados."""
    db_path = os.path.join(db_dir, db_name)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO used_game_ids (game_id, game_name) VALUES (?, ?)", (game_id, game_name))
            conn.commit()
        logging.info(f"ID do jogo {game_id} ({game_name}) adicionado ao banco de dados.")
    except Exception as e:
        logging.error(f"Erro ao adicionar ID do jogo ao banco de dados: {e}")

def get_used_game_ids(db_name: str = 'news_sent.db', db_dir: str = './databases') -> List[Dict[str, str]]:
    """Obtém todos os IDs de jogos usados do banco de dados."""
    db_path = os.path.join(db_dir, db_name)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT game_id, game_name FROM used_game_ids")
            rows = cursor.fetchall()
            return [{"game_id": row[0], "game_name": row[1]} for row in rows]
    except Exception as e:
        logging.error(f"Erro ao obter IDs de jogos usados do banco de dados: {e}")
        return []
