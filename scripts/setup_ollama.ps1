#Requires -Version 5.1
<#
  Instala/verifica Ollama + baixa Gemma + verifica Tesseract.
  Uso: powershell -ExecutionPolicy Bypass -File scripts\setup_ollama.ps1
#>
$ErrorActionPreference = "Stop"
$Model = $env:OLLAMA_MODEL
if (-not $Model) { $Model = "gemma4:e2b" }

Write-Host "== Notas MEI: setup ambiente local ==" -ForegroundColor Green

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
  Write-Host "Ollama nao encontrado. Baixe em https://ollama.com/download e reexecute este script." -ForegroundColor Yellow
  Write-Host "Apos instalar: ollama pull $Model" -ForegroundColor Yellow
  exit 1
}

Write-Host "-> Baixando modelo $Model (pode demorar na 1a vez)..."
& ollama pull $Model

Write-Host "-> Teste rapido do modelo..."
& ollama run $Model "Responda apenas: OK" --verbose | Select-Object -First 5

if (-not (Get-Command tesseract -ErrorAction SilentlyContinue)) {
  Write-Host "AVISO: Tesseract OCR nao encontrado. Baixe em https://github.com/UB-Mannheim/tesseract/wiki + pacote 'por'." -ForegroundColor Yellow
} else {
  & tesseract --version | Select-Object -First 2
}

Write-Host "== OK. Rode a API com: uvicorn backend.main:app --reload ==" -ForegroundColor Green
