"""Testes do extrator — rodam SEM Ollama (fallback deterministico)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.extractor import extrair_recibo, fallback_parse, validar


def test_fallback_mercado():
    texto = "Mercado Pague Menos\nAv. Brasil 123 Rio Branco AC\n05/10/2026\nTOTAL R$ 187,90\n"
    d = fallback_parse(texto)
    assert d["fornecedor"] == "Mercado Pague Menos"
    assert d["data"] == "2026-10-05"
    assert d["valor"] == 187.90
    assert d["categoria"] == "alimentacao"


def test_validar_categoria_invalida():
    d = validar({"fornecedor": "X", "data": "2026-10-01", "valor": "50,00", "categoria": "festa", "confianca": 2})
    assert d["categoria"] == "outros"
    assert d["confianca"] == 1.0


def test_pipeline_txt_sem_gemma():
    dados_txt = "Posto Acreano\n12/10/2026\nCombustivel R$ 200,00\n".encode("utf-8")
    texto, dados = extrair_recibo("recibo.txt", dados_txt, usar_gemma=False)
    assert dados["categoria"] == "transporte"
    assert dados["valor"] == 200.00
