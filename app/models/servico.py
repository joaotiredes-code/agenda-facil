"""Modelo Serviço: regras de negócio e persistência."""
import sqlite3

from ..errors import ValidationError
from .validacao import texto


def _validar(nome, descricao, duracao_min, preco):
    erros = []
    nome = texto(nome)
    descricao = texto(descricao)
    if len(nome) < 3:
        erros.append("O nome do serviço deve ter pelo menos 3 caracteres.")
    try:
        duracao = int(duracao_min)
        if not 5 <= duracao <= 480:
            erros.append("A duração deve estar entre 5 e 480 minutos.")
    except (TypeError, ValueError):
        duracao = None
        erros.append("Informe a duração em minutos (número inteiro).")
    try:
        valor = round(float(str(preco).replace(",", ".")), 2)
        if valor < 0:
            erros.append("O preço não pode ser negativo.")
    except (TypeError, ValueError):
        valor = None
        erros.append("Informe um preço válido (ex.: 45,90).")
    if erros:
        raise ValidationError(erros)
    return nome, descricao, duracao, valor


def listar(db, apenas_ativos=False):
    sql = "SELECT * FROM servico"
    if apenas_ativos:
        sql += " WHERE ativo = 1"
    return db.execute(sql + " ORDER BY nome").fetchall()


def obter(db, servico_id):
    return db.execute("SELECT * FROM servico WHERE id = ?", (servico_id,)).fetchone()


def criar(db, nome, descricao, duracao_min, preco, ativo=True):
    nome, descricao, duracao, valor = _validar(nome, descricao, duracao_min, preco)
    try:
        cursor = db.execute(
            "INSERT INTO servico (nome, descricao, duracao_min, preco, ativo) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, duracao, valor, 1 if ativo else 0),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise ValidationError("Já existe um serviço com este nome.")
    return cursor.lastrowid


def atualizar(db, servico_id, nome, descricao, duracao_min, preco, ativo=True):
    if obter(db, servico_id) is None:
        raise ValidationError("Serviço não encontrado.")
    nome, descricao, duracao, valor = _validar(nome, descricao, duracao_min, preco)
    try:
        db.execute(
            "UPDATE servico SET nome = ?, descricao = ?, duracao_min = ?, "
            "preco = ?, ativo = ? WHERE id = ?",
            (nome, descricao, duracao, valor, 1 if ativo else 0, servico_id),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise ValidationError("Já existe um serviço com este nome.")


def excluir(db, servico_id):
    if obter(db, servico_id) is None:
        raise ValidationError("Serviço não encontrado.")
    total = db.execute(
        "SELECT COUNT(*) FROM agendamento WHERE servico_id = ?", (servico_id,)
    ).fetchone()[0]
    if total:
        raise ValidationError(
            "Este serviço possui agendamentos e não pode ser excluído. "
            "Marque-o como inativo."
        )
    db.execute("DELETE FROM servico WHERE id = ?", (servico_id,))
    db.commit()
