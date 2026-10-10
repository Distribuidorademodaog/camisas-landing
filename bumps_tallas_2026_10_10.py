# -*- coding: utf-8 -*-
"""
Inventario de order bumps: bajas en polo premium y Purificación — 2026-10-10.

Pedido del negocio sobre el estado del 10-oct. Tres instrucciones no cuadraban
con la configuración en vivo y se confirmaron antes de tocar nada:

 1. «blanco deja solo L y XXL» en Purificación — hoy tiene XL, XXL y 3XL, no L.
    Confirmado literal: AÑADE L y quita XL y 3XL.
 2. «Amarillo solo Deja XL» en polo premium — hoy tiene M y L, no XL.
    Confirmado literal: AÑADE XL y quita M y L.
 3. «en azul rey borra 3XL» venía bajo polo premium, pero ese azul rey solo tiene
    XL (y además se borra entero). El que tiene 3XL es el de Purificación.
    Confirmado: era el de Purificación, que pierde S y 3XL.

Resultado:

    POLO PREMIUM   6 colores -> 3     se borran blanca, azul rey y roja
      amarilla      M, L          ->  XL
      negra         S, M, L, XL   ->  igual (ya era exactamente eso)
      azul oscura   S, M, L, XL   ->  igual

    PURIFICACIÓN   5 colores -> 4     se borra verde militar
      negra         L, XL, XXL, 3XL        ->  XXL
      beige         S, M, L, XL, XXL, 3XL  ->  igual
      azul rey      S, M, L, XL, XXL, 3XL  ->  M, L, XL, XXL
      blanca        XL, XXL, 3XL           ->  L, XXL

Total: 27 colores -> 23.

⚠️ polo premium se queda sin blanco y sin ningún color por encima de XL. Sumado a
que ya no tenía XXL ni 3XL desde el 2-oct, un cliente de XXL o 3XL no verá este
upsell en absoluto (el filtro esconde el bump completo cuando ningún color aplica).

La configuración está DUPLICADA en las 79 páginas con checkout. Aquí se toca solo
index.html, que es la canónica; la propagación la hace después
unificar_order_bumps_2026_09_11.py, que además valida con node que ninguna
variante quede sin tallas y que no haya ids repetidos.

Uso:  python bumps_tallas_2026_10_10.py [--dry-run]
      python unificar_order_bumps_2026_09_11.py      # propaga a las 79
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

# ── cambios de tallas: (bump, variant id, tallas nuevas) ─────────────────────
TALLAS = [
    ("bump5", "amarilla",  ["XL"]),
    ("bump7", "negra",     ["XXL"]),
    ("bump7", "azulrey",   ["M", "L", "XL", "XXL"]),
    ("bump7", "blanca",    ["L", "XXL"]),
]

# ── variantes que se borran enteras: (bump, variant id) ──────────────────────
BORRAR = [
    ("bump5", "blanca"),
    ("bump5", "azulrey"),
    ("bump5", "roja"),
    ("bump7", "verdemilitar"),
]

# Estado esperado antes de tocar. Si no coincide, se aborta: significa que alguien
# cambio el inventario entre la consulta y el parche.
ESPERADO = {
    ("bump5", "amarilla"):     ["M", "L"],
    ("bump5", "azulrey"):      ["XL"],
    ("bump5", "roja"):         ["XL"],
    ("bump5", "blanca"):       ["S", "M", "L", "XL"],
    ("bump7", "negra"):        ["L", "XL", "XXL", "3XL"],
    ("bump7", "azulrey"):      ["S", "M", "L", "XL", "XXL", "3XL"],
    ("bump7", "blanca"):       ["XL", "XXL", "3XL"],
    ("bump7", "verdemilitar"): ["L", "XL", "XXL"],
}


def limites_bump(h, bump):
    """(inicio, fin) del bloque de un bump dentro de ORDER_BUMPS_CONFIG."""
    cfg = h.find("const ORDER_BUMPS_CONFIG")
    i = h.find("id: '%s'" % bump, cfg)
    if i < 0:
        raise SystemExit("!! no encuentro %s" % bump)
    j = h.find("id: 'bump", i + 10)
    if j < 0:                       # ultimo bump: hasta el cierre del array
        j = h.find("\n];", i)
    return i, j


def linea_variant(h, bump, vid):
    """La linea completa de una variant (incluido su salto final)."""
    a, b = limites_bump(h, bump)
    m = re.search(r"[ \t]*\{ id: '%s',.*?\n" % re.escape(vid), h[a:b], re.S)
    if not m:
        return None
    return a + m.start(), a + m.end(), m.group(0)


def tallas_de(linea):
    m = re.search(r"tallas: \[([^\]]*)\]", linea)
    return [t.strip().strip("'") for t in m.group(1).split(",")] if m else None


def main():
    h = io.open(PATH, encoding="utf-8").read()

    # ── 1. comprobar el estado de partida ────────────────────────────────────
    print("=== estado de partida ===")
    for (bump, vid), esp in sorted(ESPERADO.items()):
        r = linea_variant(h, bump, vid)
        if not r:
            print("  !! %s/%s no existe — puede que ya este aplicado" % (bump, vid))
            continue
        act = tallas_de(r[2])
        ok = act == esp
        print("  %s %s/%-13s %s" % ("OK" if ok else "!!", bump, vid, ", ".join(act or [])))
        if not ok:
            raise SystemExit("!! %s/%s esperaba [%s] y hay [%s]: el inventario cambio, "
                             "abortando" % (bump, vid, ", ".join(esp), ", ".join(act or [])))

    # ── 2. tallas nuevas ────────────────────────────────────────────────────
    print("\n=== tallas nuevas ===")
    for bump, vid, nuevas in TALLAS:
        r = linea_variant(h, bump, vid)
        if not r:
            print("  !! %s/%s no existe" % (bump, vid))
            continue
        ini, fin, linea = r
        antes = tallas_de(linea)
        if antes == nuevas:
            print("  =  %s/%-13s ya esta en %s" % (bump, vid, ", ".join(nuevas)))
            continue
        nueva_linea = re.sub(r"tallas: \[[^\]]*\]",
                             "tallas: [%s]" % ",".join("'%s'" % t for t in nuevas),
                             linea, count=1)
        h = h[:ini] + nueva_linea + h[fin:]
        print("  +  %s/%-13s %-22s -> %s" % (bump, vid, ", ".join(antes), ", ".join(nuevas)))

    # ── 3. variantes que se borran ──────────────────────────────────────────
    print("\n=== colores que se borran ===")
    for bump, vid in BORRAR:
        r = linea_variant(h, bump, vid)
        if not r:
            print("  =  %s/%-13s ya no estaba" % (bump, vid))
            continue
        ini, fin, linea = r
        h = h[:ini] + h[fin:]
        print("  -  %s/%-13s (tenia %s)" % (bump, vid, ", ".join(tallas_de(linea) or [])))

    # ── 4. comprobaciones ───────────────────────────────────────────────────
    print("\n=== comprobaciones ===")
    cfg_ini = h.find("const ORDER_BUMPS_CONFIG")
    cfg = h[cfg_ini:h.find("\n];", cfg_ini) + 3]
    fallos = []
    for mb in re.finditer(r"id: '(bump\d+)'", cfg):
        bump = mb.group(1)
        a, b = limites_bump(h, bump)
        blq = h[a:b]
        vs = re.findall(r"id: '([^']*)',\s*name: '([^']*)',\s*img: '[^']*',\s*tallas: \[([^\]]*)\]", blq)
        if not vs:
            fallos.append("%s se quedo sin colores" % bump)
        for vid, nombre, tal in vs:
            lst = [t.strip().strip("'") for t in tal.split(",") if t.strip()]
            if not lst:
                fallos.append("%s/%s se quedo sin tallas" % (bump, vid))
        ids = [v[0] for v in vs]
        if len(set(ids)) != len(ids):
            fallos.append("%s tiene ids repetidos" % bump)
        print("  %s: %d colores" % (bump, len(vs)))
    for v in BORRAR:
        a, b = limites_bump(h, v[0])
        if ("id: '%s'" % v[1]) in h[a:b]:
            fallos.append("%s/%s sigue presente" % v)
    total = len(re.findall(r"tallas: \[", cfg))
    print("  colores totales: %d (eran 27)" % total)
    if fallos:
        raise SystemExit("!! " + " | ".join(fallos))
    print("  sin fallos")

    if not DRY:
        shutil.copy(PATH, PATH + ".bak-bumps-" + STAMP)
        tmp = PATH + ".tmp"
        io.open(tmp, "w", encoding="utf-8", newline="").write(h)
        os.replace(tmp, PATH)
    print("\n%s" % ("(DRY-RUN: no se escribio nada)" if DRY
                    else "index.html actualizado — backup .bak-bumps-%s" % STAMP))
    print("Siguiente:  python unificar_order_bumps_2026_09_11.py   # propaga a las 79 paginas")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
