"""Funções de validação reutilizáveis."""
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def limpar_telefone(telefone):
    """Mantém apenas os dígitos do telefone."""
    return re.sub(r"\D", "", telefone or "")


def texto(valor):
    return (valor or "").strip()
