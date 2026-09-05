# -*- coding: utf-8 -*-
"""
Quita el badge "Pagas cuando la recibes / la revisas antes de pagar" — 2026-09-05.

Decision del negocio. Es el bloque <div class="hero-proof"> del hero, identico
en las 65 paginas que lo tienen (una sola variante, verificado). Se quitan
tambien las 3 reglas CSS que quedan muertas al sacarlo.

NO se toca la prosa del cuerpo ni las FAQ, que hablan de contraentrega con otras
palabras ("puedes revisar la camisa antes de pagarla", "¿Puedo abrir el paquete
antes de pagar?"). Son frases dentro de parrafos: borrarlas dejaria oraciones
rotas y se llevaria por delante el argumento de venta del contraentrega, que no
es lo que se pidio. Si tambien hay que quitarlas, es otra pasada y a mano.

Uso:  python quitar_hero_proof_2026_09_05.py [--dry-run]
"""
import glob
import io
import os
import re
import sys

BLOQUE = re.compile(
    r'\n[ \t]*<div class="hero-proof">\s*'
    r'<div class="hero-proof-text">\s*'
    r'<strong>Pagas cuando la recibes</strong>\s*'
    r'la revisas antes de pagar\s*'
    r'</div>\s*</div>', re.S)

CSS = [
    re.compile(r'\n[ \t]*\.hero-proof \{[^}]*\}'),
    re.compile(r'\n[ \t]*\.hero-proof-text \{[^}]*\}'),
    re.compile(r'\n[ \t]*\.hero-proof-text strong \{[^}]*\}'),
]


def main():
    dry = "--dry-run" in sys.argv
    paginas = sorted(set(p.replace(os.sep, "/") for p in
                     glob.glob("*.html") + glob.glob("blog/*.html")
                     + glob.glob("guias/*.html")))
    n_blq = n_css = 0
    tocados = []
    for f in paginas:
        h = io.open(f, encoding="utf-8").read()
        orig = h
        h, k = BLOQUE.subn("", h, count=1)
        n_blq += k
        kc = 0
        for c in CSS:
            h, x = c.subn("", h, count=1)
            kc += x
        n_css += kc
        if h == orig:
            continue
        # ni una mencion suelta puede quedar
        assert "hero-proof" not in h, "%s: quedaron restos de hero-proof" % f
        tocados.append((f, k, kc))
        if not dry:
            io.open(f, "w", encoding="utf-8", newline="").write(h)

    for f, k, kc in tocados[:5]:
        print("  %-44s bloque=%d css=%d" % (f, k, kc))
    if len(tocados) > 5:
        print("  ... y %d paginas mas" % (len(tocados) - 5))
    print("\n%d paginas: %d bloques y %d reglas CSS fuera%s"
          % (len(tocados), n_blq, n_css, "  (DRY-RUN)" if dry else ""))

    # la fuente de _landings no lleva el hero (viene de la plantilla), pero el
    # section.html si podria mencionarlo: se comprueba y se avisa
    restos = [p for p in glob.glob("_landings/*.section.html")
              + glob.glob("_cities/*.section.html")
              if "hero-proof" in io.open(p, encoding="utf-8").read()]
    print("fuentes de _landings/_cities con hero-proof: %s" % (restos or "ninguna"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
