"""Controlador de Serviços."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..db import get_db
from ..errors import ValidationError
from ..models import servico
from .helpers import flash_erros

bp = Blueprint("servicos", __name__, url_prefix="/servicos")


@bp.route("/")
def lista():
    return render_template("servicos/lista.html", servicos=servico.listar(get_db()))


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    dados = request.form
    if request.method == "POST":
        try:
            servico.criar(get_db(), dados.get("nome"), dados.get("descricao"),
                          dados.get("duracao_min"), dados.get("preco"),
                          ativo=dados.get("ativo") == "1")
            flash("Serviço cadastrado com sucesso.", "sucesso")
            return redirect(url_for("servicos.lista"))
        except ValidationError as erro:
            flash_erros(erro)
    padrao = dados if request.method == "POST" else {"ativo": 1}
    return render_template("servicos/form.html", servico=padrao, editando=False)


@bp.route("/<int:servico_id>/editar", methods=["GET", "POST"])
def editar(servico_id):
    db = get_db()
    atual = servico.obter(db, servico_id)
    if atual is None:
        abort(404)
    if request.method == "POST":
        dados = request.form
        try:
            servico.atualizar(db, servico_id, dados.get("nome"), dados.get("descricao"),
                              dados.get("duracao_min"), dados.get("preco"),
                              ativo=dados.get("ativo") == "1")
            flash("Serviço atualizado com sucesso.", "sucesso")
            return redirect(url_for("servicos.lista"))
        except ValidationError as erro:
            flash_erros(erro)
        atual = {**dados.to_dict(), "ativo": 1 if dados.get("ativo") == "1" else 0}
    return render_template("servicos/form.html", servico=atual, editando=True,
                           servico_id=servico_id)


@bp.route("/<int:servico_id>/excluir", methods=["POST"])
def excluir(servico_id):
    try:
        servico.excluir(get_db(), servico_id)
        flash("Serviço excluído.", "sucesso")
    except ValidationError as erro:
        flash_erros(erro)
    return redirect(url_for("servicos.lista"))
