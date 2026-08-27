# -*- coding: utf-8 -*-
"""
Enlazado contextual hacia la pilar para romper la canibalizacion — 2026-08-27.

Diagnostico (GSC 28 abr - 25 ago 2026, cruce consulta x pagina):
  En "camisas polo" compiten OCHO paginas propias, todas en posicion 39-68:

      /camisas-hombre-colombia          29 impr  pos 39,5
      /camisas-polo-juveniles-hombre    10 impr  pos 50,9
      /camisas-polo-baratas-colombia     9 impr  pos 62,0
      /  y 5 mas                                 pos 45-68

  Ninguna es la pilar /camisas-polo-premium-colombia. Al revisar el enlazado se
  ve por que: de esas 8 paginas solo UNA enlaza a la pilar, ninguna con el ancla
  "camisas polo", y el home ni siquiera la enlaza. Google no tiene señal de cual
  de las ocho es la buena.

Por que un enlace en la PROSA y no un bloque nuevo:
  Los bloques .cc-relacionados que se inyectaron en la auditoria del 13 de ago
  ya no existen: las landings se regeneran desde _landings/*.section.html y el
  build los borro. Un <a> dentro de un parrafo que ya menciona el termino
  sobrevive mejor, no añade DOM y es una señal contextual mas fuerte que un
  chip al pie.

Que hace: envuelve la PRIMERA mencion sin enlazar de "camisas polo" en un
parrafo que no tenga ya enlaces, apuntando a la pilar. Una sola por pagina.

Uso:  python seo_pilar_2026_08_27.py [--dry-run]
"""
import io
import re
import sys

PILAR = "/camisas-polo-premium-colombia"

PAGINAS = [
    "index.html",
    "camisas-hombre-colombia.html",
    "camisas-polo-juveniles-hombre.html",
    "camisas-polo-baratas-colombia.html",
    "camisas-polo-colores-hombre.html",
    "pack-camisas-polo-hombre.html",
    "camisas-polo-bogota.html",
    "polos-hombre-colombia.html",
    "camisas-casuales-hombre-colombia.html",
]

# El ancla ideal es "camisas polo para hombre"; si no aparece, se acepta
# "camisas polo" a secas. Nunca en singular: el termino que canibaliza es plural.
PATRONES = [
    re.compile(r"camisas polo para hombre", re.I),
    re.compile(r"camisas polo", re.I),
]

MARCA = 'data-link="pilar-2026-08"'


def enlazar(html, destino):
    """Envuelve la primera mencion apta. Devuelve (html, ancla) o (html, None)."""
    if MARCA in html:
        return html, None

    for pat in PATRONES:
        for pm in re.finditer(r"<p[^>]*>(.*?)</p>", html, re.S):
            cuerpo = pm.group(1)
            if "<a" in cuerpo or "${" in cuerpo:
                continue  # ya tiene enlace, o es plantilla JS
            m = pat.search(cuerpo)
            if not m:
                continue
            ancla = m.group(0)
            nuevo_cuerpo = (cuerpo[:m.start()]
                            + '<a href="%s" %s>%s</a>' % (destino, MARCA, ancla)
                            + cuerpo[m.end():])
            ini, fin = pm.span(1)
            return html[:ini] + nuevo_cuerpo + html[fin:], ancla
    return html, None


def main():
    dry = "--dry-run" in sys.argv
    ok = 0
    for path in PAGINAS:
        h = io.open(path, encoding="utf-8").read()
        nuevo, ancla = enlazar(h, PILAR)
        if ancla is None:
            print("%-40s sin mencion apta o ya enlazada" % path)
            continue
        # el <a> no puede desbalancear nada
        assert nuevo.count("<p") == h.count("<p"), "parrafos alterados"
        assert nuevo.count("<a") == h.count("<a") + 1, "enlaces inesperados"
        if not dry:
            io.open(path, "w", encoding="utf-8", newline="").write(nuevo)
        print('%-40s ancla: "%s"' % (path, ancla))
        ok += 1
    print("\n%d enlaces a la pilar%s" % (ok, " (simulacion)" if dry else ""))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
