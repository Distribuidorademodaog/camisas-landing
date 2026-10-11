# -*- coding: utf-8 -*-
"""
Paso 5 · Poda del blog para liberar presupuesto de rastreo — 2026-10-11.

El cuello medido del sitio es el rastreo: mediana de 21 dias desde el ultimo
rastreo, p90 de 58, y 20 paginas que Google no ha abierto nunca. Mientras eso
siga asi, cualquier cambio tarda uno o dos meses en existir para Google.

El blog es 24 paginas de 102 y consume ese presupuesto para devolver muy poco.
Medido sobre 90 dias (10-jul a 8-oct), con filtro por pagina de verdad:

    blog     24 pags   20.997 impresiones   117 clics   ->  5,6 clics/1.000
    ciudad   29 pags    6.733 impresiones   188 clics   -> 27,9 clics/1.000
    tallas    6 pags    1.707 impresiones    38 clics   -> 22,3 clics/1.000
    home      1 pag       623 impresiones    30 clics   -> 48,2 clics/1.000

Se sacan del indice las CUATRO que no devuelven nada y ademas son de POLO, que es
justo lo que estamos dejando de empujar (el negocio vende oxford y tipo lino):

    /blog/polo-vs-camisa-cuello-botones        1.136 impr   1 clic
    /blog/historia-origen-camisa-polo            976 impr   1 clic
    /blog/camisas-premium-vs-marca-costosa       148 impr   0 clics
    /blog/cuantas-camisas-polo-debe-tener-un-hombre 40 impr  0 clics
    ----------------------------------------------------------------
                                               2.300 impr   2 clics en 90 dias

`polo-vs-camisa-cuello-botones` es el caso de libro: esta en posicion 1,0 para
«que es una camisa polo» y saca CERO clics, porque Google responde la definicion
el mismo. Mas palabras no lo arreglan.

NO se tocan, a proposito:
  - `/blog` (el indice): 0 clics, pero es el hub que reparte enlaces internos.
  - `/blog/pago-contraentrega-seguro` (434 impr, 1 clic): «pago contra entrega»
    son 1.900 busquedas/mes y es la propuesta de valor del negocio. Poco clic,
    pero alineado con lo que se vende.
  - Las 4 que si rinden: algodon-pique-vs-liso (33 clics), tallas-grandes (26),
    como-elegir-talla (11), tendencias-2026 (8).

Las 7 URLs de blog con erratas que Google todavia conoce
(`/blog/algodon-pique-liso`, `/blog/como-como-combinar-camisa-polo`...) ya
devuelven 404 y no estan en el sitemap: no hay nada que hacer, caen solas.

Metodo: `noindex, follow` + fuera del sitemap. Se mantiene `follow` y se mantienen
los enlaces entrantes, asi que el enlazado interno no se rompe y la autoridad
sigue fluyendo. Es reversible.

REVERSIBLE:  python podar_blog_2026_10_11.py --revertir

Uso:  python podar_blog_2026_10_11.py [--dry-run] [--revertir]
"""
import io
import os
import re
import sys

BASE = "https://www.camisascolombia.com"
SITEMAP = "sitemap.xml"

# (slug, impresiones 90d, clics 90d) — el comentario es la razon
FUERA = [
    ("polo-vs-camisa-cuello-botones",         1136, 1),  # pos 1,0 en «que es una camisa polo», 0 clics
    ("historia-origen-camisa-polo",            976, 1),  # historia del polo: cero intencion comercial
    ("camisas-premium-vs-marca-costosa",       148, 0),  # 0 clics en 90 dias
    ("cuantas-camisas-polo-debe-tener-un-hombre", 40, 0),  # 0 clics en 90 dias
]

ROBOTS_IN = ("index, follow, max-snippet:-1, max-image-preview:large, "
             "max-video-preview:-1")
ROBOTS_OUT = "noindex, follow"


def ruta(slug):
    return os.path.join("blog", slug + ".html")


