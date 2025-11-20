import os
from openai import OpenAI
from dotenv import load_dotenv
from src.colegal.core.logger import log_event

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

# Ruta al archivo .env
dotenv_path = os.path.join(PROJECT_ROOT, ".env")

# Cargar .env
load_dotenv(dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("No se encontró la variable OPENAI_API_KEY. Verifica tu archivo .env")

client = OpenAI(api_key=api_key)

def call_llm(prompt: str, session_uuid=None) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un asistente jurídico colombiano. "
                    "Analizas datos de contratos, detectas inconsistencias y "
                    "das retroalimentación clara, precisa y útil. "
                    "No generas cláusulas ni redactas contratos "
                    "a menos que se te pida explícitamente."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    content = response.choices[0].message.content

    # Log: opcional pero útil
    tokens_in = response.usage.prompt_tokens
    tokens_out = response.usage.completion_tokens

    if session_uuid:
        log_event(
            session_uuid=session_uuid,
            agent_name="generator",
            event_type="success",
            prompt=prompt,
            response=content,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
        )

    return content

