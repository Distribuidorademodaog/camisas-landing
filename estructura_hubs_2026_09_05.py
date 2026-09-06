# -*- coding: utf-8 -*-
"""
Reequilibra el enlazado interno hacia lo comercial — 2026-09-05.

Medicion previa (grafo de las 89 paginas, 3.689 enlaces internos, cruzado con
GSC 6-ago/2-sep):

  - Las 8 ciudades reactivadas esa manana quedaron HUERFANAS: 0 enlaces
    entrantes, inalcanzables desde el home. El modulo de ciudades solo lista 10
    de las 21 que existen.
  - Las 10 paginas con mas enlaces contextuales del sitio son las 10 del blog.
    /blog recibe 168; cuatro articulos reciben ~70-79 cada uno y tienen CERO
    impresiones. Mientras /camibusos-hombre (1.071 impresiones, el mayor activo
    del mes) recibe 3 y la pilar 34.
  - El cuerpo del home enlaza a 21 articulos del blog y a UNA sola pagina
    comercial.
  - Los hubs de color y de tallas ya existen y ya enlazan hacia abajo; lo que
    falta es que reciban (el home no los enlaza) y que las ciudades enlacen
    hacia arriba (20 de 21 no lo hacen).

Tres cambios:

 1. CIUDADES 10 -> 21 en el modulo `cities-footer-grid` de las 65 paginas que
    lo llevan. Cada pagina de ciudad se muestra a si misma como <strong>, no
    como enlace (un autoenlace no aporta nada).
 2. BLOG-GRID de 20 tarjetas a 4 en las paginas comerciales. Se conservan los
    cuatro articulos que SI rinden segun GSC (algodon-pique-vs-liso 13 clics,
    tallas-grandes 11, tendencias-2026 CTR 1,47%, colores-segun-tono 2,26%).
    Los otros 16 x 65 paginas eran ~1.000 enlaces hacia articulos que no
    rankean. Los blogs entre si NO se tocan: llevan `related-block`, no este.
 3. HUBS. Los tres cabezas de cluster se enlazan desde el `cc-relacionados` de
    todas las paginas que lo llevan, y las ciudades reciben un enlace
    contextual en prosa hacia la pilar.
       colores  -> /camisas-polo-colores-hombre    (10 hijos)
       tallas   -> /camisas-hombre-tallas-grandes  (5 hijos)
       ciudades -> /camisas-polo-premium-colombia  (21 hijos; la pilar hace de
                   cabeza, no se crea una pagina nueva a proposito: el sitio ya
                   demostro que sumar paginas que no rankean solo diluye)

Uso:  python estructura_hubs_2026_09_05.py [--dry-run]
"""
import glob
import io
import os
import re
import sys

CIUDADES = [
    ("bogota", "Bogotá"), ("medellin", "Medellín"), ("cali", "Cali"),
    ("barranquilla", "Barranquilla"), ("cartagena", "Cartagena"),
    ("bucaramanga", "Bucaramanga"), ("cucuta", "Cúcuta"), ("pereira", "Pereira"),
    ("manizales", "Manizales"), ("ibague", "Ibagué"), ("santa-marta", "Santa Marta"),
    ("villavicencio", "Villavicencio"), ("soacha", "Soacha"), ("armenia", "Armenia"),
    ("popayan", "Popayán"), ("valledupar", "Valledupar"), ("monteria", "Montería"),
    ("neiva", "Neiva"), ("pasto", "Pasto"), ("envigado", "Envigado"),
    ("itagui", "Itagüí"),
]

# Los 4 articulos que sí traen clics (GSC 6-ago/2-sep).
BLOGS_QUE_RINDEN = [
    "/blog/algodon-pique-vs-liso",
    "/blog/tallas-grandes-3xl-4xl-5xl",
    "/blog/tendencias-2026-camisas-polo-colombia",
    "/blog/colores-camisa-polo-segun-tono-de-piel",
]

HUBS = [
    ("/camisas-polo-colores-hombre", "Todos los colores"),
    ("/camisas-hombre-tallas-grandes", "Tallas 3XL, 4XL y 5XL"),
    ("/camisas-polo-premium-colombia", "Camisas polo para hombre"),
]

PILAR = "/camisas-polo-premium-colombia"
MARCA = 'data-link="hub-2026-09"'
ES_CIUDAD = re.compile(r"^camisas-polo-(%s)\.html$" % "|".join(c for c, _ in CIUDADES))


def paginas():
    return sorted(set(p.replace(os.sep, "/") for p in
                  glob.glob("*.html") + glob.glob("blog/*.html")
                  + glob.glob("guias/*.html")) - {"404.html", "gracias.html"})


# ── 1. modulo de ciudades ───────────────────────────────────────────────────
def nav_ciudades(propia):
    filas = []
    for slug, nombre in CIUDADES:
        if slug == propia:
            filas.append("<strong>%s</strong>" % nombre)
        else:
            filas.append('<a href="/camisas-polo-%s">%s</a>' % (slug, nombre))
    return ('<nav class="cities-footer-grid" aria-label="Ciudades con entrega rápida">\n        '
            + "\n        ".join(filas) + "\n      </nav>")


