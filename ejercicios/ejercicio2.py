from dotenv import load_dotenv
from langchain.messages import HumanMessage
from langfuse import get_client, observe, propagate_attributes
from langfuse.langchain import CallbackHandler

from agente_ejercicio2 import crear_agente


load_dotenv()
langfuse = get_client()
prompt = langfuse.get_prompt("chatbot-soporte-ej2", label="production", cache_ttl_seconds=0)
print(f"Prompt cargado: '{prompt.name}' version {prompt.version}")
grafo = crear_agente(system_prompt=prompt.compile())

@observe(name="atender-cliente")
def atender_cliente(pregunta: str, usuario:str, chat_id:str) -> str:
    with propagate_attributes(user_id=usuario,session_id=chat_id,prompt=prompt):
        salida = grafo.invoke({"messages": [HumanMessage(pregunta)]},
                            config={"callbacks":[CallbackHandler()], 
                                    "configurable":{"thread_id": chat_id},
                                    },
                            )
    return salida["messages"][-1].content


if __name__ == "__main__":
    preguntas_por_chat = {"chat_1": {"usuario": "usuario_1", "preguntas": ["Me llamo Javier, dime mi información de cuantas horas he trabajado en total",
                                           "¿En que proyectos ha trabajado Lucía?",
                                           "¿He trabajado más que Diego o no?"]},
                            "chat_2": {"usuario": "usuario_1", "preguntas": ["¿Cuantos días de vacaciones tiene Diego?"]},
                            "chat_3": {"usuario": "usuario_2", "preguntas": ["¿Cuántas horas ha trabajado Sergio?",
                                          "¿Sabes como me llamo?", 
                                          "¿Como puedo solicitar las vaciones?"]}}
    for chat_id, conversacion in preguntas_por_chat.items():
        usuario = conversacion["usuario"]
        for pregunta in conversacion["preguntas"]:
            respuesta = atender_cliente(pregunta=pregunta, usuario=usuario, chat_id=chat_id)
            print(f"[{usuario} - {chat_id}]")
            print(f"Tú: {pregunta}\nBot: {respuesta}\n")
    langfuse.flush()

