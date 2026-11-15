-- ============================================================
-- Projeto físico do banco de dados - Sistema de Agendamento
-- SGBD: SQLite 3 (SQL padrão, portável para PostgreSQL/MySQL)
-- ============================================================
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cliente (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT    NOT NULL CHECK (length(nome) >= 3),
    email      TEXT    NOT NULL UNIQUE,
    telefone   TEXT    NOT NULL CHECK (length(telefone) IN (10, 11)),
    criado_em  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS servico (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT    NOT NULL UNIQUE CHECK (length(nome) >= 3),
    descricao    TEXT,
    duracao_min  INTEGER NOT NULL CHECK (duracao_min BETWEEN 5 AND 480),
    preco        NUMERIC NOT NULL CHECK (preco >= 0),
    ativo        INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS profissional (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT    NOT NULL CHECK (length(nome) >= 3),
    especialidade TEXT,
    ativo         INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

-- Relacionamento N:N entre profissional e serviço
CREATE TABLE IF NOT EXISTS profissional_servico (
    profissional_id INTEGER NOT NULL,
    servico_id      INTEGER NOT NULL,
    PRIMARY KEY (profissional_id, servico_id),
    FOREIGN KEY (profissional_id) REFERENCES profissional (id) ON DELETE CASCADE,
    FOREIGN KEY (servico_id)      REFERENCES servico (id)      ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agendamento (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id      INTEGER NOT NULL,
    profissional_id INTEGER NOT NULL,
    servico_id      INTEGER NOT NULL,
    inicio          TEXT    NOT NULL,   -- formato AAAA-MM-DD HH:MM
    fim             TEXT    NOT NULL,   -- formato AAAA-MM-DD HH:MM
    status          TEXT    NOT NULL DEFAULT 'agendado'
                    CHECK (status IN ('agendado', 'concluido', 'cancelado')),
    observacao      TEXT,
    criado_em       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    CHECK (fim > inicio),
    FOREIGN KEY (cliente_id)      REFERENCES cliente (id)      ON DELETE RESTRICT,
    FOREIGN KEY (profissional_id) REFERENCES profissional (id) ON DELETE RESTRICT,
    FOREIGN KEY (servico_id)      REFERENCES servico (id)      ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_agendamento_prof_inicio ON agendamento (profissional_id, inicio);
CREATE INDEX IF NOT EXISTS idx_agendamento_cliente     ON agendamento (cliente_id);
CREATE INDEX IF NOT EXISTS idx_agendamento_status      ON agendamento (status);
