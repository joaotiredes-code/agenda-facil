"""Modelo Profissional: regras de negócio e persistência."""
from ..errors import ValidationError
from .validacao import texto


def _validar(nome, especialidade):
    erros = []
    nome = texto(nome)
    especialidade = texto(especialidade)
    if len(nome) < 3:
        erros.append("O nome do profissional deve ter pelo menos 3 caracteres.")
    if len(especialidade) > 60:
        erros.append("A especialidade deve ter no máximo 60 caracteres.")
    if erros:
        raise ValidationError(erros)
    return nome, especialidade


def _normalizar_servicos(db, servicos_ids):
    ids = set()
    for valor in servicos_ids or []:
        try:
            ids.add(int(valor))
        except (TypeError, ValueError):
            raise ValidationError("Serviço selecionado inválido.")
    for servico_id in ids:
        existe = db.execute("SELECT 1 FROM servico WHERE id = ?", (servico_id,)).fetchone()
        if not existe:
            raise ValidationError("Serviço selecionado não existe.")
    return ids


def _gravar_servicos(db, profissional_id, ids):
    db.execute(
        "DELETE FROM profissional_servico WHERE profissional_id = ?", (profissional_id,)
    )
    db.executemany(
        "INSERT INTO profissional_servico (profissional_id, servico_id) VALUES (?, ?)",
        [(profissional_id, servico_id) for servico_id in ids],
    )


def listar(db, apenas_ativos=False):
    sql = (
        "SELECT p.*, group_concat(s.nome, ', ') AS servicos "
        "FROM profissional p "
        "LEFT JOIN profissional_servico ps ON ps.profissional_id = p.id "
        "LEFT JOIN servico s ON s.id = ps.servico_id "
    )
    if apenas_ativos:
        sql += "WHERE p.ativo = 1 "
    sql += "GROUP BY p.id ORDER BY p.nome"
    return db.execute(sql).fetchall()


def obter(db, profissional_id):
    return db.execute(
        "SELECT * FROM profissional WHERE id = ?", (profissional_id,)
    ).fetchone()


def servicos_ids(db, profissional_id):
    linhas = db.execute(
        "SELECT servico_id FROM profissional_servico WHERE profissional_id = ?",
        (profissional_id,),
    ).fetchall()
    return [linha["servico_id"] for linha in linhas]


def por_servico(db, servico_id):
    """Profissionais ativos que realizam o serviço informado."""
    return db.execute(
        "SELECT p.id, p.nome FROM profissional p "
        "JOIN profissional_servico ps ON ps.profissional_id = p.id "
        "WHERE ps.servico_id = ? AND p.ativo = 1 ORDER BY p.nome",
        (servico_id,),
    ).fetchall()


def criar(db, nome, especialidade, servicos_ids_=None, ativo=True):
    nome, especialidade = _validar(nome, especialidade)
    ids = _normalizar_servicos(db, servicos_ids_)
    cursor = db.execute(
        "INSERT INTO profissional (nome, especialidade, ativo) VALUES (?, ?, ?)",
        (nome, especialidade, 1 if ativo else 0),
    )
    _gravar_servicos(db, cursor.lastrowid, ids)
    db.commit()
    return cursor.lastrowid


def atualizar(db, profissional_id, nome, especialidade, servicos_ids_=None, ativo=True):
    if obter(db, profissional_id) is None:
        raise ValidationError("Profissional não encontrado.")
    nome, especialidade = _validar(nome, especialidade)
    ids = _normalizar_servicos(db, servicos_ids_)
    db.execute(
        "UPDATE profissional SET nome = ?, especialidade = ?, ativo = ? WHERE id = ?",
        (nome, especialidade, 1 if ativo else 0, profissional_id),
    )
    _gravar_servicos(db, profissional_id, ids)
    db.commit()


def excluir(db, profissional_id):
    if obter(db, profissional_id) is None:
        raise ValidationError("Profissional não encontrado.")
    total = db.execute(
        "SELECT COUNT(*) FROM agendamento WHERE profissional_id = ?", (profissional_id,)
    ).fetchone()[0]
    if total:
        raise ValidationError(
            "Este profissional possui agendamentos e não pode ser excluído. "
            "Marque-o como inativo."
        )
    db.execute("DELETE FROM profissional WHERE id = ?", (profissional_id,))
    db.commit()
