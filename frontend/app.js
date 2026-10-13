const API = "";
const $ = (id) => document.getElementById(id);
const BRL = (v) => (v || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

const drop = $("drop"), file = $("file"), status = $("status");
drop.onclick = () => file.click();
drop.ondragover = (e) => { e.preventDefault(); };
drop.ondrop = (e) => { e.preventDefault(); if (e.dataTransfer.files[0]) enviar(e.dataTransfer.files[0]); };
file.onchange = () => { if (file.files[0]) enviar(file.files[0]); };

async function enviar(f) {
  status.textContent = "Lendo com Gemma local... (pode levar ~30s na 1ª vez)";
  const fd = new FormData(); fd.append("file", f);
  try {
    const r = await fetch(`${API}/api/recibos/upload`, { method: "POST", body: fd });
    const j = await r.json();
    if (j.ok) {
      status.textContent = `✅ ${j.dados.fornecedor} · ${BRL(j.dados.valor)} · ${j.dados.categoria}`;
      carregarTudo();
    } else status.textContent = "❌ " + (j.erro || "falha");
  } catch (e) { status.textContent = "❌ API fora do ar. Rode: uvicorn backend.main:app --reload"; }
}

async function carregarTudo() { carregarResumo(); carregarLista(); }

async function carregarResumo() {
  const mes = $("mes").value || "2026-10";
  const r = await fetch(`${API}/api/resumo?mes=${mes}`);
  const j = await r.json();
  $("total").textContent = BRL(j.resumo.total) + `  (${j.resumo.qtd} lançamentos)`;
  $("cats").innerHTML = j.resumo.por_categoria.map(c =>
    `<div>• <b>${c.categoria}</b>: ${BRL(c.total)} <small>(${c.qtd})</small></div>`).join("") || "<small>Sem dados neste mês.</small>";
}

async function carregarLista() {
  const r = await fetch(`${API}/api/recibos?limit=100`);
  const j = await r.json();
  $("lista").innerHTML = j.recibos.map(x =>
    `<tr><td>${x.fornecedor}</td><td>${x.data || "-"}</td><td>${x.categoria}</td><td>${BRL(x.valor)}</td></tr>`).join("");
}

carregarTudo();
