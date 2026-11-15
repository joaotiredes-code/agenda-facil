# 📅 Agenda Fácil

Sistema web de **agendamento de serviços** (barbearias, salões, clínicas…) desenvolvido para o
**Projeto Integrador Transdisciplinar em Engenharia de Software II**.

Python · Flask · SQLite · HTML/CSS/JavaScript · arquitetura **MVC** · testes com `unittest`.

## Funcionalidades
- Cadastro de clientes, serviços e profissionais (com vínculo profissional × serviço)
- Agendamento com **horários livres calculados automaticamente**
- Bloqueio de conflitos de agenda (profissional e cliente), horário de funcionamento e datas passadas
- Cancelar e concluir atendimentos; filtros por data, profissional e situação
- Painel com indicadores e agenda do dia

## Como executar
Requisitos: Python 3.10 ou superior.

```bash
# 1. (opcional) ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. dependências
pip install -r requirements.txt

# 3. (opcional) dados de demonstração
flask --app run seed

# 4. iniciar
python run.py
```
Acesse <http://127.0.0.1:5000>. O banco (`instance/agendamento.db`) é criado automaticamente.

## Testes
```bash
python -m unittest discover -s tests -t . -v
```

## Estrutura
```
app/
  models/        # Model: regras de negócio + acesso ao banco
  views/templates/  # View: telas HTML (Jinja2)
  static/        # CSS e JavaScript
  controllers/   # Controller: rotas Flask
database/schema.sql   # projeto físico do banco
tests/           # testes unitários e de integração
docs/            # documentação do projeto (organizada por Situação-Problema)
```

## Documentação
| Arquivo | Conteúdo | Situação |
|---------|----------|----------|
| `docs/situacao-1-planejamento` | Escopo, requisitos, regras de negócio, arquitetura | 1 |
| `docs/situacao-2-desenvolvimento` | Casos de uso, classes, sequência, atividades, estados | 1 |
| `docs/situacao-3-testes-validacao` | Princípios de IHC, telas, mensagens, protótipo | 1 |
| `docs/04-banco-de-dados.md` | Projeto conceitual, lógico (normalizado) e físico | 1 |
| `docs/05-dicionario-dados.md` | Dicionário de dados | 1 |
| `docs/06-plano-de-testes.md` | Verificação e validação | 2 e 3 |
| `docs/07-teste-com-usuarios.md` | Formulário e consolidação dos 5 testes | 3 |
| `docs/08-roteiro-videos.md` | Roteiro dos vídeos | 2 e 3 |

## Autor
Nome do estudante — Curso de Engenharia de Software