def set_robots(slug, valor, dry):
    p = ruta(slug)
    if not os.path.exists(p):
        raise SystemExit("!! no existe %s" % p)
    s = io.open(p, encoding="utf-8").read()
    nuevo, n = re.subn(r'(<meta name="robots" content=")[^"]*(">)',
                       lambda m: m.group(1) + valor + m.group(2), s, count=1)
    if n != 1:
        raise SystemExit("!! no se encontro meta robots en %s" % p)
    if nuevo != s and not dry:
        io.open(p, "w", encoding="utf-8", newline="").write(nuevo)
    return nuevo != s


def sitemap_sin(slugs, dry):
    s = io.open(SITEMAP, encoding="utf-8").read()
    quitados = 0
    for slug in slugs:
        url = "%s/blog/%s" % (BASE, slug)
        pat = r"\s*<url>\s*<loc>%s</loc>.*?</url>" % re.escape(url)
        s, n = re.subn(pat, "", s, count=1, flags=re.S)
        quitados += n
    if not dry:
        io.open(SITEMAP, "w", encoding="utf-8", newline="").write(s)
    return quitados


def sitemap_con(slugs, dry):
    s = io.open(SITEMAP, encoding="utf-8").read()
    puestos = 0
    hoy = re.search(r"<lastmod>([^<]+)</lastmod>", s).group(1)
    for slug in slugs:
        url = "%s/blog/%s" % (BASE, slug)
        if url + "</loc>" in s:
            continue
        bloque = ("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
                  "    <changefreq>monthly</changefreq>\n"
                  "    <priority>0.6</priority>\n  </url>\n" % (url, hoy))
        s = s.replace("</urlset>", bloque + "</urlset>", 1)
        puestos += 1
    if not dry:
        io.open(SITEMAP, "w", encoding="utf-8", newline="").write(s)
    return puestos


def main():
    dry = "--dry-run" in sys.argv
    revertir = "--revertir" in sys.argv
    slugs = [f[0] for f in FUERA]

    if revertir:
        n = sum(set_robots(s, ROBOTS_IN, dry) for s in slugs)
        p = sitemap_con(slugs, dry)
        print("REVERTIR: %d paginas vuelven a index,follow; %d reinsertadas en el sitemap" % (n, p))
    else:
        n = sum(set_robots(s, ROBOTS_OUT, dry) for s in slugs)
        q = sitemap_sin(slugs, dry)
        print("%d paginas a noindex,follow; %d URLs fuera del sitemap\n" % (n, q))
        ti = sum(f[1] for f in FUERA); tc = sum(f[2] for f in FUERA)
        for slug, i, c in FUERA:
            print("   /blog/%-44s %5d impr  %d clics" % (slug, i, c))
        print("   %-47s %5d impr  %d clics en 90 dias" % ("TOTAL", ti, tc))

    sm = io.open(SITEMAP, encoding="utf-8").read()
    total = len(re.findall(r"<loc>", sm))
    blogs = len(re.findall(r"<loc>%s/blog/" % re.escape(BASE), sm))
    print("\nsitemap: %d <loc> en total, %d de blog%s"
          % (total, blogs, "   (DRY-RUN, no se escribio)" if dry else ""))

    # el control 8 de verificar_cambios exige coherencia noindex <-> sitemap
    print("\ncoherencia noindex <-> sitemap:")
    mal = 0
    for slug in slugs:
        p = ruta(slug)
        h = io.open(p, encoding="utf-8").read()
        m = re.search(r'<meta name="robots" content="([^"]*)"', h)
        ni = bool(m) and "noindex" in m.group(1)
        en = ("%s/blog/%s</loc>" % (BASE, slug)) in sm
        if ni == en:   # noindex y en sitemap, o indexable y fuera: incoherente
            print("   INCOHERENTE  %s  noindex=%s en_sitemap=%s" % (slug, ni, en))
            mal += 1
    print("   %s" % ("%d incoherencias" % mal if mal else "OK"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
