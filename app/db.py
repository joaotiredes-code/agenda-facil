"""Acesso ao banco de dados (SQLite)."""
import os
import sqlite3

from flask import current_app, g

SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "schema.sql"
)


def conectar(caminho):
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def get_db():
    if "db" not in g:
        g.db = conectar(current_app.config["DATABASE"])
    return g.db


def close_db(_erro=None):
    conexao = g.pop("db", None)
    if conexao is not None:
        conexao.close()


def init_schema():
    """Cria as tabelas (idempotente)."""
    conexao = get_db()
    with open(SCHEMA_PATH, encoding="utf-8") as arquivo:
        conexao.executescript(arquivo.read())
    conexao.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
