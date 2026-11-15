"""Fábrica da aplicação Flask (padrão MVC)."""
import os
from datetime import datetime

import click
from flask import Flask, render_template

from . import db


def create_app(config=None):
    app = Flask(
        __name__,
        template_folder="views/templates",  # camada View
        static_folder="static",
        instance_relative_config=True,
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-troque-em-producao"),
        DATABASE=os.path.join(app.instance_path, "agendamento.db"),
        HORA_ABERTURA=8,
        HORA_FECHAMENTO=18,
        PASSO_MIN=30,
        DIAS_FUNCIONAMENTO=(0, 1, 2, 3, 4, 5),
    )
    if config:
        app.config.update(config)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    with app.app_context():
        db.init_schema()

    from .controllers import agendamentos, clientes, main, profissionais, servicos

    for modulo in (main, clientes, servicos, profissionais, agendamentos):
        app.register_blueprint(modulo.bp)

    registrar_filtros(app)
    registrar_erros(app)
    registrar_comandos(app)
    return app


def registrar_filtros(app):
    @app.template_filter("brl")
    def brl(valor):
        texto = f"{float(valor):,.2f}"
        return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")

    @app.template_filter("datahora")
    def datahora(valor):
        try:
            return datetime.strptime(valor, "%Y-%m-%d %H:%M").strftime("%d/%m/%Y %H:%M")
        except (TypeError, ValueError):
            return valor

    @app.template_filter("telefone")
    def telefone(valor):
        v = valor or ""
        if len(v) == 11:
            return f"({v[:2]}) {v[2:7]}-{v[7:]}"
        if len(v) == 10:
            return f"({v[:2]}) {v[2:6]}-{v[6:]}"
        return v


def registrar_erros(app):
    @app.errorhandler(404)
    def nao_encontrado(_erro):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def erro_interno(_erro):
        return render_template("500.html"), 500


def registrar_comandos(app):
    @app.cli.command("seed")
    def seed():
        """Popula o banco com dados de demonstração."""
        from .seed import popular

        popular(db.get_db())
        click.echo("Dados de demonstração criados.")
