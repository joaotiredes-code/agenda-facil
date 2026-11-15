# 6. Plano de Testes — Verificação e Validação

## 6.1 Estratégia (Modelo V)
| Nível | Objetivo | Tipo | Como é feito neste projeto |
|-------|----------|------|----------------------------|
| Código | Verificar cada unidade | Teste unitário | `tests/test_models.py` (`unittest`) |
| Arquitetura | Verificar a integração das camadas | Teste de integração | `tests/test_controllers.py` (cliente HTTP de teste do Flask) |
| Sistema | Verificar o sistema completo | Teste manual | Roteiro da seção 6.4 |
| Aceitação | Validar com usuários reais | Teste de aceitação | 5 testadores (`07-teste-com-usuarios.md`) |

- **Verificação:** "estamos construindo certo?" — revisão do código, testes unitários e de integração.
- **Validação:** "estamos construindo o produto certo?" — testes de aceitação por usuários.

## 6.2 Como executar
```bash
python -m unittest discover -s tests -t . -v
```

## 6.3 Casos de teste automatizados (38)
| Área | Casos | Regras cobertas |
|------|-------|-----------------|
| Cliente (6) | criação válida e normalização; nome/e-mail/telefone inválidos; e-mail duplicado; atualização e busca; exclusão; atualização de inexistente | RF01, RN10 |
| Serviço (3) | preço com vírgula; validações (nome, duração, preço); nome duplicado | RF02, RN10 |
| Profissional (3) | vínculo com serviços; serviço inexistente; inativo não aparece | RF03, RN05 |
| Agendamento (15) | cálculo do fim; passado; domingo; fora do expediente; conflito de profissional; conflito de cliente; profissional não realiza serviço; profissional inativo; serviço inativo; data/ids inválidos; cancelar libera horário; concluir após o início; horários disponíveis; domingo/data inválida; integridade referencial; filtros e resumo | RF04–RF08, RN01–RN09, RN11 |
| Rotas/telas (11) | páginas respondem 200; 404 amigável; cadastro via formulário; erros e preservação dos dados; editar/excluir; serviço + profissional; APIs JSON; fluxo completo com conflito; cancelamento; formulário vazio | RF01–RF09 |

## 6.4 Roteiro de teste manual (sistema)
| # | Passo | Resultado esperado |
|---|-------|--------------------|
| 1 | Cadastrar serviço "Corte" (30 min, R$ 45,00) | Mensagem de sucesso; aparece na lista |
| 2 | Cadastrar profissional vinculado ao serviço | Aparece na lista com o serviço |
| 3 | Cadastrar cliente com e-mail inválido | Mensagem de erro; dados preenchidos mantidos |
| 4 | Cadastrar cliente válido | Mensagem de sucesso |
| 5 | Novo agendamento: escolher serviço | Profissionais carregam automaticamente |
| 6 | Escolher profissional e data | Horários livres carregam |
| 7 | Confirmar agendamento | Mensagem de sucesso; aparece na lista |
| 8 | Repetir o mesmo horário com outro cliente | O horário não é oferecido; se forçado, erro de conflito |
| 9 | Cancelar o agendamento | Confirmação; situação "Cancelado"; horário volta a ficar livre |
| 10 | Tentar excluir cliente com agendamento | Mensagem de bloqueio |
| 11 | Acessar `/rota-inexistente` | Página 404 amigável |
| 12 | Reduzir a janela do navegador (celular) | Layout se adapta |

## 6.5 Resultado da execução
> Execução automatizada: **38 testes, 0 falhas** (registre aqui a data e a captura de tela da sua execução).
> Execução manual: preencha a coluna abaixo ao testar.

| # | Passou? | Observações |
|---|---------|-------------|
| 1–12 | ☐ | |
