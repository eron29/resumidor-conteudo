import streamlit as st
from openai import OpenAI

DEFAULT_MODEL = "gpt-4o-mini"
MAX_CONTENT_CHARS = 150_000

AUTO_PROMPT = """Você é um assistente especializado em sintetizar conteúdos longos em português.
Gere um resumo estruturado em Markdown, com as seções abaixo (use exatamente esses títulos):

## Sumário Executivo
## Principais Pontos
## Conclusão

Seja claro, objetivo e fiel ao conteúdo original. Não invente informações.

Conteúdo a resumir:
---
{content}
---
"""

CUSTOM_PROMPT = """Você é um assistente especializado em sintetizar conteúdos longos em português.
Resuma o conteúdo abaixo em Markdown, seguindo estritamente as instruções específicas do usuário.
Não invente informações que não estejam no conteúdo original.

Instruções do usuário:
{instructions}

Conteúdo a resumir:
---
{content}
---
"""


def get_secret(key: str):
    """Lê st.secrets sem quebrar quando secrets.toml não existe (uso local sem arquivo)."""
    try:
        return st.secrets.get(key)
    except Exception:
        return None


def get_client() -> OpenAI:
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        api_key = st.session_state.get("manual_api_key")
    if not api_key:
        raise RuntimeError(
            "Chave de API da OpenAI não configurada. Defina OPENAI_API_KEY em "
            "st.secrets ou informe-a na barra lateral."
        )
    return OpenAI(api_key=api_key)


def summarize(content: str, mode: str = "auto", custom_instructions: str = "", model: str = DEFAULT_MODEL) -> str:
    client = get_client()
    truncated = content[:MAX_CONTENT_CHARS]

    if mode == "custom" and custom_instructions.strip():
        prompt = CUSTOM_PROMPT.format(instructions=custom_instructions.strip(), content=truncated)
    else:
        prompt = AUTO_PROMPT.format(content=truncated)

    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
