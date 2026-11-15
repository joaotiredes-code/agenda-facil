# 5. Dicionário de Dados

## Tabela `cliente`
| Coluna | Tipo | Nulo | Chave | Restrições | Descrição |
|--------|------|------|-------|-----------|-----------|
| id | INTEGER | Não | PK | autoincremento | Identificador do cliente |
| nome | TEXT | Não | | mín. 3 caracteres | Nome completo |
| email | TEXT | Não | UK | único, formato válido | E-mail (gravado em minúsculas) |
| telefone | TEXT | Não | | 10 ou 11 dígitos | Telefone com DDD, só dígitos |
| criado_em | TEXT | Não | | padrão: data/hora atual | Data de cadastro |

## Tabela `servico`
| Coluna | Tipo | Nulo | Chave | Restrições | Descrição |
|--------|------|------|-------|-----------|-----------|
| id | INTEGER | Não | PK | autoincremento | Identificador do serviço |
| nome | TEXT | Não | UK | único, mín. 3 caracteres | Nome do serviço |
| descricao | TEXT | Sim | | | Descrição livre |
| duracao_min | INTEGER | Não | | entre 5 e 480 | Duração em minutos |
| preco | NUMERIC | Não | | ≥ 0 | Preço em reais |
| ativo | INTEGER | Não | | 0 ou 1; padrão 1 | 1 = disponível para agendamento |

## Tabela `profissional`
| Coluna | Tipo | Nulo | Chave | Restrições | Descrição |
|--------|------|------|-------|-----------|-----------|
| id | INTEGER | Não | PK | autoincremento | Identificador do profissional |
| nome | TEXT | Não | | mín. 3 caracteres | Nome |
| especialidade | TEXT | Sim | | máx. 60 (validado na aplicação) | Ex.: Barbeiro |
| ativo | INTEGER | Não | | 0 ou 1; padrão 1 | 1 = atende |

## Tabela `profissional_servico`
| Coluna | Tipo | Nulo | Chave | Restrições | Descrição |
|--------|------|------|-------|-----------|-----------|
| profissional_id | INTEGER | Não | PK, FK → profissional.id | ON DELETE CASCADE | Profissional |
| servico_id | INTEGER | Não | PK, FK → servico.id | ON DELETE CASCADE | Serviço que ele realiza |

## Tabela `agendamento`
| Coluna | Tipo | Nulo | Chave | Restrições | Descrição |
|--------|------|------|-------|-----------|-----------|
| id | INTEGER | Não | PK | autoincremento | Identificador |
| cliente_id | INTEGER | Não | FK → cliente.id | RESTRICT | Cliente atendido |
| profissional_id | INTEGER | Não | FK → profissional.id | RESTRICT | Profissional responsável |
| servico_id | INTEGER | Não | FK → servico.id | RESTRICT | Serviço contratado |
| inicio | TEXT | Não | | formato `AAAA-MM-DD HH:MM` | Início do atendimento |
| fim | TEXT | Não | | `fim > inicio` | Término (início + duração) |
| status | TEXT | Não | | `agendado`, `concluido` ou `cancelado`; padrão `agendado` | Situação |
| observacao | TEXT | Sim | | | Observações |
| criado_em | TEXT | Não | | padrão: data/hora atual | Data de criação |

## Domínios
| Domínio | Valores |
|---------|---------|
| status | `agendado`, `concluido`, `cancelado` |
| ativo | `0` (inativo), `1` (ativo) |
| formato de data/hora | `AAAA-MM-DD HH:MM` (ordenável como texto) |
