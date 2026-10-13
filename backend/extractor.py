"""Pipeline de extracao: arquivo -> OCR -> Gemma (Ollama) -> JSON validado.

Funciona em 2 modos:
1. ONLINE (Gemma): chama Ollama em http://localhost:11434/api/chat com model gemma3n:e4b.
2. OFFLINE/FALLBACK: parser heuristicos por regex (para testes, CI e demo sem GPU).
"""
from __future__ import annotations

import io
import json
import os
import re
from datetime import datetime

import httpx

from .prompts import CATEGORIAS_VALIDAS, SYSTEM_PROMPT, USER_TEMPLATE

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3n:e4b")

VALOR_RE = re.compile(r"(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2}|\d+\.\d{2}|\d+,\d{2})")
DATA_RE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")
DATA_ISO_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

PALAVRAS_CATEGORIA = {
    "alimentacao": ["mercado", "supermercado", "padaria", "restaurante", "lanchonete", "ifood", "atacadao"],
    "transporte": ["posto", "combustivel", "uber", "99 ", "oficina", "pecas", "passagem"],
    "material": ["papelaria", "informatica", "construcao", "ferramenta", "tinta", "madeira"],
    "servico": ["internet", "telefone", "contador", "aluguel de", "manutencao", "frete"],
    "saude": ["farmacia", "drogaria", "clinica", "exame", "consulta"],
    "moradia": ["energia", "eletrobras", "agua", "depurban", "aluguel", "condominio"],
}


def extrair_texto_arquivo(nome: str, conteudo: bytes) -> str:
    """Extrai texto de PDF, imagem ou .txt — tudo local, sem nuvem."""
    ext = os.path.splitext(nome.lower())[1]
    if ext == ".txt":
        return conteudo.decode("utf-8", errors="replace")
    if ext == ".pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=conteudo, filetype="pdf")
            return "\n".join(page.get_text() for page in doc)
        except Exception as exc:
            return f"[PDF sem texto extraivel: {exc}]"
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        try:
            from PIL import Image
            import pytesseract
            img = Image.open(io.BytesIO(conteudo))
            return pytesseract.image_to_string(img, lang="por+eng")
        except Exception as exc:
            return f"[OCR indisponivel: {exc}. Instale Tesseract OCR + pacote 'por'.]"
    # fallback: tenta como texto
    return conteudo.decode("utf-8", errors="replace")


def _parse_valor(texto: str) -> float | None:
    candidatos = VALOR_RE.findall(texto)
    if not candidatos:
        return None
    # pega o maior valor (normalmente o total)
    valores = []
    for c in candidatos:
        v = c.replace(".", "").replace(",", ".") if "," in c else c
        try:
            valores.append(float(v))
        except ValueError:
            continue
    return max(valores) if valores else None


def _parse_data(texto: str) -> str | None:
    m = DATA_RE.search(texto)
    if m:
        d, mo, a = m.groups()
        return f"{a}-{mo}-{d}"
    m = DATA_ISO_RE.search(texto)
    if m:
        return m.group(0)
    return None


def _classificar(texto: str) -> str:
    t = texto.lower()
    for cat, palavras in PALAVRAS_CATEGORIA.items():
        if any(p in t for p in palavras):
            return cat
    return "outros"


def fallback_parse(texto: str) -> dict:
    """Parser deterministico — usado em testes e quando Ollama esta fora do ar."""
    linhas = [ln.strip() for ln in texto.splitlines() if ln.strip()]
    fornecedor = linhas[0][:80] if linhas else "Desconhecido"
    valor = _parse_valor(texto) or 0.0
    data = _parse_data(texto)
    categoria = _classificar(texto)
    return {
        "fornecedor": fornecedor,
        "data": data,
        "valor": round(valor, 2),
        "categoria": categoria,
        "confianca": 0.5,
    }


def chamar_gemma(texto: str, timeout_s: float = 120.0) -> dict | None:
    """Chama Gemma via Ollama com resposta em JSON. Retorna None se falhar."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(texto=texto[:6000])},
        ],
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1},
    }
    try:
        r = httpx.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=timeout_s)
        r.raise_for_status()
        content = r.json()["message"]["content"]
        return json.loads(content)
    except Exception:
        return None


def validar(d: dict) -> dict:
    fornecedor = str(d.get("fornecedor") or "Desconhecido")[:80]
    valor = d.get("valor", 0.0)
    try:
        valor = round(float(valor), 2)
    except (TypeError, ValueError):
        valor = 0.0
    data = d.get("data")
    if data:
        try:
            datetime.strptime(str(data)[:10], "%Y-%m-%d")
            data = str(data)[:10]
        except ValueError:
            data = _parse_data(str(data))
    categoria = str(d.get("categoria") or "outros").lower()
    if categoria not in CATEGORIAS_VALIDAS:
        categoria = "outros"
    try:
        confianca = float(d.get("confianca", 0.5))
    except (TypeError, ValueError):
        confianca = 0.5
    return {
        "fornecedor": fornecedor, "data": data, "valor": valor,
        "categoria": categoria, "confianca": min(max(confianca, 0.0), 1.0),
    }


def extrair_recibo(nome: str, conteudo: bytes, usar_gemma: bool = True) -> tuple[str, dict]:
    """Pipeline completa. Retorna (texto_ocr, dados_validados)."""
    texto = extrair_texto_arquivo(nome, conteudo)
    dados = None
    if usar_gemma:
        dados = chamar_gemma(texto)
    if dados is None:
        dados = fallback_parse(texto)
        dados["confianca"] = 0.4
    else:
        dados = validar(dados)
    return texto, dados
