"""
Genera landings comerciales para camisascolombia.com clonando la pilar
Ralph Lauren (camisas-polo-ralph-lauren-colombia.html) como template.

Para cada slug lee:
  _landings/<slug>.meta.json     -> campos SEO (title, desc, keywords, hero, schemas, faqs)
  _landings/<slug>.section.html  -> bloque <section class="sec sec-light" id="<slug>"> unico

Reescribe: <title>, meta description/keywords, OG, Twitter, hero (eyebrow + H1),
WebPage schema (name/desc + @id/url via slug global), ambos BreadcrumbList (leaf name),
FAQPage (regenerada desde faqs) y la seccion unica. Mantiene intactos header,
catalogo, packs, checkout, footer y demas schemas (Product/ItemList/HowTo).

Salida: <slug>.html en la raiz del repo. Uso: python build_landings.py [slug1 slug2 ...]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "camisas-polo-premium-colombia.html"
SPECS = ROOT / "_landings"
BASE = "https://www.camisascolombia.com"
RL_SLUG = "camisas-polo-premium-colombia"

# ---- strings EXACTAS del template RL que reemplazamos (assert si no aparecen) ----
RL_TITLE = "Camisas Polo para Hombre en Colombia | Polos Estilo Premium"
RL_OG_TITLE = "Camisas Polo para Hombre en Colombia | Polos Estilo Premium"
RL_TW_TITLE = "Camisas Polo para Hombre en Colombia | Polos Premium"
# 2026-09-04: el JSON-LD de la pilar se reformateo (espacio tras los dos puntos)
# y la auditoria dejo UN solo BreadcrumbList, no dos. Las constantes compactas
# y RL_BC1 ya no casaban: el build llevaba semanas abortando en [wp:name].
RL_WEBPAGE_NAME = '"name": "Camisas Polo para Hombre en Colombia | Polos Estilo Premium"'
RL_WEBPAGE_DESC = '"description": "Tienda online colombiana de camisas polo para hombre: algodón piqué, tallas S a 5XL, +20 colores, pago contraentrega y envío gratis."'
RL_BC = '"name": "Camisas Polo para Hombre en Colombia", "item"'  # hoja del unico BreadcrumbList
MODULO_REL = re.compile(r'\n<style>\n\.cc-relacionados\{.*?</nav>\n(?=</body>)', re.S)


def strip_tags(html: str) -> str:
    txt = re.sub(r"<[^>]+>", "", html)
    return re.sub(r"\s+", " ", txt).strip()


def sub1(pattern, repl, s, flags=0, label=""):
    new, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    if n == 0:
        raise RuntimeError(f"[{label}] patron no encontrado: {pattern[:80]}")
    return new


def replace_exact(old, new, s, label=""):
    if old not in s:
        raise RuntimeError(f"[{label}] string exacto no encontrado: {old[:80]}")
    return s.replace(old, new, 1)


def fin_corchete(s, i):
    """i apunta a '['; devuelve el indice del ']' que lo cierra (respeta strings)."""
    prof = 0
    en_str = False
    esc = False
    while i < len(s):
        c = s[i]
        if en_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                en_str = False
        else:
            if c == '"':
                en_str = True
            elif c == "[":
                prof += 1
            elif c == "]":
                prof -= 1
                if prof == 0:
                    return i
        i += 1
    raise RuntimeError("corchete sin cerrar en el bloque FAQPage")


def build_faqpage(faqs):
    entities = []
    for f in faqs:
        text = strip_tags(f["a"])
        entities.append({
            "@type": "Question",
            "name": f["q"],
            "acceptedAnswer": {"@type": "Answer", "text": text},
        })
    # Mismo formato que el JSON-LD ya desplegado: una sola linea, ", " y ": ".
    # Reproducirlo exacto es lo que permite comprobar el build con `git diff`.
    return json.dumps(entities, ensure_ascii=False, separators=(", ", ": "))


def build(slug, template):
    meta = json.loads((SPECS / f"{slug}.meta.json").read_text(encoding="utf-8"))
    section = (SPECS / f"{slug}.section.html").read_text(encoding="utf-8").rstrip()
    canonical = f"{BASE}/{slug}"
    out = template

    # 1. Seccion unica (desde el <section id RL> hasta el marcador CARRUSEL)
    carrusel = "  <!-- ═══════ CARRUSEL ═══════ -->"
    out = sub1(
        r'  <section class="sec sec-light" id="camisas-polo-premium">.*?  <!-- ═══════ CARRUSEL ═══════ -->',
        section + "\n\n" + carrusel,
        out, flags=re.DOTALL, label="section",
    )

    # 2. <title>
    out = replace_exact(f"<title>{RL_TITLE}</title>", f"<title>{meta['title']}</title>", out, "title")

    # 3. meta description
    out = sub1(r'<meta name="description" content="[^"]*">',
               f'<meta name="description" content="{meta["meta_description"]}">', out, label="desc")

    # 4. meta keywords
    out = sub1(r'<meta name="keywords" content="[^"]*">',
               f'<meta name="keywords" content="{meta["keywords"]}">', out, label="keywords")

    # 5. OG title / description
    out = replace_exact(f'<meta property="og:title" content="{RL_OG_TITLE}">',
                        f'<meta property="og:title" content="{meta["og_title"]}">', out, "og:title")
    out = sub1(r'<meta property="og:description" content="[^"]*">',
               f'<meta property="og:description" content="{meta["og_description"]}">', out, label="og:desc")

    # 6. Twitter title / description
    out = replace_exact(f'<meta name="twitter:title" content="{RL_TW_TITLE}">',
                        f'<meta name="twitter:title" content="{meta["twitter_title"]}">', out, "tw:title")
    out = sub1(r'<meta name="twitter:description" content="[^"]*">',
               f'<meta name="twitter:description" content="{meta["twitter_description"]}">', out, label="tw:desc")

    # 7. Hero eyebrow
    out = sub1(r'<div class="hero-eyebrow">.*?</div>',
               f'<div class="hero-eyebrow">{meta["hero_eyebrow"]}</div>', out, flags=re.DOTALL, label="eyebrow")

    # 8. Hero H1 (sr-only + visible)
    sr = meta["hero_h1_sr"]
    vis = meta["hero_h1_visible"]
    new_h1 = ('<h1 class="hero-title"><span style="position:absolute;width:1px;height:1px;padding:0;'
              'margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">'
              f'{sr}</span>{vis}</h1>')
    out = sub1(r'<h1 class="hero-title">.*?</h1>', new_h1, out, flags=re.DOTALL, label="h1")

    # 9. WebPage schema name + description
    out = replace_exact(RL_WEBPAGE_NAME, f'"name": "{meta["webpage_name"]}"', out, "wp:name")
    out = replace_exact(RL_WEBPAGE_DESC, f'"description": "{meta["webpage_description"]}"', out, "wp:desc")

    # 10. Breadcrumb (leaf name del unico BreadcrumbList)
    out = replace_exact(RL_BC, f'"name": "{meta["breadcrumb_name"]}", "item"', out, "bc")

    # 11. FAQPage: regenerar mainEntity desde faqs. El bloque va en UNA linea, y
    #     un ']' dentro del texto de una respuesta romperia un regex perezoso,
    #     asi que se localiza el cierre contando corchetes fuera de string.
    ancla = '"@type": "FAQPage", "mainEntity": '
    i = out.find(ancla)
    if i < 0:
        raise RuntimeError("[faqpage] ancla no encontrada")
    ini = i + len(ancla)
    out = out[:ini] + build_faqpage(meta["faqs"]) + out[fin_corchete(out, ini) + 1:]

    # 11b. Modulo "cc-relacionados" (css + nav antes de </body>). No sale de la
    #      plantilla: lo inyecta el enlazado interno por pagina y es distinto en
    #      cada una (14 landings lo tienen, 12 no). Copiar el de la pilar a todas
    #      era lo que borraba los enlaces internos en cada regeneracion.
    propio = meta.get("related_module")
    out = MODULO_REL.sub(lambda m: propio or "", out, count=1)

    # 11c. Entradilla del hero: sale de la plantilla, pero seo_pilar_2026_08_27
    #      le metio a 3 landings un enlace a la pilar DENTRO de ese parrafo.
    #      Si esta guardada en el meta, manda la de la pagina.
    if meta.get("hero_lead"):
        out = sub1(r'<p class="sec-subtitle sec-subtitle-light" itemprop="description">.*?</p>',
                   meta["hero_lead"], out, flags=re.DOTALL, label="hero_lead")

    # 12. slug global (canonical, OG url, WebPage @id/url, breadcrumb items, alternates)
    #     OJO: es un replace ciego sobre TODO el HTML. Los enlaces internos que
    #     apuntan a la pilar a proposito (12 paginas, ancla "camisas polo", ver
    #     seo_pilar_2026_08_27.py y _2026_09_04.py) se convertian en autoenlaces
    #     — la pagina se enlazaba a si misma y se perdia la señal que rompe la
    #     canibalizacion. Se blindan antes del replace y se restauran despues.
    #     Solo la forma RELATIVA es enlace de verdad: canonical, og:url y los
    #     items del breadcrumb usan la absoluta y SI tienen que reescribirse.
    CENTINELA = "\x00PILAR\x00"
    enlace_pilar = f'href="/{RL_SLUG}"'
    out = out.replace(enlace_pilar, CENTINELA)
    out = out.replace(RL_SLUG, slug)
    out = out.replace(CENTINELA, enlace_pilar)

    # sanity checks
    assert f'<link rel="canonical" href="{canonical}">' in out, "canonical mal"
    assert 'id="perShirtGrid"' in out or 'perShirtGrid' in out, "catalogo perShirtGrid ausente"
    assert 'id="carruselTrack"' in out, "carrusel ausente"
    assert 'PACKS' in out, "packs ausente"
    return out


def main():
    template = TEMPLATE.read_text(encoding="utf-8")
    slugs = sys.argv[1:]
    if not slugs:
        slugs = sorted(p.stem[:-5] for p in SPECS.glob("*.meta.json"))
    tmpl_words = len(strip_tags(template).split())
    for slug in slugs:
        html = build(slug, template)
        (ROOT / f"{slug}.html").write_text(html, encoding="utf-8")
        words = len(strip_tags(html).split())
        print(f"  OK {slug:42} {len(html):>7,} bytes  ~{words} palabras (tmpl {tmpl_words})")
    print(f"\n[OK] {len(slugs)} landing(s) generada(s)")


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
