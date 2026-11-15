"""Modelo Agendamento: regras de negócio centrais do sistema.

Regras de negócio implementadas
-------------------------------
RN01  Não é permitido agendar em data/hora passada.
RN02  O atendimento deve ocorrer dentro do horário de funcionamento
      (por padrão, seg-sáb, 08:00-18:00) e terminar até o fechamento.
RN03  O profissional não pode ter dois agendamentos sobrepostos.
RN04  O cliente não pode ter dois agendamentos sobrepostos.
RN05  O profissional deve estar ativo e realizar o serviço escolhido.
RN06  O serviço deve estar ativo.
RN07  O fim do atendimento é calculado: início + duração do serviço.
RN08  Só é possível cancelar/concluir agendamentos com status 'agendado'.
RN09  Só é possível concluir um atendimento que já começou.
"""
from datetime import datetime, timedelta

from ..errors import ValidationError

FORMATO = "%Y-%m-%d %H:%M"

REGRAS_PADRAO = {
    "HORA_ABERTURA": 8,
    "HORA_FECHAMENTO": 18,
    "PASSO_MIN": 30,
    "DIAS_FUNCIONAMENTO": (0, 1, 2, 3, 4, 5),  # 0 = segunda ... 5 = sábado
}

STATUS_VALIDOS = ("agendado", "concluido", "cancelado")


def _regras(regras):
    combinado = dict(REGRAS_PADRAO)
    if regras:
        combinado.update(regras)
    return combinado


def _converter(texto_data_hora):
    try:
        return datetime.strptime((texto_data_hora or "").strip(), FORMATO)
    except ValueError:
        raise ValidationError("Data/hora inválida. Use o formato AAAA-MM-DD HH:MM.")


def _erros_de_janela(inicio, fim, agora, regras):
    """Valida RN01 e RN02. Retorna lista de mensagens de erro."""
    erros = []
    if inicio <= agora:
        erros.append("Não é possível agendar em data/hora que já passou.")
    if inicio.weekday() not in regras["DIAS_FUNCIONAMENTO"]:
        erros.append("O estabelecimento não funciona neste dia da semana.")
    abertura = inicio.replace(hour=regras["HORA_ABERTURA"], minute=0)
    fechamento = inicio.replace(hour=regras["HORA_FECHAMENTO"], minute=0)
    if inicio < abertura or fim > fechamento:
        erros.append(
            "O atendimento deve ocorrer entre "
            f"{regras['HORA_ABERTURA']:02d}:00 e {regras['HORA_FECHAMENTO']:02d}:00."
        )
    return erros


def _conflito(db, coluna, valor, inicio, fim):
    """Há agendamento ativo sobreposto para a coluna (profissional/cliente)?"""
    linha = db.execute(
        f"SELECT 1 FROM agendamento WHERE {coluna} = ? AND status = 'agendado' "
        "AND inicio < ? AND fim > ?",
        (valor, fim.strftime(FORMATO), inicio.strftime(FORMATO)),
    ).fetchone()
    return linha is not None


def criar(db, cliente_id, profissional_id, servico_id, inicio, observacao="",
          agora=None, regras=None):
    agora = agora or datetime.now()
    regras = _regras(regras)
    inicio_dt = _converter(inicio)

    cliente = db.execute("SELECT id FROM cliente WHERE id = ?", (cliente_id,)).fetchone()
    profissional = db.execute(
        "SELECT * FROM profissional WHERE id = ?", (profissional_id,)
    ).fetchone()
    servico = db.execute("SELECT * FROM servico WHERE id = ?", (servico_id,)).fetchone()

    erros = []
    if cliente is None:
        erros.append("Selecione um cliente válido.")
    if servico is None:
        erros.append("Selecione um serviço válido.")
    elif not servico["ativo"]:
        erros.append("O serviço selecionado está inativo.")
    if profissional is None:
        erros.append("Selecione um profissional válido.")
    elif not profissional["ativo"]:
        erros.append("O profissional selecionado está inativo.")
    if erros:
        raise ValidationError(erros)

    realiza = db.execute(
        "SELECT 1 FROM profissional_servico WHERE profissional_id = ? AND servico_id = ?",
        (profissional_id, servico_id),
    ).fetchone()
    if not realiza:
        raise ValidationError("Este profissional não realiza o serviço selecionado.")

    fim_dt = inicio_dt + timedelta(minutes=servico["duracao_min"])
    erros = _erros_de_janela(inicio_dt, fim_dt, agora, regras)
    if erros:
        raise ValidationError(erros)

    if _conflito(db, "profissional_id", profissional_id, inicio_dt, fim_dt):
        raise ValidationError("O profissional já possui agendamento neste horário.")
    if _conflito(db, "cliente_id", cliente_id, inicio_dt, fim_dt):
        raise ValidationError("O cliente já possui agendamento neste horário.")

    cursor = db.execute(
        "INSERT INTO agendamento (cliente_id, profissional_id, servico_id, inicio, "
        "fim, observacao) VALUES (?, ?, ?, ?, ?, ?)",
        (cliente_id, profissional_id, servico_id, inicio_dt.strftime(FORMATO),
         fim_dt.strftime(FORMATO), (observacao or "").strip()),
    )
    db.commit()
    return cursor.lastrowid


