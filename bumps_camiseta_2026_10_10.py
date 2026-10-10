# -*- coding: utf-8 -*-
"""
Bajas en la camiseta 100 % algodón peruano (bump2) — 2026-10-10.

Segunda tanda del mismo día, después de bumps_tallas_2026_10_10.py (que tocó
polo premium y Purificación). Aquí solo cambia bump2.

    blanca         S,M,L,XL,XXL,3XL  ->  S,M,L,XL,XXL      (quita 3XL)
    negra          S,M,L,XL,XXL,3XL  ->  S,M,L,XL,XXL      (quita 3XL)
    azul oscura    S,M,L,XL,XXL,3XL  ->  M,L,XL,XXL        (quita 3XL y S)
    verde          S,M,L,XL,XXL,3XL  ->  S,M,L,XXL,3XL     (quita XL)
    amarilla       S,M,L,XL          ->  S,M,L             (quita XL)
    verde botella  S,L,XXL,3XL       ->  XXL,3XL           (quita S y L)
    azul rey       XXL,3XL           ->  3XL               (quita XXL)
    azul medio     XXL,3XL           ->  3XL               (quita XXL)

Sin cambios: vinotinto (L,XXL,3XL) y celeste (3XL).

⚠️ «verde oscuro» no es un nombre que exista en la configuración: hay «Verde» y
«Verde botella». Se interpreta como Verde botella, porque la instrucción anterior
(«en verde quita xl») solo puede ser Verde — Verde botella no tiene XL. Además
Verde botella sí tiene S y L, así que la instrucción encaja.

⚠️ Ningún color queda vacío, pero tres se quedan con una sola talla (azul rey,
azul medio y celeste, las tres solo en 3XL). Y XL pasa de 5 colores a 3 en este
bump, que era el único upsell con surtido amplio en XL.

La configuración está DUPLICADA en las 79 páginas con checkout: aquí se toca solo
index.html y la propagación la hace unificar_order_bumps_2026_09_11.py.

Uso:  python bumps_camiseta_2026_10_10.py [--dry-run]
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
BUMP = "bump2"

# (variant id, tallas que se quitan, tallas que deben quedar)
CAMBIOS = [
    ("blanca",       ["3XL"],      ["S", "M", "L", "XL", "XXL"]),
    ("negra",        ["3XL"],      ["S", "M", "L", "XL", "XXL"]),
    ("azuloscura",   ["3XL", "S"], ["M", "L", "XL", "XXL"]),
    ("verde",        ["XL"],       ["S", "M", "L", "XXL", "3XL"]),
    ("amarilla",     ["XL"],       ["S", "M", "L"]),
    ("verdebotella", ["S", "L"],   ["XXL", "3XL"]),
    ("azulrey",      ["XXL"],      ["3XL"]),
    ("azulmedio",    ["XXL"],      ["3XL"]),
]

ESPERADO = {
    "blanca":       ["S", "M", "L", "XL", "XXL", "3XL"],
    "negra":        ["S", "M", "L", "XL", "XXL", "3XL"],
    "azuloscura":   ["S", "M", "L", "XL", "XXL", "3XL"],
    "verde":        ["S", "M", "L", "XL", "XXL", "3XL"],
    "amarilla":     ["S", "M", "L", "XL"],
    "verdebotella": ["S", "L", "XXL", "3XL"],
    "azulrey":      ["XXL", "3XL"],
    "azulmedio":    ["XXL", "3XL"],
}
ORDEN = ["S", "M", "L", "XL", "XXL", "3XL"]


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

    print("=== estado de partida (bump2) ===")
    for vid, esp in ESPERADO.items():
        r = linea(h, BUMP, vid)
        if not r:
            raise SystemExit("!! %s/%s no existe" % (BUMP, vid))
        act = tallas_de(r[2])
        print("  %s %-13s %s" % ("OK" if act == esp else "!!", vid, ", ".join(act)))
        if act != esp:
            raise SystemExit("!! %s esperaba [%s] y hay [%s]: el inventario cambio, abortando"
                             % (vid, ", ".join(esp), ", ".join(act)))

    print("\n=== cambios ===")
    for vid, quitar, queda in CAMBIOS:
        ini, fin, lin = linea(h, BUMP, vid)
        antes = tallas_de(lin)
        # el resultado se calcula quitando, y se comprueba contra lo declarado
        calc = [t for t in antes if t not in quitar]
        if calc != queda:
            raise SystemExit("!! %s: quitar %s de [%s] da [%s], pero declare [%s]"
                             % (vid, quitar, ", ".join(antes), ", ".join(calc), ", ".join(queda)))
        if not calc:
            raise SystemExit("!! %s se quedaria sin tallas" % vid)
        nueva = re.sub(r"tallas: \[[^\]]*\]",
                       "tallas: [%s]" % ",".join("'%s'" % t for t in calc), lin, count=1)
        h = h[:ini] + nueva + h[fin:]
        print("  +  %-13s %-24s -> %-18s (quita %s)"
              % (vid, ", ".join(antes), ", ".join(calc), ", ".join(quitar)))

    print("\n=== comprobaciones ===")
    fallos = []
    a, b = limites(h, BUMP)
    vs = re.findall(r"id: '([^']*)',\s*name: '([^']*)',\s*img: '[^']*',\s*tallas: \[([^\]]*)\]", h[a:b])
    print("  bump2: %d colores" % len(vs))
    for vid, nombre, tal in vs:
        lst = [t.strip().strip("'") for t in tal.split(",") if t.strip()]
        if not lst:
            fallos.append("%s sin tallas" % vid)
    una = [n for _, n, t in vs if len([x for x in t.split(",") if x.strip()]) == 1]
    if una:
        print("  (aviso) colores con una sola talla: %s" % ", ".join(una))
    # cobertura del sitio completo
    cfg_ini = h.find("const ORDER_BUMPS_CONFIG")
    cfg = h[cfg_ini:h.find("\n];", cfg_ini) + 3]
    print("\n  cobertura por talla (los 4 upsells):")
    print("    %-22s %s" % ("", "  ".join("%-4s" % t for t in ORDEN)))
    for mb in re.finditer(r"id: '(bump\d+)',\s*\n?\s*name: '([^']*)'", cfg):
        bid, nombre = mb.group(1), mb.group(2)
        aa, bb = limites(h, bid)
        vv = re.findall(r"tallas: \[([^\]]*)\]", h[aa:bb])
        listas = [[t.strip().strip("'") for t in x.split(",") if t.strip()] for x in vv]
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
        shutil.copy(PATH, PATH + ".bak-cam-" + STAMP)
        tmp = PATH + ".tmp"
        io.open(tmp, "w", encoding="utf-8", newline="").write(h)
        os.replace(tmp, PATH)
    print("\n%s" % ("(DRY-RUN: no se escribio nada)" if DRY
                    else "index.html actualizado — backup .bak-cam-%s" % STAMP))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
