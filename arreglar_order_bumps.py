# -*- coding: utf-8 -*-
"""Limpia las marcas ajenas de los order bumps en todos los HTML desplegables.

  1. 'Polo Purificación García'   -> 'Polo Purificación'
  2. 'Polo Lacoste'               -> 'Polo Coco'
  3. bump 'Camiseta Selección Colombia' -> se ELIMINA el objeto completo

Solo toca el array ORDER_BUMPS_CONFIG. No cambia precios, imagenes, tallas
ni la logica del checkout. Preserva CRLF (newline='').

Uso:  python arreglar_order_bumps.py [--dry]
"""
import glob, io, os, sys

DRY = "--dry" in sys.argv
RENOMBRAR = [
    ("Polo Purificación García", "Polo Purificación"),
    ("Polo Lacoste", "Polo Coco"),
]
ELIMINAR = "Camiseta Selección Colombia"
EXCLUIR = ("output", "_landings", "_cities", "_blog", "node_modules")


def quitar_bump(s, nombre):
    """Borra el objeto {...} del array que contiene name: '<nombre>'."""
    i = s.find(f"name: '{nombre}'")
    if i == -1:
        return s, 0
    # hacia atras hasta la llave que abre el objeto
    ini = s.rfind("{", 0, i)
    # incluir la indentacion y el salto de linea previos
    while ini > 0 and s[ini - 1] in " \t":
        ini -= 1
    # brace matching hacia adelante
    prof, j = 0, s.find("{", i - (i - ini))
    j = s.find("{", ini)
    while j < len(s):
        if s[j] == "{":
            prof += 1
        elif s[j] == "}":
            prof -= 1
            if prof == 0:
                break
        j += 1
    fin = j + 1
    if s[fin:fin + 1] == ",":            # coma separadora del array
        fin += 1
    while s[fin:fin + 2] in ("\r\n",) or s[fin:fin + 1] == "\n":
        fin += 2 if s[fin:fin + 2] == "\r\n" else 1
        break
    return s[:ini] + s[fin:], 1


raiz = os.path.dirname(os.path.abspath(__file__))
stats = {v: 0 for _, v in RENOMBRAR}
stats["bump eliminado"] = 0
tocados = 0

for ruta in sorted(glob.glob(os.path.join(raiz, "**", "*.html"), recursive=True)):
    rel = os.path.relpath(ruta, raiz).replace("\\", "/")
    if rel.split("/")[0] in EXCLUIR:
        continue
    with io.open(ruta, encoding="utf-8", newline="") as f:
        orig = f.read()
    s = orig
    for viejo, nuevo in RENOMBRAR:
        if viejo in s:
            s = s.replace(viejo, nuevo)
            stats[nuevo] += 1
    s, n = quitar_bump(s, ELIMINAR)
    stats["bump eliminado"] += n
    if s != orig:
        tocados += 1
        if not DRY:
            with io.open(ruta, "w", encoding="utf-8", newline="") as f:
                f.write(s)

print(("[dry] " if DRY else "") + f"{tocados} archivos modificados")
for k, v in stats.items():
    print(f"  {k}: {v}")
