"""API FastAPI — Organizador de Notas para MEI (100% local)."""
from __future__ import annotations

import os
from datetime import datetime

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db, insert_recibo, list_recibos, resumo_mensal
from .extractor import OLLAMA_MODEL, extrair_recibo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = FastAPI(title="Notas MEI — Gemma Local", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

init_db()


@app.get("/api/status")
def status():
    return {
        "ok": True,
        "modelo": OLLAMA_MODEL,
        "offline": True,
        "mensagem": "100% local — nenhum dado sai do seu notebook.",
    }


@app.post("/api/recibos/upload")
async def upload_recibo(file: UploadFile = File(...)):
    conteudo = await file.read()
    if len(conteudo) > 10 * 1024 * 1024:
        return {"ok": False, "erro": "Arquivo maior que 10MB."}
    texto, dados = extrair_recibo(file.filename or "recibo", conteudo, usar_gemma=True)
    rid = insert_recibo(
        fornecedor=dados["fornecedor"], data=dados["data"], valor=dados["valor"],
        categoria=dados["categoria"], confianca=dados["confianca"],
        origem="gemma-local", arquivo=file.filename,
    )
    return {"ok": True, "id": rid, "dados": dados,
            "texto_preview": texto[:500]}


@app.get("/api/recibos")
def get_recibos(limit: int = Query(100, le=500)):
    return {"ok": True, "recibos": list_recibos(limit)}


@app.get("/api/resumo")
def get_resumo(mes: str = Query(default=datetime.now().strftime("%Y-%m"),
                                pattern=r"^\d{4}-\d{2}$")):
    return {"ok": True, "resumo": resumo_mensal(mes)}


if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/index.html", include_in_schema=False)
def index_alias():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
