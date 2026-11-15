"""Controlador de Profissionais."""
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for

from ..db import get_db
from ..errors import ValidationError
from ..models import profissional, servico
from .helpers import flash_erros

bp = Blueprint("profissionais", __name__, url_prefix="/profissionais")


@bp.route("/")
def lista():
    return render_template(
        "profissionais/lista.html", profissionais=profissional.listar(get_db())
    )


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    db = get_db()
    dados = request.form
    selecionados = []
    if request.method == "POST":
        selecionados = [int(v) for v in dados.getlist("servicos") if v.isdigit()]
        try:
            profissional.criar(db, dados.get("nome"), dados.get("especialidade"),
                               dados.getlist("servicos"), ativo=dados.get("ativo") == "1")
            flash("Profissional cadastrado com sucesso.", "sucesso")
            return redirect(url_for("profissionais.lista"))
        except ValidationError as erro:
            flash_erros(erro)
    padrao = dados if request.method == "POST" else {"ativo": 1}
    return render_template("profissionais/form.html", profissional=padrao,
                           servicos=servico.listar(db), selecionados=selecionados,
                           editando=False)


@bp.route("/<int:profissional_id>/editar", methods=["GET", "POST"])
def editar(profissional_id):
    db = get_db()
    atual = profissional.obter(db, profissional_id)
    if atual is None:
        abort(404)
    selecionados = profissional.servicos_ids(db, profissional_id)
    if request.method == "POST":
        dados = request.form
        selecionados = [int(v) for v in dados.getlist("servicos") if v.isdigit()]
        try:
            profissional.atualizar(db, profissional_id, dados.get("nome"),
                                   dados.get("especialidade"), dados.getlist("servicos"),
                                   ativo=dados.get("ativo") == "1")
            flash("Profissional atualizado com sucesso.", "sucesso")
            return redirect(url_for("profissionais.lista"))
        except ValidationError as erro:
            flash_erros(erro)
        atual = {**dados.to_dict(), "ativo": 1 if dados.get("ativo") == "1" else 0}
    return render_template("profissionais/form.html", profissional=atual,
                           servicos=servico.listar(db), selecionados=selecionados,
                           editando=True, profissional_id=profissional_id)


@bp.route("/<int:profissional_id>/excluir", methods=["POST"])
def excluir(profissional_id):
    try:
        profissional.excluir(get_db(), profissional_id)
        flash("Profissional excluído.", "sucesso")
    except ValidationError as erro:
        flash_erros(erro)
    return redirect(url_for("profissionais.lista"))


@bp.route("/por-servico/<int:servico_id>")
def por_servico(servico_id):
    """API JSON usada pelo formulário de agendamento."""
    itens = profissional.por_servico(get_db(), servico_id)
    return jsonify([{"id": p["id"], "nome": p["nome"]} for p in itens])
