"""Solucion del Ejercicio 1 · Pon lupa a tu cadena con LangFuse.

La cadena LCEL de la Sesion 1 (traductor) instrumentada con LangFuse: 3 consultas y a mirar el dashboard.
"""
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_ollama import ChatOllama  # noqa: E402
from langfuse import get_client  # noqa: E402
from langfuse.langchain import CallbackHandler  # noqa: E402

# La cadena de la Sesion 1, sin cambios
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un traductor profesional. Devuelve SOLO la traducción al inglés, sin comentarios."),
    ("human", "{texto}"),
])
cadena = prompt | ChatOllama(model="llama3.1", temperature=0) | StrOutputParser()

# La unica novedad: el CallbackHandler de LangFuse en la config de cada llamada
handler = CallbackHandler()
consultas = [
    "Hola, ¿qué tal?",
    "El modelo no recuerda nada entre llamadas.",
    "La observabilidad convierte una demo en una aplicación de producción: una que puedes depurar "
    "cuando falla, medir cuando dudas y mejorar con datos en vez de con intuiciones.",
]
for texto in consultas:
    print(f"ES: {texto}\nEN: {cadena.invoke({'texto': texto}, config={'callbacks': [handler]})}\n")

get_client().flush()
print("3 trazas en LangFuse: compara latencia y tokens. ¿Cual ha salido mas cara y por que?")
