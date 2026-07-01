"""
build-all.py — Regenera carlo-rondon.html y Carlo Rondon CV.docx desde data.json
Ejecutar desde la raíz del proyecto: python build/build-all.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

def run(script):
    result = subprocess.run([sys.executable, str(script)], cwd=str(ROOT))
    if result.returncode != 0:
        print(f"[ERROR] Error en {script.name}")
        sys.exit(1)

run(ROOT / "build" / "build-html.py")
run(ROOT / "build" / "build-docx.py")
print("\n[DONE] carlo-rondon.html y Carlo Rondon CV.docx actualizados.")
print("       Flujo: editar data.json -> py build/build-all.py -> git push")
