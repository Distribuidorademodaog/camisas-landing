"""
Generates per-city HTML files for camisascolombia.com SEO.

Takes index.html as template, performs SEO meta replacements per city,
AND injects a visible city-specific section (delivery info + testimonial + FAQ)
right before the VARIEDAD section.

Outputs:
  - camisas-polo-{slug}.html (one per city)
  - sitemap.xml (with all city URLs)
  - robots.txt

Usage:
  python build_cities.py
"""
import json
import re
from pathlib import Path

BASE_URL = "https://www.camisascolombia.com"
TEMPLATE_FILE = Path(r"C:\Users\Janus\Downloads\index (13).html")
CITIES_FILE = Path(__file__).parent / "cities.json"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def build_city_section(city: dict) -> str:
    """HTML block inserted in the body, visible to users — rich SEO signal (~1500-2000 words)."""
    name = city["name"]
    dept = city["department"]
    intro = city["intro_paragraph"]
    neighborhoods = city["neighborhoods_extended"]
    testimonials = city["testimonials"]
    faqs = city["faqs"]
    cta = city["cta_closing"]
    estilo = city.get("estilo_local", {})
    envios = city.get("envios_barrios", {})
    referentes = city.get("referentes_moda", {})

    # Testimonios (8 por ciudad)
    testi_html = ""
    for t in testimonials:
        testi_html += f"""        <div class="city-testi">
          <span class="city-stars">★★★★★</span>
          <p class="city-quote">"{t['quote']}"</p>
          <p class="city-author">— {t['name']}, {t['barrio']} ({name})</p>
        </div>
"""

    # FAQs (12 por ciudad)
    faqs_html = ""
    for f in faqs:
        faqs_html += f"""        <div class="city-faq">
          <strong>{f['q']}</strong>
          <p>{f['a']}</p>
        </div>
"""

    # SECCIÓN NUEVA: Estilo local
    estilo_html = ""
    if estilo:
        paragraphs = "".join([f"<p>{p}</p>" for p in estilo.get("paragraphs", [])])
        estilo_html = f"""    <div class="city-block">
      <h3 class="city-block-title">👔 {estilo.get("heading", "Estilo local")}</h3>
      {paragraphs}
    </div>
"""

    # SECCIÓN NUEVA: Envíos por barrio con zonas detalladas
    envios_html = ""
    if envios:
        zones_html = ""
        for z in envios.get("zones", []):
            zones_html += f"""        <div class="city-zone">
          <strong>{z['name']}</strong> · <span class="city-zone-time">{z['time']}</span>
          <p>{z['detail']}</p>
        </div>
"""
        envios_html = f"""    <div class="city-block">
      <h3 class="city-block-title">📍 {envios.get("heading", "Cobertura y tiempos por zona")}</h3>
      <p>{envios.get("intro", "")}</p>
      <div class="city-zones">
{zones_html}      </div>
    </div>
"""

    # SECCIÓN NUEVA: Referentes de moda local
    referentes_html = ""
    if referentes:
        paragraphs = "".join([f"<p>{p}</p>" for p in referentes.get("paragraphs", [])])
        referentes_html = f"""    <div class="city-block">
      <h3 class="city-block-title">🛍️ {referentes.get("heading", "Referentes de moda locales")}</h3>
      {paragraphs}
    </div>
"""

    return f"""  <!-- ═══════ CIUDAD: {name} ═══════ -->
  <div class="city-section">
    <div class="sec-head">
      <div class="sec-kicker">Envíos rápidos · {name}</div>
      <h2 class="sec-title">Camisas polo en <em>{name}</em> con entrega 1-3 días</h2>
      <p class="sec-subtitle city-intro">{intro}</p>
    </div>

    <div class="city-block">
      <h3 class="city-block-title">🚚 Llegamos a tu zona en {name}</h3>
      <p>{neighborhoods}.</p>
      <small>Y a todo el área metropolitana de {name}.</small>
    </div>

{estilo_html}
{envios_html}
    <div class="city-block">
      <h3 class="city-block-title">Lo que dicen nuestros clientes en {name}</h3>
      <div class="city-testimonials">
{testi_html}      </div>
    </div>

{referentes_html}
    <div class="city-block">
      <h3 class="city-block-title">📦 Preguntas frecuentes sobre envíos a {name}</h3>
      <div class="city-faqs">
{faqs_html}      </div>
    </div>

    <div class="city-cta-block">
      <p>{cta}</p>
    </div>
  </div>

"""


