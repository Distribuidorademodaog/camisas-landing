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
    """HTML block inserted in the body, visible to users — rich SEO signal (~600-800 words)."""
    name = city["name"]
    dept = city["department"]
    intro = city["intro_paragraph"]
    neighborhoods = city["neighborhoods_extended"]
    testimonials = city["testimonials"]
    faqs = city["faqs"]
    cta = city["cta_closing"]

    # Testimonios
    testi_html = ""
    for t in testimonials:
        testi_html += f"""        <div class="city-testi">
          <span class="city-stars">★★★★★</span>
          <p class="city-quote">"{t['quote']}"</p>
          <p class="city-author">— {t['name']}, {t['barrio']} ({name})</p>
        </div>
"""

    # FAQs
    faqs_html = ""
    for f in faqs:
        faqs_html += f"""        <div class="city-faq">
          <strong>{f['q']}</strong>
          <p>{f['a']}</p>
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

    <div class="city-block">
      <h3 class="city-block-title">Lo que dicen nuestros clientes en {name}</h3>
      <div class="city-testimonials">
{testi_html}      </div>
    </div>

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
        "<title>Camisas Polo para Hombre Estilo Ralph Lauren en Colombia | Pago Contraentrega</title>",
        f"<title>Camisas Polo Hombre en {name} ({dept}) | Pago Contraentrega Colombia</title>"
    )

    # 2. meta description
    old_desc = '<meta name="description" content="Camisas polo para hombre estilo Ralph Lauren en Colombia. Alternativa premium a precio justo, +20 colores, tallas S a 5XL. Paga al recibir, envío gratis. 4.9★ +998 clientes.">'
    new_desc = f'<meta name="description" content="Camisas polo para hombre en {name}, {dept}. Premium estilo Ralph Lauren, +20 colores, tallas S a 5XL. Paga al recibir en {name}, envío 1-3 días. 4.9★ +998 clientes en Colombia.">'
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
        '<meta property="og:title" content="Camisas Polo Hombre Estilo Ralph Lauren en Colombia | Pago Contraentrega">',
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

    # 8. ELIMINAR TESTIMONIOS y FAQ genericos en city pages.
    #    Esto reduce duplicacion vs home (fix para 'canonical duplicado' de Search Console).
    #    Los city pages ya tienen testimonios + FAQs locales en la seccion de ciudad.
    out = re.sub(
        r'  <!-- ═══════ TESTIMONIOS ═══════ -->.*?(?=  <!-- ═══════ PACKS ═══════ -->)',
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
    urls = [{"loc": f"{BASE_URL}/", "priority": "1.0"}]
    for c in cities:
        urls.append({
            "loc": f"{BASE_URL}/camisas-polo-{c['slug']}",
            "priority": "0.8"
        })

    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        parts.append("  <url>")
        parts.append(f"    <loc>{u['loc']}</loc>")
        parts.append(f"    <changefreq>weekly</changefreq>")
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
