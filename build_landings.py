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
TEMPLATE = ROOT / "camisas-polo-ralph-lauren-colombia.html"
SPECS = ROOT / "_landings"
BASE = "https://www.camisascolombia.com"
RL_SLUG = "camisas-polo-ralph-lauren-colombia"

# ---- strings EXACTAS del template RL que reemplazamos (assert si no aparecen) ----
RL_TITLE = "Camisas Polo Estilo Ralph Lauren en Colombia | Alternativa Premium"
RL_OG_TITLE = "Camisas Polo Estilo Ralph Lauren en Colombia | Alternativa Premium"
RL_TW_TITLE = "Camisas Polo Hombre Estilo Ralph Lauren en Colombia"
RL_WEBPAGE_NAME = '"name":"Camisas Polo Estilo Ralph Lauren en Colombia | Alternativa Premium"'
RL_WEBPAGE_DESC = '"description":"Tienda online colombiana de camisas polo premium para hombre estilo Ralph Lauren. Pago contraentrega, envío gratis y +20 colores."'
RL_BC1 = '"name":"Camisas Polo Estilo Ralph Lauren","item"'          # breadcrumb compacto (head)
RL_BC2 = '"name": "Camisas Polo Estilo Ralph Lauren en Colombia",'  # breadcrumb espaciado (pre-footer)


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


def build_faqpage(faqs):
    entities = []
    for f in faqs:
        text = strip_tags(f["a"])
        entities.append({
            "@type": "Question",
            "name": f["q"],
            "acceptedAnswer": {"@type": "Answer", "text": text},
        })
    body = json.dumps(entities, ensure_ascii=False, indent=1)
    # indentar para que quede prolijo dentro del <script>
    return body


def build(slug, template):
    meta = json.loads((SPECS / f"{slug}.meta.json").read_text(encoding="utf-8"))
    section = (SPECS / f"{slug}.section.html").read_text(encoding="utf-8").rstrip()
    canonical = f"{BASE}/{slug}"
    out = template

    # 1. Seccion unica (desde el <section id RL> hasta el marcador CARRUSEL)
    carrusel = "  <!-- ═══════ CARRUSEL ═══════ -->"
    out = sub1(
        r'  <section class="sec sec-light" id="camisas-polo-ralph-lauren">.*?  <!-- ═══════ CARRUSEL ═══════ -->',
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
    out = replace_exact(RL_WEBPAGE_NAME, f'"name":"{meta["webpage_name"]}"', out, "wp:name")
    out = replace_exact(RL_WEBPAGE_DESC, f'"description":"{meta["webpage_description"]}"', out, "wp:desc")

    # 10. Breadcrumbs (ambos bloques, leaf name)
    out = replace_exact(RL_BC1, f'"name":"{meta["breadcrumb_name"]}","item"', out, "bc1")
    out = replace_exact(RL_BC2, f'"name": "{meta["breadcrumb_name"]}",', out, "bc2")

    # 11. FAQPage: regenerar mainEntity desde faqs (sub1 usa lambda -> repl literal, sin backref)
    faq_json = build_faqpage(meta["faqs"])
    faq_indented = "\n".join((" " + line) if line else line for line in faq_json.splitlines())
    out = sub1(r'"@type": "FAQPage",\n "mainEntity": \[.*?\n \]',
               '"@type": "FAQPage",\n "mainEntity": ' + faq_indented, out, flags=re.DOTALL, label="faqpage")

    # 12. slug global (canonical, OG url, WebPage @id/url, breadcrumb items, alternates)
    out = out.replace(RL_SLUG, slug)

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