def build_city_html(template: str, city: dict) -> str:
    """Apply SEO meta replacements + inject visible city section."""
    name = city["name"]
    slug = city["slug"]
    dept = city["department"]
    lat = city["lat"]
    lng = city["lng"]
    extra_kw = city["extra_keywords"]
    canonical = f"{BASE_URL}/camisas-polo-{slug}"

    out = template

    # 1. <title>
    out = out.replace(
        "<title>Camisas Polo para Hombre Estilo Ralph Lauren en Colombia</title>",
        f"<title>Camisas Polo en {name} | Pago Contraentrega Colombia</title>"
    )

    # 2. meta description
    old_desc = '<meta name="description" content="Camisas polo hombre estilo Ralph Lauren en Colombia con +20 colores premium y tallas S a 5XL. Pago contraentrega, envío gratis. 4.9★ +998 clientes.">'
    new_desc = f'<meta name="description" content="Camisas polo para hombre en {name}, {dept}. Estilo Ralph Lauren, +20 colores, tallas S a 5XL. Paga al recibir, envío 1-3 días en {name}. 4.9★ +998 clientes.">'
    out = out.replace(old_desc, new_desc)

    # 3. meta keywords (insert city-specific keywords at the start)
    out = re.sub(
        r'<meta name="keywords" content="([^"]+)">',
        lambda m: f'<meta name="keywords" content="{extra_kw}, ' + m.group(1) + '">',
        out, count=1
    )

    # 4. geo meta
    out = out.replace(
        '<meta name="geo.placename" content="Colombia">',
        f'<meta name="geo.placename" content="{name}, {dept}, Colombia">'
    )
    out = out.replace(
        '<meta name="geo.position" content="4.5709;-74.2973">',
        f'<meta name="geo.position" content="{lat};{lng}">'
    )
    out = out.replace(
        '<meta name="ICBM" content="4.5709, -74.2973">',
        f'<meta name="ICBM" content="{lat}, {lng}">'
    )

    # 5. canonical
    out = out.replace(
        '<link rel="canonical" href="https://www.camisascolombia.com/">',
        f'<link rel="canonical" href="{canonical}">'
    )

    # 6. og:title & og:description & og:url
    out = out.replace(
        '<meta property="og:title" content="Camisas Polo para Hombre Estilo Ralph Lauren en Colombia">',
        f'<meta property="og:title" content="Camisas Polo Hombre en {name} | Pago Contraentrega Colombia">'
    )
    out = out.replace(
        '<meta property="og:description" content="Camisas polo premium estilo Ralph Lauren. +20 colores, tallas S a 5XL. Paga al recibir, envío gratis a todo Colombia. 4.9★ +998 clientes.">',
        f'<meta property="og:description" content="Camisas polo premium estilo Ralph Lauren en {name}, {dept}. +20 colores, tallas S a 5XL. Paga al recibir, envío 1-3 días en {name}. 4.9★ +998 clientes.">'
    )
    out = out.replace(
        '<meta property="og:url" content="https://www.camisascolombia.com/">',
        f'<meta property="og:url" content="{canonical}">'
    )

    # 7. Inyectar bloque visible de ciudad ANTES del carrusel
    anchor = '<!-- ═══════ CARRUSEL ═══════ -->'
    section = build_city_section(city)
    if anchor in out:
        out = out.replace(anchor, section + anchor)
    else:
        print(f"  WARNING: anchor '{anchor}' not found for {name}")

    # 8. ELIMINAR SECCIONES GENERICAS en city pages para reducir DRASTICAMENTE la
    #    duplicacion vs home y entre ciudades (fix para 'Rastreada/Descubierta: sin indexar'
    #    en Search Console — Google trataba las 10 paginas como doorway pages casi identicas).
    #    Se quita el bloque completo VARIEDAD -> PACKS (VARIEDAD, BENEFICIOS, DESACREDITACION,
    #    HowTo guia de tallas y TESTIMONIOS genericos). El city page queda enfocado en:
    #    hero + seccion LOCAL unica (intro, barrios, testimonios y FAQs de la ciudad) + packs.
    out = re.sub(
        r'  <!-- ═══════ VARIEDAD ═══════ -->.*?(?=  <!-- ═══════ PACKS ═══════ -->)',
        '',
        out,
        flags=re.DOTALL,
        count=1
    )
    out = re.sub(
        r'  <!-- ═══════ FAQ ═══════ -->.*?(?=  <!-- ═══════ CIUDADES ATENDIDAS ═══════ -->)',
        '',
        out,
        flags=re.DOTALL,
        count=1
    )

    return out


