"""Dados de demonstração (opcional)."""
from datetime import datetime, timedelta

from .models import agendamento, cliente, profissional, servico


def _proximo_dia_util(base, dias_a_frente):
    dia = base
    contados = 0
    while contados < dias_a_frente:
        dia += timedelta(days=1)
        if dia.weekday() != 6:  # pula domingo
            contados += 1
    return dia


def popular(db, agora=None):
    agora = agora or datetime.now()
    corte = servico.criar(db, "Corte de cabelo", "Corte masculino ou feminino", 30, "45,00")
    barba = servico.criar(db, "Barba", "Barba com toalha quente", 30, "30,00")
    combo = servico.criar(db, "Corte + Barba", "Combo completo", 60, "70,00")
    hidratacao = servico.criar(db, "Hidratação", "Tratamento capilar", 45, "55,00")

    ana = profissional.criar(db, "Ana Souza", "Cabeleireira", [corte, hidratacao, combo])
    bruno = profissional.criar(db, "Bruno Lima", "Barbeiro", [corte, barba, combo])

    c1 = cliente.criar(db, "Carlos Pereira", "carlos@exemplo.com", "(51) 99999-1111")
    c2 = cliente.criar(db, "Marina Costa", "marina@exemplo.com", "(51) 98888-2222")
    c3 = cliente.criar(db, "João Almeida", "joao@exemplo.com", "(51) 3333-4444")

    # Atendimento antigo já concluído (inserido direto, pois está no passado)
    ontem = (agora - timedelta(days=2)).strftime("%Y-%m-%d")
    db.execute(
        "INSERT INTO agendamento (cliente_id, profissional_id, servico_id, inicio, fim, status) "
        "VALUES (?, ?, ?, ?, ?, 'concluido')",
        (c1, bruno, barba, f"{ontem} 10:00", f"{ontem} 10:30"),
    )
    db.commit()

    d1 = _proximo_dia_util(agora, 1).strftime("%Y-%m-%d")
    d2 = _proximo_dia_util(agora, 2).strftime("%Y-%m-%d")
    agendamento.criar(db, c1, bruno, combo, f"{d1} 10:00", agora=agora)
    agendamento.criar(db, c2, ana, hidratacao, f"{d1} 14:00", agora=agora)
    agendamento.criar(db, c3, bruno, corte, f"{d2} 09:00", agora=agora)
