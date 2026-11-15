"""Testes de integração: rotas (Controller) + templates (View) + banco (Model)."""
import unittest
from datetime import date, timedelta

from app.models import cliente, profissional, servico
from tests.base import BaseTeste


def proximo_dia_util():
    dia = date.today() + timedelta(days=1)
    while dia.weekday() == 6:
        dia += timedelta(days=1)
    return dia.isoformat()


class TesteRotas(BaseTeste):
    def setUp(self):
        super().setUp()
        self.http = self.app.test_client()

    def test_paginas_principais_respondem(self):
        for url in ["/", "/clientes/", "/clientes/novo", "/servicos/", "/servicos/novo",
                    "/profissionais/", "/profissionais/novo", "/agendamentos/",
                    "/agendamentos/novo"]:
            with self.subTest(url=url):
                self.assertEqual(self.http.get(url).status_code, 200)

    def test_pagina_inexistente_retorna_404_amigavel(self):
        r = self.http.get("/nao-existe")
        self.assertEqual(r.status_code, 404)
        self.assertIn("Página não encontrada", r.get_data(as_text=True))
        self.assertEqual(self.http.get("/clientes/999/editar").status_code, 404)

    def test_cadastro_de_cliente_via_formulario(self):
        r = self.http.post("/clientes/novo", data={
            "nome": "Maria Silva", "email": "m@exemplo.com", "telefone": "(51) 99999-0000"},
            follow_redirects=True)
        corpo = r.get_data(as_text=True)
        self.assertIn("Cliente cadastrado com sucesso", corpo)
        self.assertIn("Maria Silva", corpo)
        self.assertIn("(51) 99999-0000", corpo)

    def test_cliente_invalido_exibe_erros_e_mantem_dados(self):
        r = self.http.post("/clientes/novo", data={"nome": "Al", "email": "x", "telefone": "1"})
        corpo = r.get_data(as_text=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn("pelo menos 3 caracteres", corpo)
        self.assertIn("e-mail válido", corpo)
        self.assertIn('value="Al"', corpo)

    def test_editar_e_excluir_cliente(self):
        cid = cliente.criar(self.db, "Maria Silva", "m@exemplo.com", "51999990000")
        r = self.http.post(f"/clientes/{cid}/editar", data={
            "nome": "Maria Souza", "email": "m@exemplo.com", "telefone": "51999990000"},
            follow_redirects=True)
        self.assertIn("Maria Souza", r.get_data(as_text=True))
        r = self.http.post(f"/clientes/{cid}/excluir", follow_redirects=True)
        self.assertIn("Cliente excluído", r.get_data(as_text=True))

    def test_cadastro_servico_e_profissional(self):
        self.http.post("/servicos/novo", data={
            "nome": "Corte", "descricao": "", "duracao_min": "30", "preco": "45,00", "ativo": "1"})
        sid = servico.listar(self.db)[0]["id"]
        r = self.http.post("/profissionais/novo", data={
            "nome": "Bruno Lima", "especialidade": "Barbeiro", "servicos": [str(sid)], "ativo": "1"},
            follow_redirects=True)
        corpo = r.get_data(as_text=True)
        self.assertIn("Profissional cadastrado com sucesso", corpo)
        self.assertIn("Corte", corpo)

    def test_api_json_profissionais_por_servico_e_horarios(self):
        sid = servico.criar(self.db, "Corte", "", 30, "45")
        pid = profissional.criar(self.db, "Bruno Lima", "", [sid])
        r = self.http.get(f"/profissionais/por-servico/{sid}")
        self.assertEqual(r.get_json(), [{"id": pid, "nome": "Bruno Lima"}])
        r = self.http.get(
            f"/agendamentos/horarios?profissional_id={pid}&servico_id={sid}&data={proximo_dia_util()}")
        horarios = r.get_json()
        self.assertIn("08:00", horarios)
        self.assertIn("17:30", horarios)

    def test_fluxo_completo_de_agendamento_e_conflito(self):
        sid = servico.criar(self.db, "Corte", "", 30, "45")
        pid = profissional.criar(self.db, "Bruno Lima", "", [sid])
        c1 = cliente.criar(self.db, "Maria Silva", "m@exemplo.com", "51999990000")
        c2 = cliente.criar(self.db, "João Pedro", "j@exemplo.com", "51988880000")
        dados = {"cliente_id": c1, "servico_id": sid, "profissional_id": pid,
                 "data": proximo_dia_util(), "horario": "10:00", "observacao": ""}

        r = self.http.post("/agendamentos/novo", data=dados, follow_redirects=True)
        self.assertIn("Agendamento realizado com sucesso", r.get_data(as_text=True))

        # mesmo horário para outro cliente: conflito do profissional
        dados["cliente_id"] = c2
        r = self.http.post("/agendamentos/novo", data=dados)
        self.assertIn("já possui agendamento neste horário", r.get_data(as_text=True))

        # horário agendado some da lista de livres
        r = self.http.get(
            f"/agendamentos/horarios?profissional_id={pid}&servico_id={sid}&data={dados['data']}")
        self.assertNotIn("10:00", r.get_json())

    def test_cancelar_agendamento(self):
        sid = servico.criar(self.db, "Corte", "", 30, "45")
        pid = profissional.criar(self.db, "Bruno Lima", "", [sid])
        cid = cliente.criar(self.db, "Maria Silva", "m@exemplo.com", "51999990000")
        self.http.post("/agendamentos/novo", data={
            "cliente_id": cid, "servico_id": sid, "profissional_id": pid,
            "data": proximo_dia_util(), "horario": "09:00"})
        r = self.http.post("/agendamentos/1/cancelar", follow_redirects=True)
        corpo = r.get_data(as_text=True)
        self.assertIn("Agendamento cancelado", corpo)
        self.assertIn("Cancelado", corpo)

    def test_agendamento_sem_campos_mostra_erro(self):
        r = self.http.post("/agendamentos/novo", data={})
        self.assertEqual(r.status_code, 200)
        self.assertIn("alert", r.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
