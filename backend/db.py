"""SQLite simples — nenhum dado sai da maquina."""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime

DB_PATH = os.environ.get("NOTAS_DB", os.path.join(os.path.dirname(__file__), "..", "data", "notas.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS recibos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor TEXT NOT NULL,
    data TEXT,
    valor REAL NOT NULL,
    categoria TEXT NOT NULL DEFAULT 'outros',
    confianca REAL DEFAULT 0.0,
    origem TEXT DEFAULT 'upload',
    arquivo TEXT,
    criado_em TEXT NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def insert_recibo(fornecedor: str, data: str | None, valor: float,
                  categoria: str = "outros", confianca: float = 0.0,
                  origem: str = "upload", arquivo: str | None = None) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO recibos (fornecedor, data, valor, categoria, confianca, origem, arquivo, criado_em)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (fornecedor, data, valor, categoria, confianca, origem, arquivo,
             datetime.now().isoformat(timespec="seconds")),
        )
        return cur.lastrowid


def list_recibos(limit: int = 100) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM recibos ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def resumo_mensal(mes: str) -> dict:
    """mes no formato AAAA-MM. Agrega por categoria."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT categoria, COUNT(*) AS qtd, SUM(valor) AS total FROM recibos"
            " WHERE substr(data, 1, 7) = ? GROUP BY categoria ORDER BY total DESC",
            (mes,)).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) AS qtd, COALESCE(SUM(valor), 0) AS total FROM recibos"
            " WHERE substr(data, 1, 7) = ?", (mes,)).fetchone()
    por_categoria = [dict(r) for r in rows]
    return {
        "mes": mes,
        "total": round(total["total"], 2),
        "qtd": total["qtd"],
        "por_categoria": [
            {"categoria": r["categoria"], "qtd": r["qtd"], "total": round(r["total"] or 0, 2)}
            for r in por_categoria
        ],
    }
