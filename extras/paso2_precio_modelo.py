"""Variacion paso 2 · Ponerle precio al modelo para que LangFuse calcule el COSTE.

llama3.1 corre en local con Ollama: coste real 0 EUR, y LangFuse no conoce su precio.
Aqui le damos un precio DE REFERENCIA (el de un modelo pequeno de API, ~0,15 $ / 0,60 $ por millon
de tokens) para ver como se calcularia el coste si usaramos un modelo de pago.
En la web: Settings -> Models -> Add model definition.
"""
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from langfuse import get_client  # noqa: E402

langfuse = get_client()
if not any(m.model_name == "llama3.1" for m in langfuse.api.models.list(limit=100).data):
    langfuse.api.models.create(model_name="llama3.1", match_pattern=r"(?i)^llama3\.1(:.*)?$", unit="TOKENS",
                               input_price=0.15 / 1_000_000, output_price=0.60 / 1_000_000)
print("Precio de referencia para llama3.1: 0,15 $ entrada / 0,60 $ salida por millon de tokens")

from importlib import import_module  # noqa: E402

atender_cliente = import_module("02_langfuse").atender_cliente   # la misma funcion del paso 2
print("Bot:", atender_cliente("¿Cómo va mi pedido 1234?"))
langfuse.flush()
print("Abre la traza nueva en LangFuse: ahora cada generation muestra su coste")
