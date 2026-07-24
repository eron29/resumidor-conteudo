import streamlit as st
from openai import OpenAI

DEFAULT_MODEL = "gpt-4o-mini"
MAX_CONTENT_CHARS = 150_000

AUTO_PROMPT = """Você é um assistente especializado em sintetizar conteúdos longos em português.
Gere um resumo completo e detalhado em Markdown, com as seções abaixo (use exatamente esses títulos):

## Sumário Executivo
Um parágrafo denso cobrindo do que se trata o conteúdo e por que ele importa.

## Principais Pontos
Organize em tópicos e subtópicos (bullet points), um por ideia central. Não resuma demais:
detalhe cada ponto o suficiente para que quem não viu/leu o conteúdo original entenda o raciocínio
completo, não apenas o título da ideia.

## Exemplos e Casos Citados
Liste, em tópicos, cada exemplo, caso prático, história, analogia, dado numérico ou demonstração
mencionados no conteúdo, explicando o contexto de cada um. Se nenhum exemplo for citado, indique
isso explicitamente nesta seção.

## Conclusão
Principais conclusões, recomendações ou próximos passos indicados no conteúdo.

Seja completo e detalhado, mas fiel ao conteúdo original — não invente informações nem infira além
do que está explícito.

Conteúdo a resumir:
---
{content}
---
"""

CUSTOM_PROMPT = """Você é um assistente especializado em sintetizar conteúdos longos em português.
Resuma o conteúdo abaixo em Markdown, organizando as ideias em tópicos e subtópicos (bullet points)
e destacando em uma seção própria os exemplos, casos práticos ou histórias citados no conteúdo,
seguindo estritamente as instruções específicas do usuário abaixo. Onde as instruções do usuário
conflitarem com essa estrutura padrão, priorize as instruções do usuário.
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
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
