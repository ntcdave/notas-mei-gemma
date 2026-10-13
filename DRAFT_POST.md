---
title: "I Built an Offline Receipt Organizer for Small Businesses — Powered by Gemma, Running on a $0 Budget"
tags: devchallenge, hf26challenge
---

# What I Built

In Acre, in the Brazilian Amazon, thousands of **MEIs** (solo micro-entrepreneurs — the moto courier, the market-stall owner, the freelance designer) run their business out of a shoebox full of paper receipts.

Every month the ritual is the same: spread the papers on the table, squint at faded ink, type numbers into a spreadsheet, and pray nothing was lost. The alternatives are a R$ 40–70/month SaaS subscription — or handing your CPF, your CNPJ and your entire revenue history to somebody else's cloud.

**Notas MEI** flips that deal. It's a receipt and invoice organizer that runs **100% on your own laptop**:

- 📸 Snap a photo (or drop a PDF) of any receipt or nota fiscal
- 🧠 **Gemma (`gemma3n:e4b`) via Ollama** reads it and extracts supplier, date, amount and category as structured JSON
- 📊 You get a clean monthly spending summary — no spreadsheet typing
- 🔒 **Nothing ever leaves the machine.** No API key, no per-token billing, no cloud copy of your finances

Who would pay for this? The courier who needs proof of fuel costs at tax time. The market vendor who wants to know whether September actually made money. The freelancer who bills R$ 3,000/month and loses R$ 200 of it to "miscellaneous, unknown." At R$ 15–25/month — less than half of ContaAzul or Organizze — this pays for itself the first time it finds one lost receipt. And the privacy pitch closes the sale: *"your accountant sees your numbers. Big Tech doesn't have to."*

# Demo

> 🎥 Video / GIF: _(record following `docs/DEMO.md` — drag 3 sample receipts, show monthly summary, then turn Wi-Fi OFF and upload again)_
>
> Live demo runs locally: `uvicorn backend.main:app --reload` → http://127.0.0.1:8000
>
> Sample files to try: `data/exemplos/recibo_mercado.txt`, `recibo_posto.txt`, `recibo_papelaria.txt`

The 10-second version: drag a market receipt for **R$ 187,90** → Gemma returns `{"fornecedor": "Mercado Pague Menos", "data": "2026-10-05", "valor": 187.9, "categoria": "alimentacao"}` → it lands in the monthly total next to fuel and office supplies. Offline. Free. Auditable.

# Code

> 🔗 Repository: _(paste your GitHub URL after pushing — e.g. https://github.com/ntcdave/notas-mei-gemma)_
>
> License: MIT. Stack: Python FastAPI · SQLite · vanilla HTML/JS · Tesseract OCR · Ollama + Gemma 3n E4B.

Everything a judge needs to reproduce: `scripts/setup_ollama.ps1` (model download + checks), `pip install -r requirements.txt`, `python scripts/seed.py`, `uvicorn backend.main:app --reload`. Tests (`pytest backend/tests/ -v`) run **without** a GPU or Ollama, so CI stays green.

# How I Built It

**The model: Gemma 3n E4B, and why it fits.** I needed a Portuguese-capable, multimodal-class open-weight model that survives on a 16 GB CPU-only notebook. `gemma3n:e4b` is the sweet spot: small enough to load locally (~4 GB), strong enough to normalize messy Brazilian receipts — converting `05/10/2026 → 2026-10-05`, `R$ 1.234,56 → 1234.56`, and picking the right category from supplier names. Temperature 0.1 + Ollama `format: json` keeps output machine-parseable, and a Pydantic-side validator clamps anything the model invents.

**The architecture decision I'm proudest of: the hybrid pipeline.** Pure vision-to-JSON sounds elegant but is slow and fragile on CPU with crooked phone photos. So the pipeline is:

```
upload → local OCR (Tesseract `por` for images, PyMuPDF for PDFs)
       → Gemma text-to-JSON (system prompt in PT-BR, JSON-only)
       → validation + SQLite → monthly aggregation → vanilla frontend
```

OCR does the brute reading; Gemma does the *reasoning*. And if Ollama is down, a deterministic regex fallback keeps the demo alive — the app degrades gracefully instead of crashing on stage.

**The frontend is deliberately boring:** one `index.html` + `app.js`, served by FastAPI itself. No build step, no npm, no deployment story to break. The loudest UI element is the badge: *"🔒 100% offline · R$ 0 de API."* That's the whole business model, rendered as a feature.

Honest limitations (judges respect these): blurry photos still hurt OCR — that's why every extraction shows a confidence score; first inference on CPU takes ~30–60 s while the model loads; natural-language questions over spending ("how much did I spend on supplies in September?") is scoped as phase 2.

# Why Does Open Innovation Matter?

Three words: **privacy, cost, sovereignty.**

1. **Privacy.** A receipt is a financial diary — where you shop, what medicine you buy, how much fuel your business burns. Closed APIs turn that diary into someone else's training data. Open weights mean the diary never leaves the drawer.
2. **Cost.** Every cloudOCR + LLM receipt parsed at scale is fractions of a cent that compound into a rent only SaaS giants can charge. With Gemma + Ollama + SQLite, the marginal cost of the 10,000th receipt is exactly zero. That math is what makes a R$ 15/month tool viable for a courier in Rio Branco.
3. **Sovereignty.** Internet in the Amazon fails. Vendor pricing changes. API deprecations kill side hustles overnight. A stack you can `ollama pull` today and run in five years — offline, in Portuguese, on commodity hardware — is independence, not just engineering.

Open innovation isn't charity here. It's the only business model where the poorest customer keeps both their money and their data.

# My First User

_(leave blank — fill after showing the MVP to one real MEI in Acre this week.)_

# Prize Categories

**Best Use of Gemma** 🏆 — Gemma is not a chatbot bolted on here; it *is* the product's brain: the structured-extraction reasoner, the Portuguese normalizer, the categorizer, all running locally as `gemma3n:e4b` through Ollama with zero cloud dependency.
