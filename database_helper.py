import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

def create_database(db_path='news_sent.db'):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS news_sent
                              (id INTEGER PRIMARY KEY, guid TEXT UNIQUE)''')
            conn.commit()
        logging.info("Banco de dados criado ou verificado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao criar/verificar o banco de dados: {e}")

def mark_news_as_sent(guid, db_path='news_sent.db'):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO news_sent (guid) VALUES (?)", (guid,))
            conn.commit()
        logging.info(f"Notícia com GUID {guid} marcada como enviada.")
    except Exception as e:
        logging.error(f"Erro ao marcar notícia como enviada: {e}")

def is_news_sent(guid, db_path='news_sent.db'):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM news_sent WHERE guid=?", (guid,))
            result = cursor.fetchone()
        return result is not None
    except Exception as e:
        logging.error(f"Erro ao verificar se a notícia foi enviada: {e}")
        return False
