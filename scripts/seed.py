"""Popula o SQLite com os recibos de exemplo (sem precisar de Ollama)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.db import init_db, insert_recibo
from backend.extractor import fallback_parse

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "exemplos")

init_db()
n = 0
for nome in sorted(os.listdir(BASE)):
    if not nome.endswith(".txt"):
        continue
    with open(os.path.join(BASE, nome), encoding="utf-8") as f:
        texto = f.read()
    d = fallback_parse(texto)
    insert_recibo(d["fornecedor"], d["data"], d["valor"], d["categoria"],
                  d["confianca"], origem="seed-exemplo", arquivo=nome)
    n += 1
    print(f"OK {nome}: {d['fornecedor']} R$ {d['valor']:.2f} ({d['categoria']})")
print(f"{n} recibos inseridos.")
