# -*- coding: utf-8 -*-
"""
Lote 2 de ciudades: 8 paginas nuevas + modulo de ciudades 21 -> 29 — 2026-09-17.

Motivo (GSC 19 ago - 15 sep 2026): las paginas de ciudad son el activo que
mejor rinde del sitio — 75 clics con 2.656 impresiones (28 clics por cada
1.000, contra 6 del blog) — y las 8 reactivadas el 04-sep entraron al indice
en 4 dias y 6 de 8 ya tienen impresiones en posicion 3,5-9. Faltaban ciudades
de mas de 170.000 habitantes sin pagina: Bello, Palmira, Floridablanca,
Sincelejo, Buenaventura, Tunja, Dosquebradas y Riohacha.

Que hace:
  1. Escribe _cities/<slug>.meta.json y .section.html desde _cities/lote2_datos.py
     (sin testimonios inventados; sin «probar antes de pagar»).
  2. Construye las 8 paginas con build_cities_clone.build() clonando la de
     Cali viva (asi heredan TODO lo de hoy: parrafo de tallas, order bumps,
     pack de 5, hubs).
  3. Repasa los restos de «Cali» que el clonador no reescribe (areaServed,
     twitter, breadcrumb…) — se listan en la salida y se corrigen.
  4. Modulo `cities-footer-grid`: 21 -> 29 ciudades en todas las paginas que
     lo llevan (la propia como <strong>). Asi las 8 nuevas nacen con enlace
     desde el home y desde las otras ciudades, que es lo que les falto a las
     paginas de talla (ver enlazar_tallas_2026_09_17.py).
  5. Sitemap: +8 URLs.
  6. De paso: 8 ciudades reactivadas conservaban un testimonio «Probé, todo
     bien, pagué» — promesa de probar antes de pagar (regla del 05-sep). Se
     reescribe.

Uso:  python ciudades_lote2_2026_09_17.py [--dry-run]
"""
import glob
import html as htmlmod
import io
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cities"))
from lote2_datos import CIUDADES  # noqa: E402
import build_cities_clone as bcc  # noqa: E402

DRY = "--dry-run" in sys.argv
BASE = "https://www.camisascolombia.com"
HOY = time.strftime("%Y-%m-%d")

CIUDADES_NAV = [
    ("bogota", "Bogotá"), ("medellin", "Medellín"), ("cali", "Cali"),
    ("barranquilla", "Barranquilla"), ("cartagena", "Cartagena"),
    ("bucaramanga", "Bucaramanga"), ("cucuta", "Cúcuta"), ("pereira", "Pereira"),
    ("manizales", "Manizales"), ("ibague", "Ibagué"), ("santa-marta", "Santa Marta"),
    ("villavicencio", "Villavicencio"), ("soacha", "Soacha"), ("armenia", "Armenia"),
    ("popayan", "Popayán"), ("valledupar", "Valledupar"), ("monteria", "Montería"),
    ("neiva", "Neiva"), ("pasto", "Pasto"), ("envigado", "Envigado"),
    ("itagui", "Itagüí"),
    # lote 2
    ("bello", "Bello"), ("palmira", "Palmira"), ("floridablanca", "Floridablanca"),
    ("sincelejo", "Sincelejo"), ("buenaventura", "Buenaventura"), ("tunja", "Tunja"),
    ("dosquebradas", "Dosquebradas"), ("riohacha", "Riohacha"),
]
ES_CIUDAD = re.compile(r"^camisas-polo-(%s)\.html$" % "|".join(c for c, _ in CIUDADES_NAV))


def e(s):
    return htmlmod.escape(s, quote=True)


