"""Paso 4 · Evaluacion: un dataset pequeno, el agente sobre todo el dataset y dos evaluadores."""
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_ollama import ChatOllama  # noqa: E402
from langfuse import Evaluation, get_client  # noqa: E402
from langfuse.langchain import CallbackHandler  # noqa: E402

from agente import crear_agente  # noqa: E402

langfuse = get_client()
DATASET = "soporte-pedidos"

# 1) DATASET: 5 preguntas con el dato que la respuesta DEBE contener
EJEMPLOS = [
    ("¿Cómo va mi pedido 1234?", "enviado"),
    ("¿Qué transportista lleva el pedido 1234?", "SEUR"),
    ("¿Qué día llega el pedido 1234?", "jueves"),
    ("¿En qué estado está el pedido 5678?", "preparación"),
    ("¿Cómo va el pedido 9999?", "no existe"),
]
try:
    langfuse.get_dataset(DATASET)
except Exception:
    langfuse.create_dataset(name=DATASET, description="Preguntas de soporte con el dato esperado")
    for pregunta, esperado in EJEMPLOS:
        langfuse.create_dataset_item(dataset_name=DATASET, input=pregunta, expected_output=esperado)
    langfuse.flush()

grafo = crear_agente()
juez = ChatOllama(model="llama3.1", temperature=0)


# 2) TAREA: lo que se ejecuta para cada ejemplo del dataset (nuestro agente)
def tarea(*, item, **kwargs):
    salida = grafo.invoke({"messages": [HumanMessage(item.input)]}, config={"callbacks": [CallbackHandler()]})
    return salida["messages"][-1].content


# 3) EVALUADOR POR REGLA: ¿la respuesta contiene el dato esperado?
def contiene_dato(*, output, expected_output, **kwargs):
    ok = expected_output.lower() in output.lower()
    return Evaluation(name="contiene_dato", value=1.0 if ok else 0.0,
                      comment=f"busca '{expected_output}'")


# 4) EVALUADOR LLM-AS-A-JUDGE: otro modelo juzga si la respuesta es correcta
def juez_llm(*, input, output, expected_output, **kwargs):
    veredicto = juez.invoke(
        f"Pregunta de un cliente: {input}\nDato correcto: {expected_output}\nRespuesta del asistente: {output}\n\n"
        "¿La respuesta es correcta y coherente con el dato correcto? Contesta SOLO 'SI' o 'NO'."
    ).content.strip().upper()
    return Evaluation(name="juez_llm", value=1.0 if veredicto.startswith("SI") else 0.0, comment=veredicto)


if __name__ == "__main__":
    dataset = langfuse.get_dataset(DATASET)
    resultado = langfuse.run_experiment(name="evaluacion-agente-soporte", run_name="llama3.1-prompt-por-defecto",
                                        data=dataset.items, task=tarea,
                                        evaluators=[contiene_dato, juez_llm], max_concurrency=1)
    print(f"{'Pregunta':<44}{'Esperado':<13}{'Regla':<7}{'Juez':<6}")
    for r in resultado.item_results:
        ev = {e.name: e.value for e in r.evaluations}
        print(f"{r.item.input:<44}{r.item.expected_output:<13}{ev['contiene_dato']:<7.0f}{ev['juez_llm']:<6.0f}")
    n = len(resultado.item_results)
    for nombre in ("contiene_dato", "juez_llm"):
        media = sum(e.value for r in resultado.item_results for e in r.evaluations if e.name == nombre) / n
        print(f"Media {nombre}: {media:.0%}")
    # Detalle para revisar a mano: la respuesta completa y el veredicto de cada evaluador
    with open("detalle_evaluacion.txt", "w", encoding="utf-8") as f:
        for r in resultado.item_results:
            f.write(f"PREGUNTA : {r.item.input}\nESPERADO : {r.item.expected_output}\nRESPUESTA: {r.output}\n")
            for e in r.evaluations:
                f.write(f"  {e.name}: {e.value:.0f} ({e.comment})\n")
            f.write("\n")
    langfuse.flush()
    print("Detalle en detalle_evaluacion.txt · Resultados en LangFuse: Datasets -> soporte-pedidos")