def build_sitemap(cities: list) -> str:
    urls = [{"loc": f"{BASE_URL}/", "priority": "1.0", "changefreq": "weekly"}]
    for c in cities:
        urls.append({
            "loc": f"{BASE_URL}/camisas-polo-{c['slug']}",
            "priority": "0.8",
            "changefreq": "weekly"
        })

    # Blog: index + posts (lee posts.json si existe)
    posts_path = Path(__file__).parent / "posts.json"
    if posts_path.exists():
        urls.append({
            "loc": f"{BASE_URL}/blog",
            "priority": "0.7",
            "changefreq": "weekly"
        })
        posts = json.loads(posts_path.read_text(encoding="utf-8"))
        for p in posts:
            urls.append({
                "loc": f"{BASE_URL}/blog/{p['slug']}",
                "priority": "0.6",
                "changefreq": "monthly",
                "lastmod": p.get("modified_date", p.get("publish_date"))
            })

    # Guias hub + pillar pages
    pillars_path = Path(__file__).parent / "pillars.json"
    if pillars_path.exists():
        urls.append({
            "loc": f"{BASE_URL}/guias",
            "priority": "0.8",
            "changefreq": "weekly"
        })
        pillars = json.loads(pillars_path.read_text(encoding="utf-8"))
        for p in pillars:
            urls.append({
                "loc": f"{BASE_URL}/guias/{p['slug']}",
                "priority": "0.9",  # pillar pages prioridad alta
                "changefreq": "monthly",
                "lastmod": p.get("modified_date", p.get("publish_date"))
            })

    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        parts.append("  <url>")
        parts.append(f"    <loc>{u['loc']}</loc>")
        if u.get("lastmod"):
            parts.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        parts.append(f"    <changefreq>{u.get('changefreq','weekly')}</changefreq>")
        parts.append(f"    <priority>{u['priority']}</priority>")
        parts.append("  </url>")
    parts.append("</urlset>")
    return "\n".join(parts) + "\n"


def build_robots() -> str:
    return f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""


def main():
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    cities = json.loads(CITIES_FILE.read_text(encoding="utf-8"))

    print(f"Template: {len(template):,} bytes")
    print(f"Cities: {len(cities)}\n")

    for c in cities:
        html = build_city_html(template, c)
        out_path = OUTPUT_DIR / f"camisas-polo-{c['slug']}.html"
        out_path.write_text(html, encoding="utf-8")
        size_diff = len(html) - len(template)
        print(f"  {c['name']:15} -> {out_path.name:40} ({len(html):,} bytes, +{size_diff} vs template)")

    (OUTPUT_DIR / "sitemap.xml").write_text(build_sitemap(cities), encoding="utf-8")
    (OUTPUT_DIR / "robots.txt").write_text(build_robots(), encoding="utf-8")

    print(f"\n[OK] Generated {len(cities)} city pages + sitemap.xml + robots.txt")


if __name__ == "__main__":
    main()