# ── 1. fuentes ──────────────────────────────────────────────────────────────
def seccion(c):
    n = c["nombre"]
    zonas = "".join(
        '        <div class="city-zone">\n'
        '          <strong>%s</strong> · <span class="city-zone-time">%s</span>\n'
        '          <p>%s</p>\n'
        '        </div>\n' % (z, t, d) for z, t, d in c["zonas"])
    faqs = "".join(
        '        <div class="city-faq">\n'
        '          <strong>%s</strong>\n'
        '          <p>%s</p>\n'
        '        </div>\n' % (q, a) for q, a in c["faqs"])
    ps = lambda lst: "".join("<p>%s</p>" % p for p in lst)
    return f'''  <div class="city-section">
    <div class="sec-head">
      <div class="sec-kicker">Envíos rápidos · {n}</div>
      <h2 class="sec-title">Camisas polo en <em>{n}</em> con entrega {c["plazo"]}</h2>
      <p class="sec-subtitle city-intro">{c["intro"]}</p>
    </div>

    <div class="city-block">
      <h3 class="city-block-title">🚚 Llegamos a tu zona en {n}</h3>
      <p>{c["barrios"]}</p>
      <small>Y a toda el área urbana y rural de {n}.</small>
    </div>

    <div class="city-block">
      <h3 class="city-block-title">👔 El estilo del hombre {c["gent"]} y la camisa polo</h3>
      {ps(c["estilo"])}
    </div>

    <div class="city-block">
      <h3 class="city-block-title">📍 Cobertura y tiempos de entrega por zona en {n}</h3>
      <p>Cubrimos toda la ciudad y sus alrededores con estos tiempos:</p>
      <div class="city-zones">
{zonas}      </div>
    </div>

    <div class="city-block">
      <h3 class="city-block-title">{c["emoji_clima"]} {c["clima_t"]}</h3>
      {ps(c["clima"])}
    </div>

    <div class="city-block">
      <h3 class="city-block-title">🏙️ {c["dia_t"]}</h3>
      {ps(c["dia"])}
      <small>{c["tip"]}</small>
    </div>

    <div class="city-block">
      <h3 class="city-block-title">🛍️ Centros comerciales y referentes de moda masculina en {n}</h3>
      {ps(c["malls"])}
    </div>

    <div class="city-block">
      <h3 class="city-block-title">📦 Preguntas frecuentes sobre envíos a {n}</h3>
      <div class="city-faqs">
{faqs}      </div>
    </div>

    <div class="city-cta-block">
      <p>{c["cta"]}</p>
    </div>
  </div>'''


def meta(c):
    return {
        "title": c["title"], "meta_description": c["meta"], "keywords": c["keywords"],
        "og_title": c["og_title"], "og_description": c["og_desc"],
        "placename": c["placename"], "lat": c["lat"], "lng": c["lng"],
        "faqs": [{"q": q, "a": a} for q, a in c["faqs"]],
    }


# ── 3. restos de la ciudad base que el clonador no toca ─────────────────────
def restos(h, c, template):
    """Lo que el clonador no reescribe (medido en el dry-run): la description de
    Cali copiada dentro del JSON-LD (WebPage y otro nodo), el nombre del
    breadcrumb y el comentario de seccion."""
    n = c["nombre"]
    desc_cali = re.search(r'<meta name="description" content="([^"]*)"', template).group(1)
    h = h.replace(desc_cali, c["meta"])
    h = h.replace("Camisas Polo en Cali", "Camisas Polo en %s" % n)
    h = h.replace("CIUDAD: Cali ", "CIUDAD: %s " % n)
    return h


def nav_ciudades(propia):
    filas = []
    for slug, nombre in CIUDADES_NAV:
        filas.append("<strong>%s</strong>" % nombre if slug == propia
                     else '<a href="/camisas-polo-%s">%s</a>' % (slug, nombre))
    return ('<nav class="cities-footer-grid" aria-label="Ciudades con entrega rápida">\n        '
            + "\n        ".join(filas) + "\n      </nav>")