def ciudades(f, h):
    m = re.search(r'<nav class="cities-footer-grid".*?</nav>', h, re.S)
    if not m:
        return h, 0
    propia = ""
    mm = ES_CIUDAD.match(os.path.basename(f))
    if mm:
        propia = mm.group(1)
    h = h[:m.start()] + nav_ciudades(propia) + h[m.end():]
    h = h.replace(
        "Estas son nuestras 10 ciudades principales, pero <strong>despachamos a cualquier rincón de Colombia</strong> con pago contraentrega:",
        "Estas son las ciudades donde entregamos más rápido, pero <strong>despachamos a cualquier rincón de Colombia</strong> con pago contraentrega:")
    return h, 1


# ── 2. recortar el blog-grid en paginas comerciales ─────────────────────────
def blog_grid(h):
    m = re.search(r'<div class="blog-grid">(.*?)</div>\s*</div>', h, re.S)
    if not m:
        return h, 0
    bloque = m.group(1)
    tarjetas = re.findall(r'<a class="blogcard".*?</a>', bloque, re.S)
    if len(tarjetas) <= len(BLOGS_QUE_RINDEN):
        return h, 0
    quedan = [t for t in tarjetas
              if any(('href="%s"' % u) in t for u in BLOGS_QUE_RINDEN)]
    if not quedan:
        return h, 0
    nuevo = "\n          " + "\n          ".join(quedan) + "\n        "
    return h[:m.start(1)] + nuevo + h[m.end(1):], len(tarjetas) - len(quedan)


# ── 3. hubs en el cc-relacionados ───────────────────────────────────────────
def hubs_en_relacionados(f, h):
    m = re.search(r'(<nav class="cc-relacionados"[^>]*>\s*<h3>[^<]*</h3>\s*<ul>)', h, re.S)
    if not m:
        return h, 0
    propia = "/" + os.path.basename(f)[:-5]
    items = "".join('\n    <li><a href="%s" %s>%s</a></li>' % (u, MARCA, t)
                    for u, t in HUBS if u != propia and ('%s" %s' % (u, MARCA)) not in h)
    if not items:
        return h, 0
    return h[:m.end(1)] + items + h[m.end(1):], items.count("<li>")


def dentro_de_enlace(cuerpo, pos):
    return any(a.start() <= pos < a.end()
               for a in re.finditer(r"<a\b.*?</a>", cuerpo, re.S))


def enlace_contextual(h, destino, patrones):
    """Envuelve la primera mencion apta en prosa. Una sola por pagina."""
    if ('href="%s"' % destino) in h:
        return h, None
    for pat in patrones:
        for pm in re.finditer(r"<p[^>]*>(.*?)</p>", h, re.S):
            cuerpo = pm.group(1)
            if "${" in cuerpo:
                continue
            for mm in pat.finditer(cuerpo):
                if dentro_de_enlace(cuerpo, mm.start()):
                    continue
                nuevo = (cuerpo[:mm.start()]
                         + '<a href="%s" %s>%s</a>' % (destino, MARCA, mm.group(0))
                         + cuerpo[mm.end():])
                a, b = pm.span(1)
                return h[:a] + nuevo + h[b:], mm.group(0)
    return h, None


PAT_POLO = [re.compile(r"camisas polo para hombre", re.I),
            re.compile(r"camisas polo", re.I),
            re.compile(r"camisa polo", re.I)]
PAT_COLOR = [re.compile(r"colores de camisa polo", re.I),
             re.compile(r"m[aá]s de 20 colores", re.I),
             re.compile(r"\+20 colores", re.I),
             re.compile(r"colores", re.I)]


def main():
    dry = "--dry-run" in sys.argv
    n_ciu = n_blog = n_hub = n_ctx = 0
    tocados = set()
    for f in paginas():
        h = io.open(f, encoding="utf-8").read()
        orig = h
        es_blog = f.startswith("blog/")

        h, k = ciudades(f, h)
        n_ciu += k
        if not es_blog:
            h, k = blog_grid(h)
            n_blog += k

        # El enlace en PROSA va antes que el del nav: si el hub ya figura en
        # cc-relacionados, enlace_contextual se salta la pagina, y un enlace
        # contextual es mejor señal que un item de navegacion.
        if ES_CIUDAD.match(os.path.basename(f)):
            h, anc = enlace_contextual(h, PILAR, PAT_POLO)
            if anc:
                n_ctx += 1
        # la unica pagina de color que no enlazaba a su hub
        if os.path.basename(f) == "camisas-polo-blancas-hombre.html":
            h, anc = enlace_contextual(h, "/camisas-polo-colores-hombre", PAT_COLOR)
            if anc:
                n_ctx += 1

        h, k = hubs_en_relacionados(f, h)
        n_hub += k

        if h != orig:
            tocados.add(f)
            if not dry:
                io.open(f, "w", encoding="utf-8", newline="").write(h)

    print("paginas tocadas          : %d" % len(tocados))
    print("modulo de ciudades 10->21: %d paginas" % n_ciu)
    print("tarjetas de blog quitadas: %d" % n_blog)
    print("enlaces a hubs anadidos  : %d" % n_hub)
    print("enlaces contextuales     : %d" % n_ctx)
    print("\n%s" % ("(DRY-RUN, no se escribio)" if dry else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
