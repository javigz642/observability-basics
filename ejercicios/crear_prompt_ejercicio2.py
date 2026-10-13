from dotenv import load_dotenv
from langfuse import get_client
from agente_ejercicio2 import PROMPT_POR_DEFECTO

load_dotenv()
langfuse = get_client()

v1 = langfuse.create_prompt(name="chatbot-soporte-ej2", prompt=PROMPT_POR_DEFECTO, labels=["production"],
                           commit_message="v1: el prompt del ejercicio 2")

v2 = langfuse.create_prompt(name="chatbot-soporte-ej2",
                           prompt=PROMPT_POR_DEFECTO + " Si te preguntan otra cosa distinta que no sea información horaria de un trabajador, responde 'No puedo ayudarte, para más información consulta info@empresa.com'. "
                           "Habla en segunda persona cuando el usuario pregunte por sí mismo. Responde directo, sin introducciones.",
                           labels=["staging"],
                           commit_message="v2: fallback y tono")

langfuse.flush()
print(f"Prompt 'chatbot-soporte-ej2' guardado: v{v1.version} (production) y v{v2.version} (staging)")