def main():
    # La pagina de Cali viva ya no lleva el FAQPage por ciudad (desde el
    # de-branding es el FAQ generico del sitio, en una linea, igual en las 21
    # ciudades). Se conserva tal cual: el clonador no debe tocarlo.
    _sub1 = bcc.sub1

    def sub1_sin_faq(pattern, repl, s, flags=0, label=""):
        return s if label == "faqpage" else _sub1(pattern, repl, s, flags, label)
    bcc.sub1 = sub1_sin_faq
    template = bcc.BASE_PAGE.read_text(encoding="utf-8")
    assert len(CIUDADES) == 8
    for slug, c in CIUDADES.items():
        io.open("_cities/%s.meta.json" % slug, "w", encoding="utf-8", newline="").write(
            json.dumps(meta(c), ensure_ascii=False, indent=1))
        io.open("_cities/%s.section.html" % slug, "w", encoding="utf-8", newline="").write(seccion(c))
        h = bcc.build(slug, template)
        h = restos(h, c, template)
        # nada de la ciudad base puede sobrevivir fuera de la seccion
        cuerpo = re.sub(r'<div class="city-section">.*?<!-- ═══════ CARRUSEL ═══════ -->', "", h, flags=re.S)
        sobran = [m for m in re.findall(r"[^\w]Cali[^\wf][^<\"]{0,40}|cale[ñn][oa]s?|Valle del Cauca", cuerpo)]
        if sobran and c["depto"] != "Valle del Cauca":
            print("   !! restos en %s: %s" % (slug, sobran[:6]))
        assert "pack de 6" not in h and "495.000" not in h, slug
        for prohibido in ("prob", "revis", "abrir"):
            secc = seccion(c).lower()
            assert ("%sar antes de pagar" % prohibido) not in secc, (slug, prohibido)
        if not DRY:
            io.open("camisas-polo-%s.html" % slug, "w", encoding="utf-8", newline="").write(h)
            # mismo guardarrail que verificar_cambios.py (control 3): los nombres
            # de archivo del CDN (order-bumps/lacoste-*.webp) se exceptuan; la
            # pagina de Cali viva ya los lleva y bcc.verificar_marcas abortaria.
            limpio = re.sub(r"order-bumps/[a-z0-9-]+\.webp", "", h.lower()).replace("rené lacoste", "").replace("rene lacoste", "")
            marcas = sorted({m for m in bcc.MARCAS_PROHIBIDAS if m in limpio})
            assert not marcas, "marca ajena en %s: %s" % (slug, marcas)
        print("  OK camisas-polo-%-14s %7d bytes  %s (%d chars) " % (slug, len(h), c["title"], len(c["title"])))

    # 4. modulo de ciudades en todas las paginas
    pgs = sorted(set(p.replace(os.sep, "/") for p in glob.glob("*.html")) - {"404.html", "gracias.html"})
    n_mod = 0
    for f in pgs:
        if DRY and ES_CIUDAD.match(f) and ES_CIUDAD.match(f).group(1) in CIUDADES:
            continue  # en dry-run las nuevas no existen
        h = io.open(f, encoding="utf-8").read()
        m = re.search(r'<nav class="cities-footer-grid".*?</nav>', h, re.S)
        if not m:
            continue
        mm = ES_CIUDAD.match(f)
        nuevo = h[:m.start()] + nav_ciudades(mm.group(1) if mm else "") + h[m.end():]
        if nuevo != h:
            n_mod += 1
            if not DRY:
                io.open(f, "w", encoding="utf-8", newline="").write(nuevo)
    print("modulo de ciudades (29) reescrito en %d paginas" % n_mod)

    # 5. sitemap
    sm = io.open("sitemap.xml", encoding="utf-8").read()
    antes = sm.count("<url>")
    for slug in CIUDADES:
        loc = "%s/camisas-polo-%s" % (BASE, slug)
        if loc + "</loc>" in sm:
            continue
        sm = sm.replace("</urlset>", "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n</urlset>" % (loc, HOY))
    if not DRY:
        io.open("sitemap.xml", "w", encoding="utf-8", newline="").write(sm)
    print("sitemap %d -> %d URLs" % (antes, sm.count("<url>")))

    # 6. testimonio con promesa de probar antes de pagar
    # 8 variantes: «llegaron.» / «llegaron a <barrio>.» y «Nequi» / «transferencia Nequi»
    PAT = re.compile(r"llegaron( a [^.]+)?\. Probé, todo bien, pagué con (transferencia )?Nequi al mismo repartidor\.")
    REP = lambda m: "llegaron%s y pagué con %sNequi al mismo repartidor. Todo bien." % (m.group(1) or "", m.group(2) or "")
    n_t = 0
    for f in pgs:
        h = io.open(f, encoding="utf-8").read()
        nuevo, k = PAT.subn(REP, h)
        if k:
            n_t += 1
            if not DRY:
                io.open(f, "w", encoding="utf-8", newline="").write(nuevo)
    print("testimonio «Probé, todo bien, pagué» reescrito en %d paginas" % n_t)
    print("\n%s" % ("(DRY-RUN: fuentes escritas, HTML no)" if DRY else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
