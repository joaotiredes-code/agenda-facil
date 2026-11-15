# 2. Modelagem UML

## 2.1 Diagrama de casos de uso
```mermaid
flowchart LR
    A((Atendente))
    subgraph Sistema Agenda Fácil
      UC1([Gerenciar clientes])
      UC2([Gerenciar serviços])
      UC3([Gerenciar profissionais])
      UC4([Realizar agendamento])
      UC5([Consultar horários livres])
      UC6([Cancelar agendamento])
      UC7([Concluir atendimento])
      UC8([Consultar agendamentos])
      UC9([Visualizar painel])
    end
    A --- UC1
    A --- UC2
    A --- UC3
    A --- UC4
    A --- UC6
    A --- UC7
    A --- UC8
    A --- UC9
    UC4 -. include .-> UC5
```

### Especificação do caso de uso principal — UC04 Realizar agendamento
| Item | Descrição |
|------|-----------|
| Ator | Atendente |
| Pré-condição | Existir ao menos 1 cliente, 1 serviço ativo e 1 profissional ativo que realize o serviço |
| Fluxo principal | 1. Seleciona o cliente. 2. Seleciona o serviço. 3. Sistema lista os profissionais que o realizam. 4. Seleciona o profissional. 5. Escolhe a data. 6. Sistema lista os horários livres (UC05). 7. Escolhe o horário. 8. Confirma. 9. Sistema valida as regras e grava. 10. Sistema exibe a confirmação. |
| Fluxo alternativo A | Não há horários livres: o sistema informa e sugere outro dia/profissional. |
| Fluxo de exceção E1 | Violação de RN01–RN06 (ex.: conflito criado por outro usuário): o sistema exibe a mensagem de erro e mantém os dados preenchidos. |
| Pós-condição | Agendamento criado com situação "agendado". |

## 2.2 Diagrama de classes
```mermaid
classDiagram
    class Cliente {
        +int id
        +string nome
        +string email
        +string telefone
        +criar()
        +atualizar()
        +excluir()
    }
    class Profissional {
        +int id
        +string nome
        +string especialidade
        +bool ativo
        +criar()
        +atualizar()
        +excluir()
    }
    class Servico {
        +int id
        +string nome
        +string descricao
        +int duracaoMin
        +decimal preco
        +bool ativo
        +criar()
        +atualizar()
        +excluir()
    }
    class Agendamento {
        +int id
        +datetime inicio
        +datetime fim
        +string status
        +string observacao
        +criar()
        +cancelar()
        +concluir()
        +horariosDisponiveis()
    }
    Cliente "1" --> "0..*" Agendamento : realiza
    Profissional "1" --> "0..*" Agendamento : atende
    Servico "1" --> "0..*" Agendamento : é prestado em
    Profissional "0..*" -- "0..*" Servico : executa
```

## 2.3 Diagrama de sequência — Realizar agendamento
```mermaid
sequenceDiagram
    actor At as Atendente
    participant V as View (form.html + JS)
    participant C as Controller (agendamentos)
    participant M as Model (agendamento.py)
    participant B as Banco SQLite

    At->>V: Seleciona serviço
    V->>C: GET /profissionais/por-servico/{id}
    C->>M: por_servico()
    M->>B: SELECT profissionais
    B-->>M: linhas
    C-->>V: JSON de profissionais
    At->>V: Seleciona profissional e data
    V->>C: GET /agendamentos/horarios
    C->>M: horarios_disponiveis()
    M->>B: SELECT conflitos
    C-->>V: JSON com horários livres
    At->>V: Escolhe horário e confirma
    V->>C: POST /agendamentos/novo
    C->>M: criar()
    M->>M: valida RN01..RN06
    alt regra violada
        M-->>C: ValidationError
        C-->>V: formulário com mensagens de erro
    else válido
        M->>B: INSERT agendamento
        C-->>V: redireciona para a lista com mensagem de sucesso
    end
```

## 2.4 Diagrama de atividades — Validação do agendamento
```mermaid
flowchart TD
    I([Início]) --> A[Receber dados do formulário]
    A --> B{Cliente, serviço e<br/>profissional válidos e ativos?}
    B -- Não --> E[Exibir erro]
    B -- Sim --> C{Profissional realiza<br/>o serviço?}
    C -- Não --> E
    C -- Sim --> D[Calcular fim = início + duração]
    D --> F{Data futura e dentro<br/>do horário de funcionamento?}
    F -- Não --> E
    F -- Sim --> G{Profissional livre<br/>no intervalo?}
    G -- Não --> E
    G -- Sim --> H{Cliente livre<br/>no intervalo?}
    H -- Não --> E
    H -- Sim --> J[Gravar agendamento]
    J --> K[Exibir confirmação]
    E --> Z([Fim])
    K --> Z
```

## 2.5 Diagrama de estados — Agendamento
```mermaid
stateDiagram-v2
    [*] --> agendado : criar()
    agendado --> cancelado : cancelar()
    agendado --> concluido : concluir() após o início
    cancelado --> [*]
    concluido --> [*]
```
