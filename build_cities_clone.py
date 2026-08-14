"""
Genera paginas de ciudad para camisascolombia.com clonando una pagina de ciudad
VIVA (camisas-polo-cali.html) como base — garantiza calcar la estructura en produccion
(el viejo build_cities.py apunta a un template obsoleto en Downloads/ y escribe en output/).

Para cada slug lee:
  _cities/<slug>.meta.json     -> title, meta_description, keywords, og_title, og_description,
                                  placename ("Ciudad, Depto, Colombia"), lat, lng, faqs[]
  _cities/<slug>.section.html  -> bloque <div class="city-section"> ... </div> unico (contenido local)

Reescribe por regex (agnostico a la ciudad base): title, meta desc/keywords, canonical, og:url,
og:title, og:description, geo placename/position/ICBM, FAQPage (regenerada desde faqs) y la
seccion local. NO toca hero (generico), header, catalogo, packs, footer ni demas schemas.

Salida: camisas-polo-<slug>.html en la raiz. Uso: python build_cities_clone.py [slug1 ...]
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
BASE_PAGE = ROOT / "camisas-polo-cali.html"
SPECS = ROOT / "_cities"
BASE = "https://www.camisascolombia.com"


def strip_tags(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def sub1(pattern, repl, s, flags=0, label=""):
    new, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    if n == 0:
        raise RuntimeError(f"[{label}] patron no encontrado")
    return new


def build_faqpage(faqs):
    items = []
    for f in faqs:
        text = strip_tags(f["a"]).replace('"', "'")
        q = f["q"].replace('"', "'")
        items.append(
            '    {\n      "@type":"Question",\n      "name":"' + q + '",\n'
            '      "acceptedAnswer":{\n        "@type":"Answer",\n        "text":"' + text + '"\n      }\n    }'
        )
    return '"@type":"FAQPage",\n  "mainEntity":[\n' + ",\n".join(items) + "\n  ]"


def build(slug, template):
    meta = json.loads((SPECS / f"{slug}.meta.json").read_text(encoding="utf-8"))
    section = (SPECS / f"{slug}.section.html").read_text(encoding="utf-8").rstrip()
    canonical = f"{BASE}/camisas-polo-{slug}"
    out = template

    # 1. seccion local (de <div class="city-section"> hasta el marcador CARRUSEL, que va sin indentar)
    car = "<!-- ═══════ CARRUSEL ═══════ -->"
    out = sub1(r'  <div class="city-section">.*?<!-- ═══════ CARRUSEL ═══════ -->',
               section + "\n\n" + car, out, flags=re.DOTALL, label="city-section")

    # 2. head por regex de atributo
    out = sub1(r'<title>.*?</title>', f'<title>{meta["title"]}</title>', out, re.DOTALL, "title")
    out = sub1(r'<meta name="description" content="[^"]*">',
               f'<meta name="description" content="{meta["meta_description"]}">', out, 0, "desc")
    out = sub1(r'<meta name="keywords" content="[^"]*">',
               f'<meta name="keywords" content="{meta["keywords"]}">', out, 0, "kw")
    out = sub1(r'<meta name="geo.placename" content="[^"]*">',
               f'<meta name="geo.placename" content="{meta["placename"]}">', out, 0, "placename")
    out = sub1(r'<meta name="geo.position" content="[^"]*">',
               f'<meta name="geo.position" content="{meta["lat"]};{meta["lng"]}">', out, 0, "geopos")
    out = sub1(r'<meta name="ICBM" content="[^"]*">',
               f'<meta name="ICBM" content="{meta["lat"]}, {meta["lng"]}">', out, 0, "icbm")
    out = sub1(r'<link rel="canonical" href="[^"]*">',
               f'<link rel="canonical" href="{canonical}">', out, 0, "canonical")
    out = sub1(r'<meta property="og:url" content="[^"]*">',
               f'<meta property="og:url" content="{canonical}">', out, 0, "og:url")
    out = sub1(r'<meta property="og:title" content="[^"]*">',
               f'<meta property="og:title" content="{meta["og_title"]}">', out, 0, "og:title")
    out = sub1(r'<meta property="og:description" content="[^"]*">',
               f'<meta property="og:description" content="{meta["og_description"]}">', out, 0, "og:desc")

    # 3. FAQPage regen (formato 2-espacios del city page)
    out = sub1(r'"@type":"FAQPage",\n  "mainEntity":\[.*?\n  \]',
               build_faqpage(meta["faqs"]), out, re.DOTALL, "faqpage")

    # sanity
    assert canonical + '"' in out, "canonical mal"
    assert 'id="carruselTrack"' in out and 'perShirtGrid' in out, "shell roto"
    assert f'<div class="city-section">' in out, "city-section ausente"
    return out


def main():
    template = BASE_PAGE.read_text(encoding="utf-8")
    slugs = sys.argv[1:] or sorted(p.stem[:-5] for p in SPECS.glob("*.meta.json"))
    for slug in slugs:
        html = build(slug, template)
        (ROOT / f"camisas-polo-{slug}.html").write_text(html, encoding="utf-8")
        print(f"  OK camisas-polo-{slug:22} {len(html):>7,} bytes")
    print(f"\n[OK] {len(slugs)} ciudad(es)")


if __name__ == "__main__":
    main()


# ─────────────────────────────────────────────────────────────
# Guardarrail de marcas ajenas (añadido por la auditoria SEO 2026-08).
# Usar una marca de terceros en title/description/alt es lo que revisa
# Google Merchant Center bajo su politica de marcas, y es reportable por
# el titular ante Meta Ads. Si el build vuelve a introducirla, aborta.
# ─────────────────────────────────────────────────────────────
MARCAS_PROHIBIDAS = [
    "ralph lauren", "polo rl", "lacoste", "tommy hilfiger",
    "hugo boss", "calvin klein", "nautica",
]


def verificar_marcas(ruta_salida):
    """Aborta el build si el HTML generado contiene una marca ajena."""
    with open(ruta_salida, encoding="utf-8", errors="replace") as fh:
        contenido = fh.read().lower()
    encontradas = sorted({m for m in MARCAS_PROHIBIDAS if m in contenido})
    if encontradas:
        raise SystemExit(
            "BUILD ABORTADO: marca ajena en %s -> %s" % (ruta_salida, encontradas))
