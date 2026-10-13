# 🧾 Notas MEI — organizador local de recibos com Gemma

MEI e freelancer fotografam notas e recibos → a ferramenta extrai **fornecedor, data, valor e categoria** e gera o **resumo mensal de gastos**. Tudo **100% no notebook**: modelo open-weight **Gemma (`gemma4:e2b`) via Ollama**, OCR local (Tesseract), banco **SQLite**. Nenhum dado vai para a nuvem. Custo de API: **R$ 0**.

> Feito para o DEV **Hacktoberfest Open-Source AI Challenge — Week 2: Side Hustle**. Categoria: **Best Use of Gemma**.

## Por que alguém pagaria por isso?

- MEI paga R$ 40–70/mês em planilhas/contadores para organizar papel.
- Alternativas em nuvem veem seu CPF, CNPJ e faturamento. Aqui, **seu contador vê seus números. A nuvem, não.**
- Funciona offline no interior do Acre, sem internet boa.

## Como funciona

```
Foto/PDF → OCR local (Tesseract / PyMuPDF) → Gemma via Ollama (JSON) → SQLite → resumo mensal
```

Pipeline híbrida de propósito: OCR cuida da leitura bruta (rápido em CPU) e a Gemma cuida do raciocínio (normalizar datas `DD/MM/AAAA → AAAA-MM-DD`, valores `R$ 1.234,56 → 1234.56`, classificar categoria). Se o Ollama estiver fora do ar, há fallback determinístico por regex para a demo não quebrar.

## Instalação

### 1. Ollama + Gemma (único download pesado)

```powershell
# 1. Baixe o Ollama: https://ollama.com/download
# 2. Depois:
ollama pull gemma4:e2b
ollama run gemma4:e2b "Responda apenas: OK"
```

> Alternativa: `OLLAMA_MODEL=gemma3n:e4b` também funciona (maior, mais lento em CPU).
> Benchmark dos dois: `python scripts/bench_models.py`.

Ou rode `powershell -ExecutionPolicy Bypass -File scripts\setup_ollama.ps1`.

### 2. Tesseract OCR (para ler fotos)

Baixe em https://github.com/UB-Mannheim/tesseract/wiki e marque o pacote de idioma **por** na instalação.

### 3. API Python

```powershell
cd notas-mei-gemma
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\seed.py
uvicorn backend.main:app --reload
```

Abra **http://127.0.0.1:8000** — o frontend já é servido pela própria API.

## Endpoints

| Método | Rota | O que faz |
|---|---|---|
| GET | `/api/status` | saúde + modelo em uso |
| POST | `/api/recibos/upload` | envia foto/PDF/TXT, extrai com Gemma e salva |
| GET | `/api/recibos?limit=100` | lista lançamentos |
| GET | `/api/resumo?mes=2026-10` | total + agregado por categoria |

## Testes

```powershell
python -m pytest backend\tests\ -v
```

Rodam **sem Ollama** (usam o fallback), então passam no CI.

## Estrutura

```
backend/   → FastAPI + extrator + SQLite
frontend/  → HTML/JS vanilla (offline-first)
data/exemplos/ → 4 recibos sintéticos p/ demo
scripts/   → setup_ollama.ps1, seed.py
docs/      → roteiro de demo
```

## Limitações honestas

- OCR sofre com foto borrada/torta — o app avisa a confiança da extração.
- Gemma `4:e2b` em CPU leva ~30 s na primeira extração (carregamento do modelo); depois reaproveita o modelo carregado.
- Perguntas em linguagem natural sobre gastos ("quanto gastei com material em setembro?") estão no roadmap, fora do MVP.

## Licença

MIT — uso comercial liberado. Veja `LICENSE`.
