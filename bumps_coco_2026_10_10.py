# -*- coding: utf-8 -*-
"""
Bajas en el Polo Coco (bump6) — 2026-10-10.

Tercera tanda del día, después de bumps_tallas_2026_10_10.py (polo premium y
Purificación) y bumps_camiseta_2026_10_10.py (camiseta peruana).

    roja       S,M,L,XL,XXL  ->  S,M,L,XL      (quita XXL)
    amarilla   S,M,L,XL,XXL  ->  S,M,L,XL      (quita XXL)
    azul rey   S,M,L,XL,XXL  ->  M,L,XL,XXL    (quita S)

⚠️ «quita la L de la beige» NO se aplica: el beige del Polo Coco tiene S, M, XL y
XXL — no tiene L, así que no hay nada que quitar. Se deja igual y se consulta,
porque la alternativa plausible es que fuera XL (que sí tiene) y eso sí cambiaría
lo que un cliente puede pedir. Mejor preguntar que inventar la talla equivocada.

Sin cambios: beige, azul oscura (XL) y negra (XL). Siguen 6 colores y 23 en total.

La configuración está DUPLICADA en las 79 páginas con checkout: aquí se toca solo
index.html y la propagación la hace unificar_order_bumps_2026_09_11.py.

Uso:  python bumps_coco_2026_10_10.py [--dry-run]
      python unificar_order_bumps_2026_09_11.py
"""
import io
import os
import re
import shutil
import sys
import time

DRY = "--dry-run" in sys.argv
STAMP = time.strftime("%Y%m%d-%H%M")
PATH = "index.html"
BUMP = "bump6"
ORDEN = ["S", "M", "L", "XL", "XXL", "3XL"]

# (variant id, tallas que se quitan)
CAMBIOS = [
    ("roja",     ["XXL"]),
    ("amarilla", ["XXL"]),
    ("azulrey",  ["S"]),
]

# Lo que se pidió pero no se aplica, con el motivo.
NO_APLICADO = [
    ("beige", ["L"], "el beige no tiene L (tiene S, M, XL, XXL): nada que quitar"),
]

ESPERADO = {
    "roja":       ["S", "M", "L", "XL", "XXL"],
    "amarilla":   ["S", "M", "L", "XL", "XXL"],
    "azulrey":    ["S", "M", "L", "XL", "XXL"],
    "beige":      ["S", "M", "XL", "XXL"],
    "azuloscura": ["XL"],
    "negra":      ["XL"],
}


def limites(h, bump):
    cfg = h.find("const ORDER_BUMPS_CONFIG")
    i = h.find("id: '%s'" % bump, cfg)
    if i < 0:
        raise SystemExit("!! no encuentro %s" % bump)
    j = h.find("id: 'bump", i + 10)
    if j < 0:
        j = h.find("\n];", i)
    return i, j


def linea(h, bump, vid):
    a, b = limites(h, bump)
    m = re.search(r"[ \t]*\{ id: '%s',.*?\n" % re.escape(vid), h[a:b], re.S)
    return (a + m.start(), a + m.end(), m.group(0)) if m else None


def tallas_de(s):
    m = re.search(r"tallas: \[([^\]]*)\]", s)
    return [t.strip().strip("'") for t in m.group(1).split(",") if t.strip()] if m else None


def main():
    h = io.open(PATH, encoding="utf-8").read()

    print("=== estado de partida (bump6 Polo Coco) ===")
    for vid, esp in ESPERADO.items():
        r = linea(h, BUMP, vid)
        if not r:
            raise SystemExit("!! %s/%s no existe" % (BUMP, vid))
        act = tallas_de(r[2])
        print("  %s %-12s %s" % ("OK" if act == esp else "!!", vid, ", ".join(act)))
        if act != esp:
            raise SystemExit("!! %s esperaba [%s] y hay [%s]: el inventario cambio, abortando"
                             % (vid, ", ".join(esp), ", ".join(act)))

    print("\n=== cambios ===")
    for vid, quitar in CAMBIOS:
        ini, fin, lin = linea(h, BUMP, vid)
        antes = tallas_de(lin)
        faltan = [t for t in quitar if t not in antes]
        if faltan:
            raise SystemExit("!! %s no tiene %s, no puedo quitarlo" % (vid, ", ".join(faltan)))
        calc = [t for t in antes if t not in quitar]
        if not calc:
            raise SystemExit("!! %s se quedaria sin tallas" % vid)
        nueva = re.sub(r"tallas: \[[^\]]*\]",
                       "tallas: [%s]" % ",".join("'%s'" % t for t in calc), lin, count=1)
        h = h[:ini] + nueva + h[fin:]
        print("  +  %-12s %-20s -> %-18s (quita %s)"
              % (vid, ", ".join(antes), ", ".join(calc), ", ".join(quitar)))

    print("\n=== pedido pero NO aplicado ===")
    for vid, quitar, motivo in NO_APLICADO:
        r = linea(h, BUMP, vid)
        act = tallas_de(r[2])
        print("  ?  %-12s se pidio quitar %-4s pero %s" % (vid, ", ".join(quitar), motivo))
        print("     queda igual: %s" % ", ".join(act))

    print("\n=== comprobaciones ===")
    fallos = []
    a, b = limites(h, BUMP)
    vs = re.findall(r"id: '([^']*)',\s*name: '([^']*)',\s*img: '[^']*',\s*tallas: \[([^\]]*)\]", h[a:b])
    print("  bump6: %d colores" % len(vs))
    for vid, nombre, tal in vs:
        if not [t for t in tal.split(",") if t.strip()]:
            fallos.append("%s sin tallas" % vid)

    cfg_ini = h.find("const ORDER_BUMPS_CONFIG")
    cfg = h[cfg_ini:h.find("\n];", cfg_ini) + 3]
    print("\n  cobertura por talla (los 4 upsells):")
    print("    %-22s %s" % ("", "  ".join("%-4s" % t for t in ORDEN)))
    for mb in re.finditer(r"id: '(bump\d+)',\s*\n?\s*name: '([^']*)'", cfg):
        bid, nombre = mb.group(1), mb.group(2)
        aa, bb = limites(h, bid)
        listas = [[t.strip().strip("'") for t in x.split(",") if t.strip()]
                  for x in re.findall(r"tallas: \[([^\]]*)\]", h[aa:bb])]
        print("    %-22s %s" % (nombre[:22],
              "  ".join("%-4d" % sum(1 for l in listas if t in l) for t in ORDEN)))
    todas = [[t.strip().strip("'") for t in x.split(",") if t.strip()]
             for x in re.findall(r"tallas: \[([^\]]*)\]", cfg)]
    print("    %-22s %s" % ("TOTAL", "  ".join("%-4d" % sum(1 for l in todas if t in l) for t in ORDEN)))
    print("  colores totales: %d" % len(todas))
    if fallos:
        raise SystemExit("!! " + " | ".join(fallos))
    print("  sin fallos")

    if not DRY:
        shutil.copy(PATH, PATH + ".bak-coco-" + STAMP)
        tmp = PATH + ".tmp"
        io.open(tmp, "w", encoding="utf-8", newline="").write(h)
        os.replace(tmp, PATH)
    print("\n%s" % ("(DRY-RUN: no se escribio nada)" if DRY
                    else "index.html actualizado — backup .bak-coco-%s" % STAMP))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
