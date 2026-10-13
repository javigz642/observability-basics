"""Ejercicio 1"""
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

from langfuse import get_client
from langfuse.langchain import CallbackHandler
load_dotenv()

class State(TypedDict):
    tipo_pregunta: str
    message: Annotated[list, add_messages]

modelo = ChatOllama(model="llama3.1", temperature=0)
SYSTEM = SystemMessage("Eres un asistente que clasifica los mensajes en 'pregunta' o 'queja' o 'otro'. Devuelve ESTRICTAMENTE una palabra que es el resultado de la clasificación de la entrada del usuario.")


def bot_clasificador(state: State):
    respuesta = modelo.invoke([SYSTEM] + state["message"])
    etiqueta = respuesta.content.strip().lower()
    return {"tipo_pregunta": etiqueta}

def pregunta(state: State):
    return {"message": AIMessage("Para cualquier pregunta relacionada con la empresa "
    "puedes contactar con preguntas@empresa.com")}

def queja(state: State):
    return {"message": AIMessage("Lamentamos su experiencia con nosotros."
    " Para cualquier queja contactar con quejas@empresa.com")}

def otro(state: State):
    return {"message": AIMessage("Para cualquier otra consulta contactar con info@empresa.com")}

def decidir_siguiente(state: State):
    if state["tipo_pregunta"]== "pregunta":
        return "pregunta"
    elif state["tipo_pregunta"] == "queja":
        return "queja"
    else:
        return "otro"
    
builder = StateGraph(State)
builder.add_node("bot_clasificador", bot_clasificador)
builder.add_node("pregunta", pregunta)
builder.add_node("queja", queja)
builder.add_node("otro", otro)

builder.add_edge(START, "bot_clasificador")
builder.add_conditional_edges("bot_clasificador", decidir_siguiente, {"pregunta": "pregunta", "queja": "queja", "otro": "otro"})
builder.add_edge("pregunta", END)
builder.add_edge("queja", END)
builder.add_edge("otro", END)

grafo = builder.compile()
if __name__=="__main__":
    preguntas = ["¡¡No me han pagado la nónima a tiempo!!",
                 "¿Cuántos días tengo de vacaciones?",
                 "Hola buenos días, soy Javier, el de recursos humanos",
                 "Tengo una queja y una pregunta para la empresa"
                 ]
    for n, preg in enumerate(preguntas, 1):
        print(f"----PREGUNTA{n}----")
        resultado = grafo.invoke({"message": preg}, config={"callbacks": [CallbackHandler()]})
        print("ENTRADA: ", preg)
        print("TOOL: ", resultado["tipo_pregunta"])
        print("SALIDA: ", resultado["message"][-1].content)
        print()
    get_client().flush()
    png = grafo.get_graph().draw_mermaid_png(max_retries=5, retry_delay=2.0)
    with open("capturas/grafo_ejercicio1.png", "wb") as f:
        f.write(png)
    print("Guardado capturas/grafo_ejercicio1.png")