def obter(db, agendamento_id):
    return db.execute(
        "SELECT * FROM agendamento WHERE id = ?", (agendamento_id,)
    ).fetchone()


def listar(db, data=None, profissional_id=None, status=None):
    sql = (
        "SELECT a.*, c.nome AS cliente_nome, p.nome AS profissional_nome, "
        "s.nome AS servico_nome, s.preco AS preco "
        "FROM agendamento a "
        "JOIN cliente c ON c.id = a.cliente_id "
        "JOIN profissional p ON p.id = a.profissional_id "
        "JOIN servico s ON s.id = a.servico_id WHERE 1 = 1 "
    )
    parametros = []
    if data:
        sql += "AND substr(a.inicio, 1, 10) = ? "
        parametros.append(data)
    if profissional_id:
        sql += "AND a.profissional_id = ? "
        parametros.append(profissional_id)
    if status in STATUS_VALIDOS:
        sql += "AND a.status = ? "
        parametros.append(status)
    sql += "ORDER BY a.inicio"
    return db.execute(sql, parametros).fetchall()


def _mudar_status(db, agendamento_id, novo_status, agora=None):
    agendamento = obter(db, agendamento_id)
    if agendamento is None:
        raise ValidationError("Agendamento não encontrado.")
    if agendamento["status"] != "agendado":
        raise ValidationError(
            f"Só é possível alterar agendamentos com status 'agendado' "
            f"(este está '{agendamento['status']}')."
        )
    if novo_status == "concluido":
        agora = agora or datetime.now()
        if _converter(agendamento["inicio"]) > agora:
            raise ValidationError("Não é possível concluir um atendimento que ainda não começou.")
    db.execute(
        "UPDATE agendamento SET status = ? WHERE id = ?", (novo_status, agendamento_id)
    )
    db.commit()


def cancelar(db, agendamento_id):
    _mudar_status(db, agendamento_id, "cancelado")


def concluir(db, agendamento_id, agora=None):
    _mudar_status(db, agendamento_id, "concluido", agora)


def horarios_disponiveis(db, profissional_id, servico_id, data, agora=None, regras=None):
    """Lista os horários ('HH:MM') livres para o profissional e serviço na data."""
    agora = agora or datetime.now()
    regras = _regras(regras)
    servico = db.execute("SELECT * FROM servico WHERE id = ?", (servico_id,)).fetchone()
    if servico is None:
        return []
    try:
        dia = datetime.strptime(data, "%Y-%m-%d")
    except (TypeError, ValueError):
        return []

    duracao = timedelta(minutes=servico["duracao_min"])
    atual = dia.replace(hour=regras["HORA_ABERTURA"], minute=0)
    limite = dia.replace(hour=regras["HORA_FECHAMENTO"], minute=0)
    livres = []
    while atual + duracao <= limite:
        fim = atual + duracao
        if (not _erros_de_janela(atual, fim, agora, regras)
                and not _conflito(db, "profissional_id", profissional_id, atual, fim)):
            livres.append(atual.strftime("%H:%M"))
        atual += timedelta(minutes=regras["PASSO_MIN"])
    return livres


def resumo(db, agora=None):
    """Indicadores para o painel inicial."""
    agora = agora or datetime.now()
    hoje = agora.strftime("%Y-%m-%d")
    consulta = lambda sql, p=(): db.execute(sql, p).fetchone()[0]  # noqa: E731
    return {
        "clientes": consulta("SELECT COUNT(*) FROM cliente"),
        "profissionais": consulta("SELECT COUNT(*) FROM profissional WHERE ativo = 1"),
        "servicos": consulta("SELECT COUNT(*) FROM servico WHERE ativo = 1"),
        "hoje": consulta(
            "SELECT COUNT(*) FROM agendamento WHERE status = 'agendado' "
            "AND substr(inicio, 1, 10) = ?", (hoje,)),
        "proximos": consulta(
            "SELECT COUNT(*) FROM agendamento WHERE status = 'agendado' AND inicio > ?",
            (agora.strftime(FORMATO),)),
    }
