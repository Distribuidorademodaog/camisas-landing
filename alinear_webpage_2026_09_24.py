# -*- coding: utf-8 -*-
"""Alinear el JSON-LD WebPage con los titles nuevos — 2026-09-24.

`cabeza_camibusos_2026_09_24.py` cambio title, og, twitter, description y el H1
oculto de las tres paginas del reparto del termino cabeza, pero NO el nodo
WebPage del JSON-LD, que seguia anunciando el nombre viejo. Ademas, en la pilar
ese string ES una constante del template de `build_landings.py` (RL_WEBPAGE_NAME)
y el build abortaba en [wp:name].
"""
import io, re, sys
DRY = "--dry-run" in sys.argv
N = {
 "index.html": ("Camisas Polo Hombre estilo clásico en Colombia",
                "Camisas Polo para Hombre en Colombia | Tallas S a 5XL"),
 "camisas-polo-premium-colombia.html": ("Camisas Polo para Hombre en Colombia | Polos Estilo Premium",
                "Catálogo de Camisas Polo: Color, Talla y Ocasión"),
 "camisas-hombre-colombia.html": (None,
                "Camisas para Hombre en Colombia | Contraentrega"),
}
for f, (viejo, nuevo) in N.items():
    h = io.open(f, encoding="utf-8").read()
    m = re.search(r'("@type": "WebPage".*?"name": ")([^"]*)(")', h, re.S)
    assert m, f
    if m.group(2) == nuevo:
        print("  = %-36s ya alineado" % f); continue
    print("  · %-36s %s" % (f, m.group(2)[:52]))
    print("    %-36s -> %s" % ("", nuevo))
    h = h[:m.start(2)] + nuevo + h[m.end(2):]
    if not DRY:
        io.open(f, "w", encoding="utf-8", newline="").write(h)
print("\n%s" % ("(DRY-RUN)" if DRY else "aplicado"))
