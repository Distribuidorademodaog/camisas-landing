# -*- coding: utf-8 -*-
"""
Saca del indice las paginas de ciudad de mercado pequeno que Google ya rechaza.

Contexto (2026-08-14): la URL Inspection API dice que 12 de las 21 paginas de
ciudad NO estan indexadas, y las 9 que si lo estan son exactamente las 9 con
trafico. Se descartaron con medicion las tres causas sospechadas: duplicacion
(medellin 40,4% de solapamiento vs cali 44,9% que SI rankea), contenido delgado
(las no indexadas tienen MAS unico: 1.154 palabras de media vs 653) y enlazado
(medellin 79 entrantes). Lo que encaja es saturacion de indice: el sitio paso de
31 a 86 paginas en cinco semanas y Google indexo ~1 de cada 6 de las nuevas.

Que hace: en las ciudades de la lista pone <meta name="robots" content="noindex,
follow"> y las saca del sitemap. Se mantiene "follow" y se mantienen los enlaces
internos a proposito: siguen siendo utiles para el usuario y el link equity
sigue fluyendo hacia las paginas que si queremos indexar.

REVERSIBLE:  python noindex_ciudades_pequenas.py --revertir

Uso:  python noindex_ciudades_pequenas.py [--dry-run] [--revertir]
"""
import io
import re
import sys

# Ciudades de menor mercado, todas con 0 impresiones y rechazadas por Google.
# Para volver a intentar indexar alguna: quitarla de aqui y correr --revertir.
FUERA = [
    "neiva",       # Discovered - currently not indexed
    "pasto",       # Discovered - currently not indexed
    "armenia",     # Discovered - currently not indexed
    "popayan",     # URL is unknown to Google
    "valledupar",  # Crawled - currently not indexed (ultimo rastreo 2026-05-13)
    "monteria",    # Crawled - currently not indexed (ultimo rastreo 2026-05-13)
    "itagui",      # Discovered - currently not indexed
    "envigado",    # Discovered - currently not indexed
]

ROBOTS_IN = ("index, follow, max-snippet:-1, max-image-preview:large, "
             "max-video-preview:-1")
ROBOTS_OUT = "noindex, follow"
BASE = "https://www.camisascolombia.com"
SITEMAP = "sitemap.xml"


def set_robots(slug, valor, dry):
    p = "camisas-polo-%s.html" % slug
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
        url = "%s/camisas-polo-%s" % (BASE, slug)
        pat = r"\s*<url>\s*<loc>%s</loc>.*?</url>" % re.escape(url)
        s, n = re.subn(pat, "", s, count=1, flags=re.S)
        quitados += n
    if not dry:
        io.open(SITEMAP, "w", encoding="utf-8", newline="").write(s)
    return quitados


def sitemap_con(slugs, dry):
    """Reinserta las URLs antes de </urlset>, con prioridad de ciudad."""
    s = io.open(SITEMAP, encoding="utf-8").read()
    puestos = 0
    hoy = re.search(r"<lastmod>([^<]+)</lastmod>", s).group(1)
    for slug in slugs:
        url = "%s/camisas-polo-%s" % (BASE, slug)
        if url + "</loc>" in s:
            continue
        bloque = ("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
                  "    <changefreq>weekly</changefreq>\n"
                  "    <priority>0.8</priority>\n  </url>\n" % (url, hoy))
        s = s.replace("</urlset>", bloque + "</urlset>", 1)
        puestos += 1
    if not dry:
        io.open(SITEMAP, "w", encoding="utf-8", newline="").write(s)
    return puestos


def main():
    dry = "--dry-run" in sys.argv
    revertir = "--revertir" in sys.argv

    if revertir:
        n = sum(set_robots(c, ROBOTS_IN, dry) for c in FUERA)
        p = sitemap_con(FUERA, dry)
        print("REVERTIR: %d paginas vuelven a index,follow; %d reinsertadas en "
              "el sitemap" % (n, p))
    else:
        n = sum(set_robots(c, ROBOTS_OUT, dry) for c in FUERA)
        q = sitemap_sin(FUERA, dry)
        print("%d paginas a noindex,follow; %d URLs fuera del sitemap" % (n, q))
        for c in FUERA:
            print("   /camisas-polo-%s" % c)

    total = len(re.findall(r"<loc>", io.open(SITEMAP, encoding="utf-8").read()))
    print("\nsitemap: %d URLs%s" % (total, "  (DRY-RUN, no se escribio)" if dry else ""))


if __name__ == "__main__":
    main()
