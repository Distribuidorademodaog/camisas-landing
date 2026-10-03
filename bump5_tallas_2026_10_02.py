# -*- coding: utf-8 -*-
"""Bump 5 (polo premium): tallas agotadas — 2026-10-02.

Decision del negocio:
  blanca, negra, azul oscura -> fuera XXL y 3XL  (quedan S a XL)
  roja                       -> fuera XXL        (queda solo XL)

Tras esto el bump pierde TODA presencia por encima de XL, justo el tramo que
en septiembre fue el 51,7% de las prendas vendidas en los packs. Queda anotado.

Uso:  python bump5_tallas_2026_10_02.py [--dry-run]
"""
import io, re, sys
DRY = "--dry-run" in sys.argv
R = [
 ("{ id: 'roja',      name: 'Roja',       img: 'https://media.paquetecompleto.com.co/order-bumps/polo-roja.webp',      tallas: ['XL','XXL'] }",
  "{ id: 'roja',      name: 'Roja',       img: 'https://media.paquetecompleto.com.co/order-bumps/polo-roja.webp',      tallas: ['XL'] }"),
 ("{ id: 'negra',      name: 'Negra',       img: 'https://media.paquetecompleto.com.co/order-bumps/polo-negra-v2.webp',      tallas: ['S','M','L','XL','XXL','3XL'] }",
  "{ id: 'negra',      name: 'Negra',       img: 'https://media.paquetecompleto.com.co/order-bumps/polo-negra-v2.webp',      tallas: ['S','M','L','XL'] }"),
 ("{ id: 'blanca',     name: 'Blanca',      img: 'https://media.paquetecompleto.com.co/order-bumps/polo-blanca-v2.webp',     tallas: ['S','M','L','XL','XXL','3XL'] }",
  "{ id: 'blanca',     name: 'Blanca',      img: 'https://media.paquetecompleto.com.co/order-bumps/polo-blanca-v2.webp',     tallas: ['S','M','L','XL'] }"),
 ("{ id: 'azuloscura', name: 'Azul oscura', img: 'https://media.paquetecompleto.com.co/order-bumps/polo-azuloscura-v2.webp', tallas: ['S','M','L','XL','XXL','3XL'] }",
  "{ id: 'azuloscura', name: 'Azul oscura', img: 'https://media.paquetecompleto.com.co/order-bumps/polo-azuloscura-v2.webp', tallas: ['S','M','L','XL'] }"),
]
p = "index.html"
h = io.open(p, encoding="utf-8").read()
for v, n in R:
    assert h.count(v) == 1, "esperaba 1 ocurrencia: %r" % v[:70]
    h = h.replace(v, n)
if not DRY:
    io.open(p, "w", encoding="utf-8", newline="").write(h)
# comprobacion: ninguna variante puede quedarse sin tallas
i = h.find("id: 'bump5'"); j = h.find("id: 'bump6'", i)
for m in re.finditer(r"id: '(\w+)',\s+name: '([^']+)'.*?tallas: \[([^\]]*)\]", h[i:j], re.S):
    tl = [t.strip(" '") for t in m.group(3).split(",") if t.strip()]
    assert tl, "%s se quedo SIN tallas" % m.group(2)
    print("   %-13s %s" % (m.group(2), " · ".join(tl)))
print("\n%s" % ("(DRY-RUN)" if DRY else "aplicado en index.html"))
