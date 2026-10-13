"""Prompts PT-BR para extracao estruturada com Gemma via Ollama."""

SYSTEM_PROMPT = """Voce e um assistente financeiro para MEIs e freelancers brasileiros.
Sua tarefa: ler o texto de uma nota fiscal ou recibo (obtido por OCR) e extrair os dados em JSON valido.

Regras:
- Responda SOMENTE com JSON valido, sem markdown, sem explicacao.
- Campos obrigatorios: fornecedor (string), data (AAAA-MM-DD ou null), valor (numero, ponto decimal), categoria (uma de: alimentacao, transporte, material, servico, saude, moradia, outros), confianca (0.0 a 1.0).
- Datas em formato brasileiro DD/MM/AAAA devem ser convertidas para AAAA-MM-DD.
- Valores como "R$ 1.234,56" devem virar 1234.56.
- Se algum campo nao for encontrado, use null (menos categoria, que vira "outros", e confianca baixa).
- Categoria: escolha a mais provavel pelo nome do fornecedor/itens.

Exemplo de saida:
{"fornecedor": "Mercado Pague Menos", "data": "2026-10-05", "valor": 187.9, "categoria": "alimentacao", "confianca": 0.85}
"""

USER_TEMPLATE = """Texto do recibo/nota (OCR):
---
{texto}
---
Extraia o JSON agora."""

CATEGORIAS_VALIDAS = {
    "alimentacao", "transporte", "material", "servico",
    "saude", "moradia", "outros",
}
