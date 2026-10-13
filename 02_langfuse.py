"""Paso 2 · LangFuse: instrumentacion explicita con @observe + CallbackHandler."""
from dotenv import load_dotenv

load_dotenv()  # LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY y LANGFUSE_HOST

from langchain_core.messages import HumanMessage  # noqa: E402
from langfuse import get_client, observe  # noqa: E402
from langfuse.langchain import CallbackHandler  # noqa: E402

from agente import crear_agente  # noqa: E402

langfuse = get_client()
grafo = crear_agente()


# @observe crea la TRAZA (la peticion completa); el CallbackHandler anade dentro
# un SPAN por cada nodo del grafo y una GENERATION por cada llamada al modelo
@observe(name="atender-cliente")
def atender_cliente(pregunta: str) -> str:
    salida = grafo.invoke({"messages": [HumanMessage(pregunta)]},
                          config={"callbacks": [CallbackHandler()]}) #Oyente que en LangSmith se ponía solo. Recibe los avisos (on_chain_start, on_llm_end, on_tool_start, ...) y lo convierte en span por cada nodo, y generation por cada llamada al LLM
    return salida["messages"][-1].content


if __name__ == "__main__":
    for pregunta in ["Hola, ¿cómo va mi pedido 1234?", "¿Y el pedido 5678?", "¿Cuánto cuesta el envío 1234?"]:
        respuesta = atender_cliente(pregunta)
        print(f"Tú : {pregunta}\nBot: {respuesta}\n")
    langfuse.flush()  # enviar todo antes de salir
    print("3 trazas enviadas a LangFuse: Tracing -> Traces")
