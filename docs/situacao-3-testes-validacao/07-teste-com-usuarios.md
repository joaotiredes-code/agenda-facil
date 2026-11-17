# 7. Teste com Usuários (Validação)

## 7.1 Como conduzir
1. Escolha **5 colegas de curso ou profissionais da área**.
2. Envie a eles o endereço do sistema (ou o link do repositório com as instruções de execução) e o **formulário** abaixo (um por testador).
3. Peça que testem as funcionalidades da lista da seção 7.3 e anexem **prints das telas com erro**.
4. Recolha os cinco formulários, consolide na tabela 7.4, aplique as correções pertinentes e registre-as na seção 7.5.
5. Entregue o **PDF com as 5 opiniões** e o **vídeo** mostrando as mudanças adotadas.

> Não esconda falhas: elas fazem parte da avaliação do seu aprendizado.

## 7.2 Formulário de teste (copie um para cada testador)

**Sistema:** Agenda Fácil  **Versão:** 1.0

| Campo | Preenchimento |
|-------|---------------|
| Nome de quem testou | |
| Data do teste | |
| Perfil (colega / profissional da área) | |
| Dispositivo e navegador | |

**A) O que foi testado e funcionou**
| Funcionalidade | Descrição do que funcionou |
|----------------|----------------------------|
| | |

**B) O que foi testado e NÃO funcionou**
| Funcionalidade | O que aconteceu | O que deve ser corrigido | Print anexo? |
|----------------|-----------------|--------------------------|--------------|
| | | | |

**C) Funcionalidade não testada**
| Funcionalidade | Por que não foi testada (faltou tempo / não encontrei / existe no projeto mas não foi realizada) |
|----------------|--------------------------------------------------------------------------------------------------|
| | |

**D) Sugestões de melhoria:**

**E) Nota de usabilidade (1 a 5):** ____

## 7.3 Funcionalidades a testar
Cadastro/edição/exclusão de cliente · Cadastro de serviço · Cadastro de profissional e vínculo com serviços · Novo agendamento (fluxo completo) · Conflito de horário · Cancelar e concluir · Filtros da lista · Busca de clientes · Uso no celular.

## 7.4 Consolidação dos resultados

Foram recebidas **5 respostas** pelo Google Formulários (PDF original das respostas anexado à entrega). Os textos abaixo resumem o que cada testador escreveu.

| # | Testador | Data informada | Dispositivo | O que funcionou | O que não funcionou | Não testado | Sugestões | Nota (1–5) |
|---|----------|----------------|-------------|-----------------|---------------------|-------------|-----------|-----------|
| 1 | Demenson dos Santos Castro | 16/11/2026 (*) | Notebook, Chrome | Cadastro de todos os funcionários (profissionais) | Nada informado | Informou que testou todas as funcionalidades | "Nenhuma no momento" | 5 |
| 2 | Fagner Clyff | 16/11/2026 | Notebook | Cadastros e serviços | Nada relatado como falha ("funcionamento dentro das expectativas") | Informou que tudo funcionou | Layout | 3 |
| 3 | Fernando Silva Sousa | 15/11/2026 | Notebook | Cadastro de clientes e de serviços | Nada relatado ("até o momento tudo funcionou normalmente") | Nenhuma que considere necessária | Aplicativo mobile | 5 |
| 4 | Jose Carlos | 16/11/2026 | Notebook | Cadastro de clientes, serviços e funcionários | Nada relatado ("bem simples e funcional") | Acredita ter testado todas | Nenhuma no momento | 5 |
| 5 | Carol Fontinele | 16/11/2026 | Notebook | Cadastro de serviços e precificação | Nada relatado ("funcionou muito bem") | Cadastro de clientes (faltou tempo) | Nenhuma | 5 |

(*) No formulário original (PDF das respostas), o testador 1 preencheu por engano a própria data de nascimento (14/05/2000) no campo "Data do teste". A data foi corrigida para 16/11/2026, conforme informado pelo testador ao autor.

**Resumo:** nenhum defeito foi reportado. Nota média de usabilidade: **4,6** (5, 3, 5, 5, 5). Dispositivo: notebook em todos os testes (nenhum teste em celular).

## 7.5 Análise dos resultados

**Pontos positivos:** os testadores consideraram o sistema simples e funcional, e os cadastros de serviços, clientes e profissionais funcionaram nos testes feitos.

**Limitações dos testes (honestidade sobre a cobertura):**
- As respostas são genéricas. Nenhum testador descreveu ter testado o **fluxo de agendamento**, o **bloqueio de conflito de horário**, o **cancelamento/conclusão**, os **filtros** da lista de agendamentos ou o **uso no celular**. Esses itens, que são o núcleo do sistema, não ficaram validados por usuários externos neste ciclo.
- Alguns testadores afirmaram ter testado "todas as funcionalidades" sem detalhar quais.
- Respostas positivas foram escritas no campo "O que não funcionou" (testadores 2, 3, 4 e 5), o que indica falha de clareza na pergunta do formulário.
- O testador 5 não testou o cadastro de clientes por falta de tempo.
- Todos os testes foram em notebook.

**Cobertura por funcionalidade (segundo o que foi descrito):**
| Funcionalidade | Citada como testada por |
|----------------|-------------------------|
| Cadastro de clientes | Testadores 3 e 4 |
| Cadastro de serviços | Testadores 2, 3, 4 e 5 |
| Cadastro de profissionais | Testadores 1 e 4 |
| Novo agendamento, conflito, cancelar/concluir, filtros, celular | Nenhum testador descreveu |

## 7.6 Correções e melhorias adotadas

| # | Origem | Sugestão/problema | Decisão | Justificativa |
|---|--------|-------------------|---------|---------------|
| 1 | Testador 2 | "Layout" | Pendente de detalhamento | A sugestão é vaga. Sem saber o que incomodou (cores, espaçamento, organização), não há como corrigir com segurança. Registrada como melhoria futura. |
| 2 | Testador 3 | Aplicativo mobile | Não adotada nesta versão | Fora do escopo (ver `01-escopo-requisitos.md`, seção 1.7). A interface já é responsiva e funciona no navegador do celular; app nativo fica para versões futuras. |
| 3 | Todos | Nenhum defeito reportado | Sem alterações no código | Não houve erro para corrigir. Os 38 testes automatizados continuam passando. |
| 4 | Análise do autor | Cobertura incompleta dos testes (agendamento, conflito, cancelar/concluir, filtros, celular) | Registrada como limitação | Esses fluxos são cobertos pelos testes automatizados (`tests/`) e pelo roteiro manual do plano de testes, mas não foram validados por usuários externos neste ciclo. |
| 5 | Análise do autor | Pergunta "O que não funcionou" gerou respostas positivas | Melhoria no processo | Em próximos ciclos, o formulário deve trazer a opção "Nada falhou" e listar as funcionalidades com caixas de seleção. |

> Teste do autor (opcional, separado dos 5 testadores): se você mesmo executou o roteiro manual do `06-plano-de-testes.md`, registre aqui, com seu nome, quais passos passaram ou falharam.
