# -*- coding: utf-8 -*-
"""
Enlaces en prosa hacia el cluster de tallas desde las 64 paginas con checkout
— 2026-09-17.

Motivo: las 5 paginas de talla (/camisas-xxl-hombre, /camisas-3xl-hombre,
/camisas-4xl-hombre, /camisas-5xl-hombre y /tallas-de-camisas-hombre-colombia)
se crearon el 21-ago y 27 dias despues la URL Inspection API dice de cuatro
«Google no reconoce esta URL» y de la quinta «descubierta, sin indexar». Estan
en el sitemap (descargado el 13-sep) y tienen 19 enlaces, pero todos desde
paginas frias (colores, blogs, entre ellas mismas): ni el home ni las ciudades
grandes las enlazan. Mismo cuadro que [[feedback_descubierta_no_rastreada_enlaces_frios]].

Mientras tanto «talla 3xl» esta en posicion 5,9 con el articulo del blog al
0,9% de CTR; el hub de tallas grandes convierte al 3,7%.

Que hace: el parrafo compartido «En Camisas Colombia distribuimos…» termina en
«con tallas de S a 5XL.» en 64 paginas (home, 21 ciudades, pilar, landings).
Se le anade UNA frase con los 5 enlaces. En cada pagina de talla su propio
enlace se muestra como <strong> (sin autoenlace). Y el callout del articulo de
tallas grandes enlaza a las tres paginas de talla, no solo al hub.

Uso:  python enlazar_tallas_2026_09_17.py [--dry-run]
"""
import glob
import io
import os
import sys

DRY = "--dry-run" in sys.argv
ANCLA = "con tallas <strong>de S a 5XL</strong>."
TALLAS = [
    ("camisas-xxl-hombre", "camisas XXL"),
    ("camisas-3xl-hombre", "camisas 3XL"),
    ("camisas-4xl-hombre", "camisas 4XL"),
    ("camisas-5xl-hombre", "camisas 5XL"),
]
TABLA = ("tallas-de-camisas-hombre-colombia", "tabla de tallas en centímetros")
MARCA = 'data-link="tallas-2026-09"'


def frase(propia):
    def a(slug, txt):
        if slug == propia:
            return "<strong>%s</strong>" % txt
        return '<a href="/%s" %s>%s</a>' % (slug, MARCA, txt)
    partes = [a(s, t) for s, t in TALLAS]
    return (" Las tallas grandes tienen página propia: %s, %s, %s y %s, con su %s."
            % (partes[0], partes[1], partes[2], partes[3], a(*TABLA)))


def main():
    pgs = sorted(p for p in glob.glob("*.html") if p not in ("404.html", "gracias.html"))
    tocadas = ya = 0
    for f in pgs:
        h = io.open(f, encoding="utf-8").read()
        if MARCA in h:
            ya += 1
            continue
        if h.count(ANCLA) != 1:
            continue
        h = h.replace(ANCLA, ANCLA + frase(f[:-5]))
        tocadas += 1
        if not DRY:
            io.open(f, "w", encoding="utf-8", newline="").write(h)
    print("parrafo compartido: %d paginas enlazadas (%d ya lo tenian)" % (tocadas, ya))

    # callout del articulo de tallas grandes
    f = "blog/tallas-grandes-3xl-4xl-5xl.html"
    h = io.open(f, encoding="utf-8").read()
    v = ('<a href="/camisas-hombre-tallas-grandes"><strong>camisas en tallas grandes 3XL, 4XL y 5XL</strong></a>: '
         'producto, colores, tallas S-5XL y pago contraentrega con envío gratis a toda Colombia.')
    n = ('<a href="/camisas-hombre-tallas-grandes"><strong>camisas en tallas grandes</strong></a> o entra directo a la talla: '
         '<a href="/camisas-3xl-hombre" %s><strong>camisas 3XL</strong></a>, '
         '<a href="/camisas-4xl-hombre" %s><strong>camisas 4XL</strong></a> o '
         '<a href="/camisas-5xl-hombre" %s><strong>camisas 5XL</strong></a>. '
         'Pago contraentrega y envío gratis a toda Colombia.' % (MARCA, MARCA, MARCA))
    if v in h:
        if not DRY:
            io.open(f, "w", encoding="utf-8", newline="").write(h.replace(v, n))
        print("callout del blog de tallas: enlazado a 3XL/4XL/5XL")
    elif MARCA in h:
        print("callout del blog de tallas: ya estaba")
    else:
        raise SystemExit("!! no encuentro el callout del blog de tallas")
    print("\n%s" % ("(DRY-RUN)" if DRY else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
