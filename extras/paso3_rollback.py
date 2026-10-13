"""Variacion paso 3 · Rollback: volver a la v1 del prompt en un segundo, sin desplegar nada."""
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")

from langfuse import get_client  # noqa: E402

langfuse = get_client()
langfuse.update_prompt(name="chatbot-soporte", version=1, new_labels=["production"])
langfuse.flush()
print("Rollback: 'production' vuelve a apuntar a la version 1\n", flush=True)

# Ejecutamos el MISMO script del paso 3, sin cambiar ni una linea
subprocess.run([sys.executable, str(RAIZ / "03_prompt_management.py")], cwd=RAIZ, check=True)
