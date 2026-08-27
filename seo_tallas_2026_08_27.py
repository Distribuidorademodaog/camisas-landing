# -*- coding: utf-8 -*-
"""
Cluster de tallas grandes: resolver canibalizacion, no crear paginas — 2026-08-27.

Diagnostico (GSC 28 abr - 25 ago 2026):
  El cluster de tallas ya da señal real: 191 impresiones, posiciones 3-12.
  "5xl" esta en posicion 6,9 y "talla 4xl hombre" en 3,0.

  PERO ya hay DOS paginas propias peleando las mismas consultas:

      "5xl"        -> /camisas-hombre-tallas-grandes  pos 6,9
                      /blog/tallas-grandes-3xl-4xl-5xl pos 4,5
      "camisa 5xl" -> /camisas-hombre-tallas-grandes  pos 5,1
                      /blog/tallas-grandes-3xl-4xl-5xl pos 5,5

  Por eso NO se crean /camisas-polo-4xl-hombre ni /camisas-polo-5xl-hombre:
  serian una tercera pagina compitiendo por lo mismo, justo el problema que
  este lote de cambios viene a corregir. Ademas contradiria la decision del
  proyecto del 7 de agosto ("atacar posicion, no cobertura").

Reparto de intencion:
  * comercial ("camisa 5xl", "5xl", "polo hombre 3xl") -> pagina de catalogo
  * informacional ("que talla es 3xl en colombia")     -> el blog

Que hace:
  1. Reescribe el title/description del catalogo hacia la consulta comercial,
     usando el diferenciador que el corpus de 1.954 resenas demostro que pesa:
     medidas reales en centimetros (el 48,5% de las resenas de 1-2 estrellas
     del sector son por talla).
  2. Enlaza el articulo de tallas grandes hacia el catalogo con ancla exacta,
     para que la pagina comercial gane las consultas de compra.
     (En /blog/como-elegir-talla-camisa-polo no se enlaza: la unica mencion
     apta caia dentro de la enumeracion "(S, M, L, XL, XXL, 3XL, 4XL y 5XL)"
     y un ancla de dos caracteres ahi no aporta señal ni al usuario ni a
     Google.)

Uso:  python seo_tallas_2026_08_27.py [--dry-run]
"""
import io
import re
import sys

CATALOGO = "/camisas-hombre-tallas-grandes"
MARCA = 'data-link="tallas-2026-08"'

TITLE = "Camisas 3XL, 4XL y 5XL para Hombre | Medidas Reales en cm"
DESC = ("Camisas polo en tallas 3XL, 4XL y 5XL con la medida real de pecho y "
        "largo en centímetros, para que no falles la talla. Pago contraentrega "
        "y envío gratis.")

# blog -> patron de la mencion que se convierte en enlace
BLOGS = {
    "blog/tallas-grandes-3xl-4xl-5xl.html":
        re.compile(r"camisas? (?:polo )?(?:en )?tallas? grandes", re.I),
}


def set_meta(h, title, desc):
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, h,
               count=1, flags=re.S)
    for attr, val in (('name="description"', desc),
                      ('property="og:title"', title),
                      ('property="og:description"', desc),
                      ('name="twitter:title"', title),
                      ('name="twitter:description"', desc)):
        h = re.sub(r'(<meta\s+%s\s+content=")[^"]*(")' % attr,
                   lambda m: m.group(1) + val + m.group(2), h, count=1)
    return h


def enlazar(html, destino, pat):
    if MARCA in html:
        return html, None
    for pm in re.finditer(r"<p[^>]*>(.*?)</p>", html, re.S):
        cuerpo = pm.group(1)
        if "<a" in cuerpo or "${" in cuerpo:
            continue
        m = pat.search(cuerpo)
        if not m:
            continue
        ancla = m.group(0)
        nuevo = (cuerpo[:m.start()]
                 + '<a href="%s" %s>%s</a>' % (destino, MARCA, ancla)
                 + cuerpo[m.end():])
        ini, fin = pm.span(1)
        return html[:ini] + nuevo + html[fin:], ancla
    return html, None


def main():
    dry = "--dry-run" in sys.argv

    # 1. catalogo
    p = "camisas-hombre-tallas-grandes.html"
    h = io.open(p, encoding="utf-8").read()
    antes = re.search(r"<title>(.*?)</title>", h, re.S)
    antes = " ".join(antes.group(1).split()) if antes else ""
    nuevo = set_meta(h, TITLE, DESC)
    if not dry:
        io.open(p, "w", encoding="utf-8", newline="").write(nuevo)
    print("%s" % p)
    print("   antes (%2d): %s" % (len(antes), antes))
    print("   ahora (%2d): %s" % (len(TITLE), TITLE))
    print("   desc  (%2d)%s" % (len(DESC), "  !! LARGA" if len(DESC) > 160 else ""))
    print()

    # 2. blogs -> catalogo
    for path, pat in BLOGS.items():
        s = io.open(path, encoding="utf-8").read()
        n, ancla = enlazar(s, CATALOGO, pat)
        if ancla is None:
            print("%-44s sin mencion apta" % path)
            continue
        assert n.count("<a") == s.count("<a") + 1
        if not dry:
            io.open(path, "w", encoding="utf-8", newline="").write(n)
        print('%-44s ancla: "%s"' % (path, ancla))

    if dry:
        print("\n(simulacion)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
