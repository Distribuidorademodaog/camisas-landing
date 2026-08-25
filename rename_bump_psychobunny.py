# -*- coding: utf-8 -*-
"""Renombra el order bump 'Polo Psycho Bunny' -> 'Polo Bun' en todos los HTML.

Solo toca la cadena del campo `name:` del bump. No cambia precio, imagen,
tallas ni la logica del checkout. Preserva CRLF (newline='').

Uso:  python rename_bump_psychobunny.py [--dry]
"""
import glob, io, os, sys

VIEJO = "Polo Psycho Bunny"
NUEVO = "Polo Bun"
DRY = "--dry" in sys.argv

raiz = os.path.dirname(os.path.abspath(__file__))
archivos = sorted(glob.glob(os.path.join(raiz, "**", "*.html"), recursive=True))
# no tocar artefactos que no se despliegan
EXCLUIR = ("output", "_landings", "_cities", "_blog", "node_modules")

tocados = 0
for ruta in archivos:
    rel = os.path.relpath(ruta, raiz).replace("\\", "/")
    if rel.split("/")[0] in EXCLUIR:
        continue
    with io.open(ruta, encoding="utf-8", newline="") as f:
        s = f.read()
    n = s.count(VIEJO)
    if not n:
        continue
    if n != 1:
        print(f"  OJO {rel}: {n} ocurrencias (se esperaba 1)")
    if not DRY:
        with io.open(ruta, "w", encoding="utf-8", newline="") as f:
            f.write(s.replace(VIEJO, NUEVO))
    tocados += 1

print(f"{'[dry] ' if DRY else ''}{tocados} archivos con '{VIEJO}' -> '{NUEVO}'")
