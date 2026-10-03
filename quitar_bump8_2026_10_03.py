# -*- coding: utf-8 -*-
"""Retirar el order bump 8 «Polo Bun» — 2026-10-03.

Decision del negocio. Los bumps se pintan dinamicamente desde
ORDER_BUMPS_CONFIG (renderBumps / renderWompiBumps / bumpsForCustomer), y no
hay NINGUNA referencia a 'bump8' fuera de la config: basta con borrar su bloque.

El bloque retirado queda copiado aqui abajo por si hay que devolverlo:

  {
    id: 'bump8',
    name: 'Polo Bun',
    precioAntes: 95000,
    precioAhora: 70000,
    variants: [
      lila       S M L XL XXL      psychobunny-lila.webp
      blanca     S M L XL XXL      psychobunny-blanca.webp
      roja       M XL XXL          psychobunny-roja.webp
      rosada     M L XL XXL        psychobunny-rosada.webp
      negra      M L XL XXL        psychobunny-negra.webp
      azuloscura XL XXL            psychobunny-azuloscura.webp
      verde      XXL               psychobunny-verde.webp
      vino       XXL               psychobunny-vino.webp
    ]
  }

Uso:  python quitar_bump8_2026_10_03.py [--dry-run]
"""
import io, re, sys
DRY = "--dry-run" in sys.argv
p = "index.html"
h = io.open(p, encoding="utf-8").read()

ini = h.find("  {\n    id: 'bump8'")
assert ini > 0, "no encuentro el bloque de bump8"
fin = h.find("\n];", ini)
assert fin > ini, "no encuentro el cierre del array"
# bump8 es el ultimo: hay que llevarse tambien la coma que cierra bump7
antes = h[:ini].rstrip()
assert antes.endswith("},"), "esperaba que el bloque anterior cerrara con '},'"
nuevo = antes[:-1] + "\n" + h[fin + 1:]

ids_antes = re.findall(r"id: '(bump\d+)'", h)
ids_despues = re.findall(r"id: '(bump\d+)'", nuevo)
print("  bumps antes:   %s" % ", ".join(ids_antes))
print("  bumps despues: %s" % ", ".join(ids_despues))
assert ids_despues == [b for b in ids_antes if b != "bump8"], "se perdio algun bump"
assert "psychobunny" not in nuevo, "quedaron imagenes de Polo Bun"

if not DRY:
    io.open(p, "w", encoding="utf-8", newline="").write(nuevo)
print("\n%s" % ("(DRY-RUN)" if DRY else "aplicado en index.html"))
