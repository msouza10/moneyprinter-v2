import unittest
from scripts.database_helper import create_database, mark_news_as_sent, is_news_sent
import sqlite3
import os

class TestDatabaseHelper(unittest.TestCase):

    def setUp(self):
        self.db_path = 'test_news_sent.db'
        create_database(self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def tearDown(self):
        # Verifica se o cursor e a conexão estão abertos antes de fechá-los
        if self.cursor:
            try:
                self.cursor.close()
            except sqlite3.ProgrammingError:
                pass  # O cursor já foi fechado
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.ProgrammingError:
                pass  # A conexão já foi fechada
        try:
            os.remove(self.db_path)
        except PermissionError:
            pass

    def test_mark_news_as_sent(self):
        guid = "test_guid"
        mark_news_as_sent(guid, self.db_path)
        # Fechar conexão antes de reabrir
        if self.conn:
            self.conn.close()
        self.conn = sqlite3.connect(self.db_path)  # Reabra a conexão para verificar
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM news_sent WHERE guid=?", (guid,))
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        self.cursor.close()
        self.conn.close()

    def test_is_news_sent(self):
        guid = "test_guid"
        mark_news_as_sent(guid, self.db_path)
        # Fechar conexão antes de reabrir
        if self.conn:
            self.conn.close()
        self.assertTrue(is_news_sent(guid, self.db_path))
        self.assertFalse(is_news_sent("nonexistent_guid", self.db_path))

if __name__ == '__main__':
    unittest.main()
