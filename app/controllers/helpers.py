"""Funções auxiliares dos controladores."""
from flask import current_app, flash

from ..errors import ValidationError


def regras_config():
    c = current_app.config
    return {
        "HORA_ABERTURA": c["HORA_ABERTURA"],
        "HORA_FECHAMENTO": c["HORA_FECHAMENTO"],
        "PASSO_MIN": c["PASSO_MIN"],
        "DIAS_FUNCIONAMENTO": c["DIAS_FUNCIONAMENTO"],
    }


def flash_erros(erro: ValidationError):
    for mensagem in erro.mensagens:
        flash(mensagem, "erro")
