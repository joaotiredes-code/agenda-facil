"""Testes unitários da camada Model (verificação das regras de negócio)."""
import unittest
from datetime import datetime

from app.errors import ValidationError
from app.models import agendamento, cliente, profissional, servico
from tests.base import BaseTeste

# Segunda-feira, 16/11/2026, 09:00 — "agora" fixo para os testes
AGORA = datetime(2026, 11, 16, 9, 0)


class TesteCliente(BaseTeste):
    def test_criar_cliente_valido(self):
        cid = cliente.criar(self.db, "  Maria Silva ", "MARIA@Exemplo.com", "(51) 99999-0000")
        c = cliente.obter(self.db, cid)
        self.assertEqual(c["nome"], "Maria Silva")
        self.assertEqual(c["email"], "maria@exemplo.com")
        self.assertEqual(c["telefone"], "51999990000")

    def test_nome_curto_e_email_invalido(self):
        with self.assertRaises(ValidationError) as ctx:
            cliente.criar(self.db, "Al", "sem-arroba", "123")
        self.assertEqual(len(ctx.exception.mensagens), 3)

    def test_email_duplicado(self):
        cliente.criar(self.db, "Maria Silva", "m@exemplo.com", "51999990000")
        with self.assertRaises(ValidationError) as ctx:
            cliente.criar(self.db, "Outra Maria", "m@exemplo.com", "51988880000")
        self.assertIn("e-mail", ctx.exception.mensagens[0])

    def test_atualizar_e_buscar(self):
        cid = cliente.criar(self.db, "Maria Silva", "m@exemplo.com", "51999990000")
        cliente.atualizar(self.db, cid, "Maria Souza", "m@exemplo.com", "5133334444")
        self.assertEqual(len(cliente.listar(self.db, "Souza")), 1)
        self.assertEqual(len(cliente.listar(self.db, "inexistente")), 0)

    def test_excluir_cliente_sem_agendamentos(self):
        cid = cliente.criar(self.db, "Maria Silva", "m@exemplo.com", "51999990000")
        cliente.excluir(self.db, cid)
        self.assertIsNone(cliente.obter(self.db, cid))

    def test_atualizar_cliente_inexistente(self):
        with self.assertRaises(ValidationError):
            cliente.atualizar(self.db, 999, "Maria Silva", "m@exemplo.com", "51999990000")


class TesteServico(BaseTeste):
    def test_criar_servico_com_virgula_no_preco(self):
        sid = servico.criar(self.db, "Corte", "", 30, "45,90")
        self.assertAlmostEqual(servico.obter(self.db, sid)["preco"], 45.90)

    def test_validacoes(self):
        with self.assertRaises(ValidationError) as ctx:
            servico.criar(self.db, "Co", "", "abc", "x")
        self.assertEqual(len(ctx.exception.mensagens), 3)
        with self.assertRaises(ValidationError):
            servico.criar(self.db, "Corte", "", 600, "10")      # duração acima do limite
        with self.assertRaises(ValidationError):
            servico.criar(self.db, "Corte", "", 30, "-5")       # preço negativo

    def test_nome_duplicado(self):
        servico.criar(self.db, "Corte", "", 30, "45")
        with self.assertRaises(ValidationError):
            servico.criar(self.db, "Corte", "", 20, "40")


class TesteProfissional(BaseTeste):
    def test_vinculo_com_servicos(self):
        s1 = servico.criar(self.db, "Corte", "", 30, "45")
        s2 = servico.criar(self.db, "Barba", "", 30, "30")
        pid = profissional.criar(self.db, "Bruno Lima", "Barbeiro", [s1, s2])
        self.assertCountEqual(profissional.servicos_ids(self.db, pid), [s1, s2])
        profissional.atualizar(self.db, pid, "Bruno Lima", "Barbeiro", [s1])
        self.assertEqual(profissional.servicos_ids(self.db, pid), [s1])
        self.assertEqual([p["id"] for p in profissional.por_servico(self.db, s1)], [pid])
        self.assertEqual(profissional.por_servico(self.db, s2), [])

    def test_servico_inexistente_no_vinculo(self):
        with self.assertRaises(ValidationError):
            profissional.criar(self.db, "Bruno Lima", "", [999])

    def test_inativo_nao_aparece_por_servico(self):
        s1 = servico.criar(self.db, "Corte", "", 30, "45")
        profissional.criar(self.db, "Bruno Lima", "", [s1], ativo=False)
        self.assertEqual(profissional.por_servico(self.db, s1), [])


