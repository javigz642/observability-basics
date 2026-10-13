# Sesión 3 · Observability: LangFuse y LangSmith · Prompts para Claude Code

Estos son los prompts que usamos en la práctica, en el mismo orden que en clase. Cópialos y pégalos en Claude Code uno a uno.

**Cómo usarlos**
1. Pega el prompt del paso y deja que Claude Code proponga los cambios.
2. **Lee el código antes de aceptar** (y los comandos, como `pip install`, antes de permitirlos).
3. Ejecuta y compara con el apartado *Qué deberías ver*.
4. Si no sale lo esperado, vuelve a pedírselo con lo que has aprendido.

> Antes de empezar: el agente de la Sesión 2, una cuenta gratuita en [LangSmith](https://smith.langchain.com) y otra en [LangFuse Cloud](https://cloud.langfuse.com), con sus API keys copiadas en un archivo `.env` (tienes la plantilla en `.env.example`). **Nunca compartas ni subas tu `.env`.**

El resultado de referencia, con todo el código comentado, está en la carpeta `observability-basics` del material de la sesión.

---

## Paso 1 · Instrumentar con LangSmith

**Qué construye**

- Coger el agente de la sesion 2
- LANGSMITH_TRACING=true + API key en el .env
- Ejecutar el grafo con una pregunta
- Abrir la primera traza en el dashboard

**Prompt**

```text
Coge el grafo LangGraph de la Sesion 2. Ya tengo cuenta gratuita en LangSmith y la API key en el .env. Activa el tracing con las variables de entorno LANGSMITH_TRACING=true y LANGSMITH_API_KEY. Ejecuta el grafo con una pregunta y ensename donde ver la primera traza en el dashboard de LangSmith.
```

**Qué deberías ver**

La respuesta de siempre y, debajo, el enlace a la traza. El codigo del agente no ha cambiado.

---

## Paso 2 · Instrumentar con LangFuse

**Qué construye**

- Instalar el SDK de langfuse
- @observe crea la traza
- CallbackHandler anade spans y generations
- Tres preguntas y al dashboard

**Prompt**

```text
Instala el SDK de langfuse. Instrumenta el mismo grafo con LangFuse usando el decorador @observe y el callback handler, apuntando a LangFuse Cloud (free tier). Ejecuta el grafo y muestra en el dashboard la traza con sus spans, los tokens, el coste y la latencia.
```

**Qué deberías ver**

La tercera respuesta: a '¿que horario teneis?' el modelo se inventa una tool que no existe.

### Variación en vivo: ponerle precio al modelo

```text
Define en LangFuse un precio de referencia para llama3.1 (0,15 $ / 0,60 $ por millon de tokens) y vuelve a lanzar una pregunta.
```

**Qué demuestra**

Con Ollama el coste real es 0. Dandole un precio de referencia, LangFuse calcula cuanto costaria con una API de pago: la misma traza, ahora con dolares.

---

## Paso 3 · Prompt management

**Qué construye**

- Guardar el prompt en LangFuse, en dos versiones
- El codigo lo pide por nombre y etiqueta
- Mover la etiqueta production a la v2
- Mismo codigo, otra respuesta

**Prompt**

```text
Usa el prompt management de LangFuse: guarda el prompt del chatbot en LangFuse con un nombre, crea una segunda version con un cambio, haz que el codigo cargue el prompt desde LangFuse por nombre, y demuestra que puedo cambiar de version sin tocar ni desplegar el codigo.
```

**Qué deberías ver**

Las dos ejecuciones de 03_prompt_management.py son el MISMO codigo: la v2 responde con otro tono y firma.

### Variación en vivo: rollback en un segundo

```text
Vuelve a poner la etiqueta production en la version 1 del prompt y ejecuta otra vez el mismo script del paso 3.
```

**Qué demuestra**

Si la v2 da problemas en produccion, volver atras es mover una etiqueta: el mismo script carga la version 1 al instante, sin desplegar nada.

---

## Paso 4 · Evaluación

**Qué construye**

- Dataset de 5 preguntas con el dato esperado
- El agente sobre todo el dataset
- Evaluador por regla + juez LLM
- Tabla de resultados

**Prompt**

```text
Crea un dataset pequeno (4-5 ejemplos de entrada y salida esperada) en LangFuse. Ejecuta el grafo sobre todo el dataset, anade un evaluador simple (comprobar que la respuesta contiene algo esperado) y un LLM-as-a-judge, y muestra la tabla de resultados con las metricas.
```

**Qué deberías ver**

La regla dice 100%, el juez solo 40%. ¿Quien tiene razon? Lo vemos en dos slides.

### Variación en vivo: ¿es mejor la v2?

```text
Lanza un experimento por cada version del prompt (v1 y v2) sobre el mismo dataset y compara la metrica contiene_dato.
```

**Qué demuestra**

Las dos aciertan 5 de 5: por esta metrica son iguales. Para decidir por el tono haria falta otro evaluador. Medir en vez de opinar tambien es saber que mide cada metrica.

---

## Paso 5 · La misma ejecución en las dos

**Qué construye**

- Una sola ejecucion del agente
- LangSmith por variables de entorno
- LangFuse por callback
- Dos enlaces, dos vistas

**Prompt**

```text
Prepara una comparativa lado a lado: abre la misma ejecucion en LangFuse y en LangSmith y explica que ofrece cada una. Anade comentarios didacticos al codigo y un README que resuma trazas, spans, prompt management y evaluacion. Deja el proyecto limpio para compartirlo como material de clase.
```

**Qué deberías ver**

Una sola ejecucion y dos enlaces: la misma traza, vista por las dos herramientas.

---

*Material del Master AI Engineer · The Power · Ignacio de Pastors*
