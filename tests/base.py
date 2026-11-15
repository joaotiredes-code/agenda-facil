"""Infraestrutura comum aos testes: banco temporário isolado por teste."""
import os
import tempfile
import unittest

from app import create_app, db as camada_db


class BaseTeste(unittest.TestCase):
    def setUp(self):
        self.arquivo = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.arquivo.close()
        self.app = create_app({"DATABASE": self.arquivo.name, "TESTING": True})
        self.contexto = self.app.app_context()
        self.contexto.push()
        self.db = camada_db.get_db()

    def tearDown(self):
        camada_db.close_db()
        self.contexto.pop()
        os.unlink(self.arquivo.name)
