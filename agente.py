"""El agente de soporte de la Sesion 2 (LangGraph + tool consulta_pedido), sin cambios.

Hoy NO construimos un agente nuevo: lo observamos. Este modulo no sabe nada de LangSmith ni de LangFuse.
"""
from typing import Annotated, TypedDict

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

PEDIDOS = {
    "1234": {"estado": "enviado", "transportista": "SEUR", "llegada": "jueves"},
    "5678": {"estado": "en preparación", "transportista": "-", "llegada": "la semana que viene"},
}

PROMPT_POR_DEFECTO = ("Eres el asistente de soporte de una tienda online. Responde en español, breve. "
                      "Usa la herramienta consulta_pedido cuando te pregunten por un pedido.")


@tool
def consulta_pedido(numero: str) -> dict:
    """Devuelve el estado, el transportista y la fecha de llegada de un pedido a partir de su número."""
    return PEDIDOS.get(numero, {"error": f"No existe el pedido {numero}"})


class State(TypedDict):
    messages: Annotated[list, add_messages]


def crear_agente(system_prompt: str = PROMPT_POR_DEFECTO):
    """Construye el grafo chatbot <-> tools. El system prompt se puede inyectar (paso 3)."""
    tools = [consulta_pedido]
    modelo = ChatOllama(model="llama3.1", temperature=0).bind_tools(tools)
    system = SystemMessage(system_prompt)

    def chatbot(state: State) -> dict:
        return {"messages": [modelo.invoke([system] + state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("chatbot", chatbot)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")
    return builder.compile()
