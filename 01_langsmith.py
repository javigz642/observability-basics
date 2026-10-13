"""Paso 1 · LangSmith: activar el tracing SIN tocar el codigo del agente."""
import os

from dotenv import load_dotenv

# 1) Esto es TODO lo que hace falta: cargar LANGSMITH_TRACING=true y LANGSMITH_API_KEY del .env
load_dotenv()

from langchain_core.messages import HumanMessage  # noqa: E402

from agente import crear_agente  # noqa: E402

# 2) El agente de la Sesion 2, tal cual: no importa nada de LangSmith
grafo = crear_agente()
salida = grafo.invoke({"messages": [HumanMessage("Hola, ¿cómo va mi pedido 1234?")]},
                      config={"run_name": "paso1-langsmith"}) #run_name solo pone nombre a la traza
print("Respuesta:", salida["messages"][-1].content)

# 3) (Solo para la demo) esperar a que se envie la traza e imprimir su enlace
from langchain_core.tracers.langchain import wait_for_all_tracers  # noqa: E402
from langsmith import Client  # noqa: E402

wait_for_all_tracers()
cliente = Client()
run = next(cliente.list_runs(project_name=os.environ["LANGSMITH_PROJECT"], is_root=True, limit=1))
print(f"Traza '{run.name}' enviada a LangSmith (proyecto {os.environ['LANGSMITH_PROJECT']}):")
print(cliente.get_run_url(run=run, project_name=os.environ["LANGSMITH_PROJECT"]))

# tu script ──avisos──► LangChainTracer ──HTTP──► servidores LangSmith ──► web