class TesteAgendamento(BaseTeste):
    def setUp(self):
        super().setUp()
        self.corte = servico.criar(self.db, "Corte", "", 30, "45")
        self.combo = servico.criar(self.db, "Combo", "", 60, "70")
        self.barba = servico.criar(self.db, "Barba", "", 30, "30")
        self.prof = profissional.criar(self.db, "Bruno Lima", "", [self.corte, self.combo])
        self.prof2 = profissional.criar(self.db, "Ana Souza", "", [self.corte])
        self.cli = cliente.criar(self.db, "Maria Silva", "m@exemplo.com", "51999990000")
        self.cli2 = cliente.criar(self.db, "João Pedro", "j@exemplo.com", "51988880000")

    def agendar(self, inicio, cli=None, prof=None, serv=None):
        return agendamento.criar(
            self.db, cli or self.cli, prof or self.prof, serv or self.corte, inicio, agora=AGORA
        )

    def test_agendamento_valido_calcula_fim(self):
        aid = self.agendar("2026-11-17 10:00", serv=self.combo)
        a = agendamento.obter(self.db, aid)
        self.assertEqual(a["fim"], "2026-11-17 11:00")   # RN07
        self.assertEqual(a["status"], "agendado")

    def test_rn01_nao_agenda_no_passado(self):
        with self.assertRaises(ValidationError) as ctx:
            self.agendar("2026-11-16 08:30")
        self.assertIn("passou", ctx.exception.mensagens[0])

    def test_rn02_domingo_fechado(self):
        with self.assertRaises(ValidationError):
            self.agendar("2026-11-22 10:00")   # domingo

    def test_rn02_fora_do_horario(self):
        with self.assertRaises(ValidationError):
            self.agendar("2026-11-17 07:30")   # antes de abrir
        with self.assertRaises(ValidationError):
            self.agendar("2026-11-17 17:45")   # terminaria às 18:15
        self.agendar("2026-11-17 17:30")       # termina exatamente às 18:00: válido

    def test_rn03_conflito_profissional(self):
        self.agendar("2026-11-17 10:00", serv=self.combo)           # 10:00-11:00
        with self.assertRaises(ValidationError) as ctx:
            self.agendar("2026-11-17 10:30", cli=self.cli2)          # sobrepõe
        self.assertIn("profissional", ctx.exception.mensagens[0])
        self.agendar("2026-11-17 11:00", cli=self.cli2)              # encosta, sem sobrepor

    def test_rn04_conflito_cliente(self):
        self.agendar("2026-11-17 10:00")
        with self.assertRaises(ValidationError) as ctx:
            self.agendar("2026-11-17 10:00", prof=self.prof2)        # mesmo cliente, outro profissional
        self.assertIn("cliente", ctx.exception.mensagens[0])

    def test_rn05_profissional_nao_realiza_servico(self):
        with self.assertRaises(ValidationError) as ctx:
            self.agendar("2026-11-17 10:00", serv=self.barba)
        self.assertIn("não realiza", ctx.exception.mensagens[0])

    def test_rn05_profissional_inativo(self):
        profissional.atualizar(self.db, self.prof, "Bruno Lima", "", [self.corte], ativo=False)
        with self.assertRaises(ValidationError):
            self.agendar("2026-11-17 10:00")

    def test_rn06_servico_inativo(self):
        servico.atualizar(self.db, self.corte, "Corte", "", 30, "45", ativo=False)
        with self.assertRaises(ValidationError):
            self.agendar("2026-11-17 10:00")

    def test_data_hora_invalida_e_ids_invalidos(self):
        with self.assertRaises(ValidationError):
            agendamento.criar(self.db, self.cli, self.prof, self.corte, "ontem", agora=AGORA)
        with self.assertRaises(ValidationError) as ctx:
            agendamento.criar(self.db, 999, 999, 999, "2026-11-17 10:00", agora=AGORA)
        self.assertEqual(len(ctx.exception.mensagens), 3)

    def test_rn08_cancelar_libera_horario(self):
        aid = self.agendar("2026-11-17 10:00")
        agendamento.cancelar(self.db, aid)
        self.assertEqual(agendamento.obter(self.db, aid)["status"], "cancelado")
        self.agendar("2026-11-17 10:00", cli=self.cli2)   # horário liberado
        with self.assertRaises(ValidationError):
            agendamento.cancelar(self.db, aid)             # já cancelado

    def test_rn09_concluir_so_depois_de_comecar(self):
        aid = self.agendar("2026-11-17 10:00")
        with self.assertRaises(ValidationError):
            agendamento.concluir(self.db, aid, agora=AGORA)
        agendamento.concluir(self.db, aid, agora=datetime(2026, 11, 17, 10, 40))
        self.assertEqual(agendamento.obter(self.db, aid)["status"], "concluido")

    def test_horarios_disponiveis(self):
        livres = agendamento.horarios_disponiveis(
            self.db, self.prof, self.corte, "2026-11-17", agora=AGORA)
        self.assertEqual(livres[0], "08:00")
        self.assertEqual(livres[-1], "17:30")
        self.assertEqual(len(livres), 20)
        self.agendar("2026-11-17 08:00", serv=self.combo)   # ocupa 08:00-09:00
        livres = agendamento.horarios_disponiveis(
            self.db, self.prof, self.corte, "2026-11-17", agora=AGORA)
        self.assertNotIn("08:00", livres)
        self.assertNotIn("08:30", livres)
        self.assertEqual(livres[0], "09:00")

    def test_horarios_domingo_e_data_invalida(self):
        self.assertEqual(agendamento.horarios_disponiveis(
            self.db, self.prof, self.corte, "2026-11-22", agora=AGORA), [])
        self.assertEqual(agendamento.horarios_disponiveis(
            self.db, self.prof, self.corte, "xx", agora=AGORA), [])

    def test_integridade_referencial_bloqueia_exclusoes(self):
        self.agendar("2026-11-17 10:00")
        with self.assertRaises(ValidationError):
            cliente.excluir(self.db, self.cli)
        with self.assertRaises(ValidationError):
            profissional.excluir(self.db, self.prof)
        with self.assertRaises(ValidationError):
            servico.excluir(self.db, self.corte)

    def test_listar_com_filtros_e_resumo(self):
        self.agendar("2026-11-17 10:00")
        self.agendar("2026-11-18 10:00", cli=self.cli2)
        self.assertEqual(len(agendamento.listar(self.db)), 2)
        self.assertEqual(len(agendamento.listar(self.db, data="2026-11-17")), 1)
        self.assertEqual(len(agendamento.listar(self.db, profissional_id=self.prof2)), 0)
        self.assertEqual(len(agendamento.listar(self.db, status="cancelado")), 0)
        r = agendamento.resumo(self.db, AGORA)
        self.assertEqual((r["clientes"], r["proximos"], r["hoje"]), (2, 2, 0))


if __name__ == "__main__":
    unittest.main()
