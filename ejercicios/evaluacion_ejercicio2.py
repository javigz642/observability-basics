"""Ejercicio 2 · Fase 3: un dataset pequeno, el agente de horas con cada version del prompt y dos evaluadores."""
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_ollama import ChatOllama  # noqa: E402
from langfuse import Evaluation, get_client, propagate_attributes  # noqa: E402
from langfuse.langchain import CallbackHandler  # noqa: E402

from agente_ejercicio2 import crear_agente  # noqa: E402

langfuse = get_client()
DATASET = "horas-empleados"
PROMPT = "chatbot-soporte-ej2"
VERSIONES = (1, 2, 3)  # las que no existan en LangFuse se saltan

# 1) DATASET: (pregunta, texto que la respuesta DEBE contener, respuesta correcta para el juez)
#    Los datos salen de datos.csv calculados con pandas, NUNCA del propio LLM.
#    Cada pregunta es independiente: si necesita saber quien eres, lo dice ("Soy Javier...").
EJEMPLOS = [
    # Datos que la tool SI tiene
    ("Soy Javier, ¿cuántas horas he trabajado en total?", "70",
     "Javier ha trabajado 70 horas en total."),
    ("¿Cuántas horas facturables tiene Diego?", "68",
     "Diego tiene 68 horas facturables (todas sus horas lo son)."),
    ("¿Cuántas horas no facturables tiene Ana?", "11.5",
     "Ana tiene 11,5 horas no facturables."),
    ("¿En qué proyectos ha trabajado Lucía?", "hermes",
     "Lucía ha trabajado en Atlas y Hermes."),
    ("Soy Ana, ¿he trabajado más horas que Marcos?", "63",
     "No. Ana ha trabajado 63 horas y Marcos 70."),
    # Empleado que no existe: la tool devuelve la lista de validos y una buena respuesta la ofrece
    ("¿Cuántas horas ha trabajado Sergio?", "marcos",
     "Sergio no existe. Debe decirlo, sin inventar horas, y puede ofrecer los empleados válidos."),
    # Fuera de alcance: no hay datos de vacaciones, debe responder con el fallback
    ("¿Cuántos días de vacaciones tiene Diego?", "info@empresa.com",
     "No hay datos de vacaciones. No debe dar ningún número de días: debe decir que no puede ayudar."),
    ("¿Cómo puedo solicitar las vacaciones?", "info@empresa.com",
     "Fuera de alcance. No debe inventar ningún procedimiento: debe decir que no puede ayudar."),
]
try:
    langfuse.get_dataset(DATASET)
except Exception:
    langfuse.create_dataset(name=DATASET, description="Preguntas sobre el registro de horas con la respuesta esperada")
    for pregunta, contiene, correcta in EJEMPLOS:
        langfuse.create_dataset_item(dataset_name=DATASET, input=pregunta, expected_output=correcta,
                                     metadata={"contiene": contiene})
    langfuse.flush()

juez = ChatOllama(model="llama3.1", temperature=0)


# 2) TAREA: se crea una por version del prompt (cada una con su propio grafo y su propia memoria)
def crear_tarea(prompt):
    grafo = crear_agente(system_prompt=prompt.compile())

    def tarea(*, item, **kwargs):
        # thread_id = id del item: cada pregunta empieza sin memoria de las anteriores
        with propagate_attributes(prompt=prompt):
            salida = grafo.invoke({"messages": [HumanMessage(item.input)]},
                                  config={"callbacks": [CallbackHandler()], "configurable": {"thread_id": item.id}})
        return salida["messages"][-1].content
    return tarea


# 3) EVALUADOR POR REGLA: ¿la respuesta contiene el dato clave? (coma decimal -> punto: "11,5" == "11.5")
def contiene_dato(*, output, metadata, **kwargs):
    clave = metadata["contiene"]
    ok = clave.lower() in output.lower().replace(",", ".")
    return Evaluation(name="contiene_dato", value=1.0 if ok else 0.0, comment=f"busca '{clave}'")


# 4) EVALUADOR LLM-AS-A-JUDGE: con el criterio claro (lo aprendido en el paso 4)
def juez_llm(*, input, output, expected_output, **kwargs):
    veredicto = juez.invoke(
        f"Pregunta de un usuario: {input}\nRespuesta correcta de referencia: {expected_output}\n"
        f"Respuesta del asistente: {output}\n\n"
        "¿La respuesta del asistente es coherente con la referencia? La información extra correcta NO es un error. "
        "Es un error cualquier dato inventado o que contradiga la referencia. Contesta SOLO 'SI' o 'NO'."
    ).content.strip().upper().replace("Í", "I")  # "SÍ" tambien cuenta como "SI"
    return Evaluation(name="juez_llm", value=1.0 if veredicto.startswith("SI") else 0.0, comment=veredicto)


if __name__ == "__main__":
    dataset = langfuse.get_dataset(DATASET)
    resumen = {}
    detalle = []
    for version in VERSIONES:
        try:
            prompt = langfuse.get_prompt(PROMPT, version=version, cache_ttl_seconds=0)
        except Exception:
            print(f"(La version {version} de '{PROMPT}' no existe en LangFuse: se salta)\n")
            continue

        resultado = langfuse.run_experiment(name="evaluacion-ejercicio2", run_name=f"prompt-v{version}",
                                            data=dataset.items, task=crear_tarea(prompt),
                                            evaluators=[contiene_dato, juez_llm], max_concurrency=1)
        print(f"== Prompt v{version} ==")
        print(f"{'Pregunta':<48}{'Regla':<7}{'Juez':<6}")
        for r in resultado.item_results:
            ev = {e.name: e.value for e in r.evaluations}
            print(f"{r.item.input:<48}{ev['contiene_dato']:<7.0f}{ev['juez_llm']:<6.0f}")
            detalle.append((version, r))
        n = len(resultado.item_results)
        resumen[version] = {nombre: sum(e.value for r in resultado.item_results for e in r.evaluations
                                        if e.name == nombre) / n
                            for nombre in ("contiene_dato", "juez_llm")}
        print()

    print("== Resumen ==")
    for version, medias in resumen.items():
        print(f"Prompt v{version}: contiene_dato {medias['contiene_dato']:.0%} - juez_llm {medias['juez_llm']:.0%}")

    # Detalle para revisar a mano: la respuesta completa y el veredicto de cada evaluador
    ruta = Path(__file__).resolve().parent / "detalle_evaluacion_ejercicio2.txt"
    with open(ruta, "w", encoding="utf-8") as f:
        for version, r in detalle:
            f.write(f"[v{version}] PREGUNTA : {r.item.input}\nESPERADO : {r.item.expected_output}\nRESPUESTA: {r.output}\n")
            for e in r.evaluations:
                f.write(f"  {e.name}: {e.value:.0f} ({e.comment})\n")
            f.write("\n")
    langfuse.flush()
    print(f"\nDetalle en {ruta.name} - Comparalos en LangFuse: Experiments -> evaluacion-ejercicio2 -> Compare")
