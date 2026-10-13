"""Paso 3 · Prompt management: el codigo pide el prompt POR NOMBRE; LangFuse decide la version."""
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage  # noqa: E402
from langfuse import get_client  # noqa: E402

from agente import crear_agente  # noqa: E402

langfuse = get_client()

# El prompt ya no esta "quemado" en el codigo: se carga la version con la etiqueta production
prompt = langfuse.get_prompt("chatbot-soporte", label="production", cache_ttl_seconds=0)
print(f"Prompt cargado: '{prompt.name}' version {prompt.version}")

grafo = crear_agente(system_prompt=prompt.compile())
salida = grafo.invoke({"messages": [HumanMessage("Hola, ¿cómo va mi pedido 1234?")]})
print("Respuesta:", salida["messages"][-1].content)
