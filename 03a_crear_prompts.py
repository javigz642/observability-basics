"""Paso 3 (preparacion) · Guardar el prompt del chatbot en LangFuse, en dos versiones."""
from dotenv import load_dotenv

load_dotenv()

from langfuse import get_client  # noqa: E402

from agente import PROMPT_POR_DEFECTO  # noqa: E402

langfuse = get_client()

# Version 1: el prompt de siempre, marcada como "production"
v1 = langfuse.create_prompt(name="chatbot-soporte", prompt=PROMPT_POR_DEFECTO, labels=["production"],
                            commit_message="v1: el prompt de la sesion 2")

# Version 2: mismo prompt con otro tono. Se guarda SIN la etiqueta production
v2 = langfuse.create_prompt(
    name="chatbot-soporte",
    prompt=PROMPT_POR_DEFECTO + " Usa un tono muy cercano, tutea al cliente y firma siempre como "
                                "'Lola, de The Power Shop'.",
    labels=["staging"],
    commit_message="v2: tono cercano con firma",
)
langfuse.flush()
print(f"Prompt 'chatbot-soporte' guardado: v{v1.version} (production) y v{v2.version} (staging)")
