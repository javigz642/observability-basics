"""Variacion paso 4 · ¿Es mejor la v2 del prompt? Medir en vez de opinar: un experimento por version."""
import sys
from importlib import import_module
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from langchain_core.messages import HumanMessage  # noqa: E402
from langfuse.langchain import CallbackHandler  # noqa: E402

from agente import crear_agente  # noqa: E402

ev = import_module("04_evaluacion")               # reutilizamos dataset y evaluadores del paso 4
langfuse = ev.langfuse
dataset = langfuse.get_dataset(ev.DATASET)

resumen = {}
for version in (1, 2):
    prompt = langfuse.get_prompt("chatbot-soporte", version=version)
    grafo = crear_agente(system_prompt=prompt.compile())

    def tarea(*, item, **kwargs):
        salida = grafo.invoke({"messages": [HumanMessage(item.input)]}, config={"callbacks": [CallbackHandler()]})
        return salida["messages"][-1].content

    r = langfuse.run_experiment(name="evaluacion-agente-soporte", run_name=f"prompt-v{version}",
                                data=dataset.items, task=tarea, evaluators=[ev.contiene_dato], max_concurrency=1)
    aciertos = sum(e.value for x in r.item_results for e in x.evaluations)
    resumen[version] = (aciertos, len(r.item_results))

langfuse.flush()
for version, (ok, n) in resumen.items():
    print(f"Prompt v{version}: contiene_dato {ok:.0f}/{n}  ({ok / n:.0%})")
print("Comparalos en LangFuse: Datasets -> soporte-pedidos -> selecciona las dos ejecuciones -> Compare")
