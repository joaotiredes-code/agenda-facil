"""Controlador de Agendamentos."""
from datetime import date

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from ..db import get_db
from ..errors import ValidationError
from ..models import agendamento, cliente, profissional, servico
from .helpers import flash_erros, regras_config

bp = Blueprint("agendamentos", __name__, url_prefix="/agendamentos")


@bp.route("/")
def lista():
    db = get_db()
    data = request.args.get("data", "").strip()
    status = request.args.get("status", "").strip()
    prof_id = request.args.get("profissional_id", type=int)
    return render_template(
        "agendamentos/lista.html",
        agendamentos=agendamento.listar(db, data or None, prof_id, status or None),
        profissionais=profissional.listar(db),
        filtros={"data": data, "status": status, "profissional_id": prof_id},
    )


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    db = get_db()
    dados = request.form
    if request.method == "POST":
        inicio = f"{dados.get('data', '')} {dados.get('horario', '')}"
        try:
            agendamento.criar(
                db,
                dados.get("cliente_id", type=int),
                dados.get("profissional_id", type=int),
                dados.get("servico_id", type=int),
                inicio,
                dados.get("observacao", ""),
                regras=regras_config(),
            )
            flash("Agendamento realizado com sucesso.", "sucesso")
            return redirect(url_for("agendamentos.lista"))
        except ValidationError as erro:
            flash_erros(erro)
    return render_template(
        "agendamentos/form.html",
        dados=dados,
        clientes=cliente.listar(db),
        servicos=servico.listar(db, apenas_ativos=True),
        hoje=date.today().isoformat(),
    )


@bp.route("/<int:agendamento_id>/cancelar", methods=["POST"])
def cancelar(agendamento_id):
    try:
        agendamento.cancelar(get_db(), agendamento_id)
        flash("Agendamento cancelado.", "sucesso")
    except ValidationError as erro:
        flash_erros(erro)
    return redirect(request.referrer or url_for("agendamentos.lista"))


@bp.route("/<int:agendamento_id>/concluir", methods=["POST"])
def concluir(agendamento_id):
    try:
        agendamento.concluir(get_db(), agendamento_id)
        flash("Atendimento marcado como concluído.", "sucesso")
    except ValidationError as erro:
        flash_erros(erro)
    return redirect(request.referrer or url_for("agendamentos.lista"))


@bp.route("/horarios")
def horarios():
    """API JSON: horários livres para profissional + serviço + data."""
    livres = agendamento.horarios_disponiveis(
        get_db(),
        request.args.get("profissional_id", type=int),
        request.args.get("servico_id", type=int),
        request.args.get("data", ""),
        regras=regras_config(),
    )
    return jsonify(livres)
