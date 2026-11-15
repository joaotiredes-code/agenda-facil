"""Controlador do painel inicial."""
from flask import Blueprint, render_template

from ..db import get_db
from ..models import agendamento
from datetime import datetime

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    db = get_db()
    agora = datetime.now()
    hoje = agora.strftime("%Y-%m-%d")
    return render_template(
        "index.html",
        resumo=agendamento.resumo(db, agora),
        agenda_hoje=agendamento.listar(db, data=hoje, status="agendado"),
    )
