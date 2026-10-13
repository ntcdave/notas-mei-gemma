"""Benchmark: gemma3n:e4b vs gemma4:e2b na extracao de recibos (texto -> JSON).

Uso: python scripts/bench_models.py
Compara tempo + qualidade do JSON em 2 recibos de exemplo.
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import backend.extractor as ext
from backend.extractor import validar

MODELOS = ["gemma3n:e4b", "gemma4:e2b"]
RECIBOS = ["recibo_mercado.txt", "recibo_posto.txt"]
BASE = os.path.join(os.path.dirname(__file__), "..", "data", "exemplos")


def main() -> None:
    for modelo in MODELOS:
        ext.OLLAMA_MODEL = modelo
        print(f"\n===== {modelo} =====")
        for nome in RECIBOS:
            with open(os.path.join(BASE, nome), encoding="utf-8") as f:
                texto = f.read()
            t0 = time.time()
            d = ext.chamar_gemma(texto)
            dt = time.time() - t0
            if d is None:
                print(f"[{nome}] FALHOU apos {dt:.1f}s (Ollama sem resposta)")
                continue
            try:
                v = validar(d)
            except Exception as exc:  # noqa: BLE001
                print(f"[{nome}] JSON invalido apos {dt:.1f}s: {str(d)[:200]} (erro: {exc})")
                continue
            print(f"[{nome}] {dt:.1f}s -> {v}")


if __name__ == "__main__":
    main()
