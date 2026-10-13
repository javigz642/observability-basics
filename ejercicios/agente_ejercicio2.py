"Ejercicio 2"
from typing import TypedDict, Annotated
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import START, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
import pandas as pd
from pathlib import Path


RUTA_DATOS = Path(__file__).resolve().parent.parent / "datos.csv"
PROMPT_POR_DEFECTO = "Eres un asistente de proyectos. Responde en español. Usa la herramienta de " \
"informacion_trabajador para obtener la informacion de un trabajador."
df = pd.read_csv(RUTA_DATOS)
class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def informacion_trabajador(empleado:str):
    """Devuelve la informacion de las horas de determinado empleado"""
    filas_empleado = df[df["empleado"] == empleado]

    if filas_empleado.empty:
        return {"error": f"No existe el empleado {empleado}",
                "empleados_validos": df["empleado"].unique().tolist()}
    horas_totales = filas_empleado["horas"].sum()
    horas_facturables = filas_empleado[filas_empleado["facturable"] == "sí"]["horas"].sum()
    horas_no_facturables = filas_empleado[filas_empleado["facturable"] == "no"]["horas"].sum()
    horas_por_proyecto = filas_empleado.groupby("proyecto")["horas"].sum().to_dict()

    return {
        "empleado": empleado,
        "horas_totales" : horas_totales,
        "horas_facturables" : horas_facturables,
        "horas_no_facturables" : horas_no_facturables,
        "horas_por_proyecto" : horas_por_proyecto
    }


def crear_agente(system_prompt: str = PROMPT_POR_DEFECTO):
    """Construye el grafo chatbot - tools."""
    tools = [informacion_trabajador]

    modelo = ChatOllama(model="llama3.1", temperature=0).bind_tools(tools)
    system = SystemMessage(system_prompt)

    def chatbot(state: State):
        return {"messages": [modelo.invoke([system] + state["messages"])]}


    builder = StateGraph(State)
    builder.add_node("chatbot", chatbot)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")
    grafo = builder.compile(checkpointer=MemorySaver())
    return grafo








