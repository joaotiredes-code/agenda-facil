"""Controlador de Clientes."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..db import get_db
from ..errors import ValidationError
from ..models import cliente
from .helpers import flash_erros

bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@bp.route("/")
def lista():
    busca = request.args.get("busca", "").strip()
    return render_template(
        "clientes/lista.html", clientes=cliente.listar(get_db(), busca), busca=busca
    )


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    dados = request.form
    if request.method == "POST":
        try:
            cliente.criar(get_db(), dados.get("nome"), dados.get("email"), dados.get("telefone"))
            flash("Cliente cadastrado com sucesso.", "sucesso")
            return redirect(url_for("clientes.lista"))
        except ValidationError as erro:
            flash_erros(erro)
    return render_template("clientes/form.html", cliente=dados, editando=False)


@bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
def editar(cliente_id):
    db = get_db()
    atual = cliente.obter(db, cliente_id)
    if atual is None:
        abort(404)
    if request.method == "POST":
        dados = request.form
        try:
            cliente.atualizar(db, cliente_id, dados.get("nome"), dados.get("email"),
                              dados.get("telefone"))
            flash("Cliente atualizado com sucesso.", "sucesso")
            return redirect(url_for("clientes.lista"))
        except ValidationError as erro:
            flash_erros(erro)
        atual = dados
    return render_template("clientes/form.html", cliente=atual, editando=True,
                           cliente_id=cliente_id)


@bp.route("/<int:cliente_id>/excluir", methods=["POST"])
def excluir(cliente_id):
    try:
        cliente.excluir(get_db(), cliente_id)
        flash("Cliente excluído.", "sucesso")
    except ValidationError as erro:
        flash_erros(erro)
    return redirect(url_for("clientes.lista"))
