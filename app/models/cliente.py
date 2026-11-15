"""Modelo Cliente: regras de negócio e persistência."""
import sqlite3

from ..errors import ValidationError
from .validacao import EMAIL_RE, limpar_telefone, texto


def _validar(nome, email, telefone):
    erros = []
    nome = texto(nome)
    email = texto(email).lower()
    telefone = limpar_telefone(telefone)
    if len(nome) < 3:
        erros.append("O nome deve ter pelo menos 3 caracteres.")
    if not EMAIL_RE.match(email):
        erros.append("Informe um e-mail válido (ex.: nome@dominio.com).")
    if len(telefone) not in (10, 11):
        erros.append("O telefone deve ter 10 ou 11 dígitos, com DDD.")
    if erros:
        raise ValidationError(erros)
    return nome, email, telefone


def listar(db, busca=None):
    if busca:
        termo = f"%{busca.strip()}%"
        return db.execute(
            "SELECT * FROM cliente WHERE nome LIKE ? OR email LIKE ? ORDER BY nome",
            (termo, termo),
        ).fetchall()
    return db.execute("SELECT * FROM cliente ORDER BY nome").fetchall()


def obter(db, cliente_id):
    return db.execute("SELECT * FROM cliente WHERE id = ?", (cliente_id,)).fetchone()


def criar(db, nome, email, telefone):
    nome, email, telefone = _validar(nome, email, telefone)
    try:
        cursor = db.execute(
            "INSERT INTO cliente (nome, email, telefone) VALUES (?, ?, ?)",
            (nome, email, telefone),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise ValidationError("Já existe um cliente cadastrado com este e-mail.")
    return cursor.lastrowid


def atualizar(db, cliente_id, nome, email, telefone):
    if obter(db, cliente_id) is None:
        raise ValidationError("Cliente não encontrado.")
    nome, email, telefone = _validar(nome, email, telefone)
    try:
        db.execute(
            "UPDATE cliente SET nome = ?, email = ?, telefone = ? WHERE id = ?",
            (nome, email, telefone, cliente_id),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise ValidationError("Já existe um cliente cadastrado com este e-mail.")


def excluir(db, cliente_id):
    if obter(db, cliente_id) is None:
        raise ValidationError("Cliente não encontrado.")
    total = db.execute(
        "SELECT COUNT(*) FROM agendamento WHERE cliente_id = ?", (cliente_id,)
    ).fetchone()[0]
    if total:
        raise ValidationError(
            "Este cliente possui agendamentos e não pode ser excluído."
        )
    db.execute("DELETE FROM cliente WHERE id = ?", (cliente_id,))
    db.commit()
