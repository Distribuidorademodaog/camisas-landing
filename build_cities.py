"""
Generates per-city HTML files for camisascolombia.com SEO.

Takes index.html as template, performs targeted SEO meta replacements per city,
and outputs:
  - camisas-polo-{slug}.html (one per city)
  - sitemap.xml (with all city URLs)
  - robots.txt (pointing to sitemap)

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


def build_city_html(template: str, city: dict) -> str:
    """Apply targeted SEO replacements for one city."""
    name = city["name"]
    name_na = city["name_no_accent"]
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

    return out


def build_sitemap(cities: list) -> str:
    """Generate sitemap.xml listing main + all city pages."""
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

    # 1. Per-city HTML files
    changed_count = 0
    for c in cities:
        html = build_city_html(template, c)
        out_path = OUTPUT_DIR / f"camisas-polo-{c['slug']}.html"
        out_path.write_text(html, encoding="utf-8")

        # Count meaningful diffs from template
        diff = sum(1 for a, b in zip(template, html) if a != b)
        diff += abs(len(template) - len(html))
        if diff > 0:
            changed_count += 1
            print(f"  {c['name']:15} -> {out_path.name:40} ({len(html):,} bytes, ~{diff} char diff)")
        else:
            print(f"  {c['name']:15} -> NO CHANGES (replacements may have failed)")

    # 2. sitemap.xml
    sitemap_path = OUTPUT_DIR / "sitemap.xml"
    sitemap_path.write_text(build_sitemap(cities), encoding="utf-8")
    print(f"\nsitemap.xml: {sitemap_path.stat().st_size} bytes")

    # 3. robots.txt
    robots_path = OUTPUT_DIR / "robots.txt"
    robots_path.write_text(build_robots(), encoding="utf-8")
    print(f"robots.txt: {robots_path.stat().st_size} bytes")

    print(f"\n[OK] Generated {len(cities)} city pages + sitemap.xml + robots.txt")
    print(f"     Changed {changed_count}/{len(cities)} files relative to template")


if __name__ == "__main__":
    main()
