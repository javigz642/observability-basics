"""Paso 3 (cambio de version) · Mover la etiqueta production a la v2, sin tocar ni desplegar codigo.

En clase se hace con un clic en la web de LangFuse (Prompts -> chatbot-soporte -> v2 -> Promote to production).
Este script hace exactamente lo mismo por API. Para volver atras (rollback), pon version=1.
"""
from dotenv import load_dotenv

load_dotenv()

from langfuse import get_client  # noqa: E402

langfuse = get_client()
langfuse.update_prompt(name="chatbot-soporte", version=2, new_labels=["production"])
langfuse.flush()
print("La etiqueta 'production' apunta ahora a la version 2 de 'chatbot-soporte'")
