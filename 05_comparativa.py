"""Paso 5 · La MISMA ejecucion trazada a la vez en LangSmith (variables de entorno) y LangFuse (callback)."""
import os

from dotenv import load_dotenv

load_dotenv()  # LangSmith queda activo por LANGSMITH_TRACING=true

from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_core.tracers.langchain import wait_for_all_tracers  # noqa: E402
from langfuse import get_client, observe  # noqa: E402
from langfuse.langchain import CallbackHandler  # noqa: E402
from langsmith import Client  # noqa: E402

from agente import crear_agente  # noqa: E402

langfuse = get_client()
grafo = crear_agente()


TRAZAS = []


@observe(name="comparativa")
def ejecutar(pregunta: str) -> str:
    TRAZAS.append(langfuse.get_current_trace_id())   # guardamos el id para imprimir el enlace
    salida = grafo.invoke({"messages": [HumanMessage(pregunta)]},
                          config={"callbacks": [CallbackHandler()], "run_name": "comparativa"})
    return salida["messages"][-1].content


respuesta = ejecutar("¿Qué transportista lleva mi pedido 1234 y cuándo llega?")
trace_id = TRAZAS[-1]
print("Respuesta:", respuesta)

langfuse.flush()
wait_for_all_tracers()
cliente = Client()
run = next(cliente.list_runs(project_name=os.environ["LANGSMITH_PROJECT"], is_root=True, limit=1))
print("\nLa misma ejecucion en las dos herramientas:")
print("  LangFuse :", langfuse.get_trace_url(trace_id=trace_id))
print("  LangSmith:", cliente.get_run_url(run=run, project_name=os.environ["LANGSMITH_PROJECT"]))
