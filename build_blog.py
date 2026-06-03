"""
Genera las paginas de blog para camisascolombia.com a partir de posts.json.

Outputs:
  - blog/index.html (listado de los 10 posts)
  - blog/{slug}.html (cada post)

Cada post incluye:
  - SEO meta completos
  - Article schema + BreadcrumbList + Organization + WebSite
  - HowTo o FAQPage segun el post
  - ItemList si el post tiene lista de elementos
  - Enlazado interno a otros posts + city pages + home
  - CTA al producto principal
"""
import json
import re
from pathlib import Path

BASE_URL = "https://www.camisascolombia.com"
POSTS_FILE = Path(__file__).parent / "posts.json"
PILLARS_FILE = Path(__file__).parent / "pillars.json"
OUTPUT_DIR = Path(__file__).parent / "output" / "blog"
GUIAS_DIR = Path(__file__).parent / "output" / "guias"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GUIAS_DIR.mkdir(parents=True, exist_ok=True)

CITY_NAMES = {
    "bogota": "Bogotá", "medellin": "Medellín", "cali": "Cali",
    "barranquilla": "Barranquilla", "cartagena": "Cartagena",
    "bucaramanga": "Bucaramanga", "pereira": "Pereira",
    "manizales": "Manizales", "cucuta": "Cúcuta", "ibague": "Ibagué"
}

# CSS compartido por todas las paginas del blog
BLOG_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif; color: #1a1a1a; background: #f5f0e8; line-height: 1.6; }
img { max-width: 100%; height: auto; display: block; }

.blog-header { background: #0e1828; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; }
.blog-header a { color: #C4A35A; text-decoration: none; font-weight: 600; font-size: 14px; }
.blog-header .brand { font-family: 'Cormorant Garamond', serif; font-size: 18px; color: white; }

.blog-container { max-width: 720px; margin: 0 auto; padding: 28px 20px 40px; }

.breadcrumb { font-size: 12px; color: #7a7060; margin-bottom: 16px; }
.breadcrumb a { color: #7a7060; text-decoration: none; }
.breadcrumb a:hover { color: #0e1828; }
.breadcrumb span { color: #0e1828; }

.post-category { display: inline-block; background: #9A7B3C; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
.post-meta { font-size: 12px; color: #7a7060; margin-bottom: 8px; }
.post-meta time { color: #5a5448; }

h1.post-title { font-family: 'Cormorant Garamond', serif; font-size: 32px; line-height: 1.2; color: #0e1828; margin-bottom: 14px; font-weight: 700; }
@media(min-width: 720px) { h1.post-title { font-size: 38px; } }

.post-lead { font-size: 16px; color: #4a443a; line-height: 1.7; margin-bottom: 24px; font-weight: 500; }

.post-cover { width: 100%; border-radius: 12px; margin: 0 0 28px; aspect-ratio: 16 / 9; object-fit: cover; }

.post-body { background: white; padding: 24px; border-radius: 12px; box-shadow: 0 3px 14px rgba(0,0,0,0.05); }
.post-body section { margin-bottom: 24px; }
.post-body h2 { font-family: 'Cormorant Garamond', serif; font-size: 24px; font-weight: 700; color: #0e1828; margin-bottom: 12px; line-height: 1.3; }
.post-body h3 { font-family: 'Outfit', sans-serif; font-size: 16px; font-weight: 700; color: #0e1828; margin: 18px 0 8px; }
.post-body p { font-size: 14.5px; color: #3a342a; margin-bottom: 12px; line-height: 1.7; }
.post-body strong { color: #0e1828; font-weight: 700; }
.post-body a { color: #9A7B3C; text-decoration: underline; font-weight: 600; }
.post-body a:hover { color: #0e1828; }

.howto-list { list-style: none; padding: 0; margin: 16px 0; counter-reset: howto; }
.howto-list li { display: flex; gap: 14px; padding: 14px 0; border-bottom: 1px solid #f0ece4; }
.howto-list li:last-child { border-bottom: none; }
.howto-num { width: 34px; height: 34px; flex-shrink: 0; background: #0e1828; color: #C4A35A; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: 'Cormorant Garamond', serif; font-size: 17px; font-weight: 700; }
.howto-content strong { display: block; font-size: 14px; margin-bottom: 4px; }
.howto-content p { font-size: 13px; margin: 0; }

.faq-block { margin: 20px 0; }
.faq-item { padding: 14px 0; border-bottom: 1px solid #f0ece4; }
.faq-item:last-child { border-bottom: none; }
.faq-item strong { display: block; font-size: 14px; color: #0e1828; margin-bottom: 6px; }
.faq-item p { font-size: 13.5px; color: #5a5448; margin: 0; }

.itemlist-block { background: #faf7f1; padding: 16px; border-radius: 10px; margin: 16px 0; }
.itemlist-block ol { padding-left: 22px; margin: 0; }
.itemlist-block li { margin-bottom: 10px; font-size: 14px; }
.itemlist-block li strong { color: #0e1828; }

.post-conclusion { background: #faf7f1; padding: 18px; border-radius: 10px; margin-top: 24px; border-left: 4px solid #C4A35A; }
.post-conclusion h2 { font-size: 18px; margin-bottom: 8px; }
.post-conclusion p { font-size: 14px; color: #4a443a; margin: 0; }

.related-block { background: white; padding: 20px; border-radius: 12px; margin-top: 22px; box-shadow: 0 3px 14px rgba(0,0,0,0.05); }
.related-block h3 { font-family: 'Outfit', sans-serif; font-size: 14px; font-weight: 700; color: #0e1828; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
.related-block ul { list-style: none; padding: 0; }
.related-block li { padding: 8px 0; border-bottom: 1px solid #f0ece4; }
.related-block li:last-child { border-bottom: none; }
.related-block a { color: #9A7B3C; text-decoration: none; font-weight: 600; font-size: 14px; }
.related-block a:hover { color: #0e1828; text-decoration: underline; }

.cta-block { background: #0e1828; color: white; padding: 24px; border-radius: 12px; margin-top: 22px; text-align: center; }
.cta-block h3 { font-family: 'Cormorant Garamond', serif; font-size: 24px; color: #C4A35A; margin-bottom: 8px; }
.cta-block p { font-size: 14px; opacity: 0.9; margin-bottom: 14px; }
.cta-block a { display: inline-block; background: #C4A35A; color: #0e1828; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 14px; }
.cta-block a:hover { background: white; }

.cities-block { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 12px; }
.cities-block a { display: block; padding: 8px 10px; background: #faf7f1; border-radius: 6px; text-decoration: none; color: #0e1828; font-size: 12.5px; font-weight: 600; text-align: center; }
.cities-block a:hover { background: #0e1828; color: #C4A35A; }

.blog-footer { background: #0e1828; color: rgba(255,255,255,0.6); padding: 20px; text-align: center; font-size: 12px; margin-top: 32px; }
.blog-footer a { color: #C4A35A; text-decoration: none; }

/* Blog index */
.blog-index-header { text-align: center; padding: 40px 20px 28px; }
.blog-index-header h1 { font-family: 'Cormorant Garamond', serif; font-size: 36px; color: #0e1828; margin-bottom: 8px; }
.blog-index-header p { font-size: 15px; color: #5a5448; max-width: 520px; margin: 0 auto; }

.posts-grid { display: grid; grid-template-columns: 1fr; gap: 18px; max-width: 720px; margin: 0 auto; padding: 0 20px 40px; }
@media(min-width: 720px) { .posts-grid { grid-template-columns: 1fr 1fr; } }
.post-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 3px 14px rgba(0,0,0,0.06); transition: transform 0.2s; }
.post-card:hover { transform: translateY(-4px); }
.post-card a { color: inherit; text-decoration: none; display: block; }
.post-card img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }
.post-card-body { padding: 16px 18px 18px; }
.post-card-category { display: inline-block; background: #9A7B3C; color: white; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }
.post-card h2 { font-family: 'Cormorant Garamond', serif; font-size: 20px; font-weight: 700; color: #0e1828; margin-bottom: 8px; line-height: 1.3; }
.post-card p { font-size: 13px; color: #5a5448; margin-bottom: 10px; line-height: 1.5; }
.post-card-meta { font-size: 11px; color: #8a7d6b; }
"""


def format_date_es(iso_date: str) -> str:
    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
              "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    parts = iso_date.split("-")
    return f"{int(parts[2])} de {months[int(parts[1])-1]} de {parts[0]}"


def build_article_schema(post: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post["title"],
        "description": post["meta_description"],
        "image": post["cover_image"],
        "datePublished": post["publish_date"],
        "dateModified": post["modified_date"],
        "author": {"@type": "Person", "name": post["author"]},
        "publisher": {
            "@type": "Organization",
            "name": "Camisas Colombia",
            "logo": {"@type": "ImageObject", "url": "https://media.paquetecompleto.com.co/landing/logo.png"}
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{BASE_URL}/blog/{post['slug']}"},
        "articleSection": post["category"],
        "wordCount": estimate_word_count(post)
    }


def build_breadcrumb_schema(post: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{BASE_URL}/blog"},
            {"@type": "ListItem", "position": 3, "name": post["title"], "item": f"{BASE_URL}/blog/{post['slug']}"}
        ]
    }


def build_howto_schema(post: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": post["title"],
        "description": post["meta_description"],
        "image": post["cover_image"],
        "step": [
            {"@type": "HowToStep", "position": i + 1, "name": s["name"], "text": s["text"]}
            for i, s in enumerate(post["howto_steps"])
        ]
    }


def build_faq_schema(post: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in post["faqs"]
        ]
    }


def build_itemlist_schema(post: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": post["title"],
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": item["name"], "description": item["description"]}
            for i, item in enumerate(post["list_items"])
        ]
    }


def estimate_word_count(post: dict) -> int:
    text = post.get("intro", "") + " "
    for s in post.get("sections", []):
        text += " ".join(s["paragraphs"]) + " "
    text += post.get("conclusion", "")
    return len(text.split())


def render_post(post: dict, all_posts: dict) -> str:
    schemas = [build_article_schema(post), build_breadcrumb_schema(post)]
    if "howto_steps" in post:
        schemas.append(build_howto_schema(post))
    if "faqs" in post:
        schemas.append(build_faq_schema(post))
    if "list_items" in post:
        schemas.append(build_itemlist_schema(post))

    schema_html = "\n".join(
        f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'
        for s in schemas
    )

    sections_html = ""
    for s in post["sections"]:
        sections_html += f'<section><h2>{s["heading"]}</h2>'
        for p in s["paragraphs"]:
            sections_html += f"<p>{p}</p>"
        sections_html += "</section>"

    howto_html = ""
    if "howto_steps" in post:
        howto_html = '<section><h2>📋 Pasos prácticos</h2><ol class="howto-list">'
        for i, step in enumerate(post["howto_steps"]):
            howto_html += f'<li><div class="howto-num">{i+1}</div><div class="howto-content"><strong>{step["name"]}</strong><p>{step["text"]}</p></div></li>'
        howto_html += "</ol></section>"

    faqs_html = ""
    if "faqs" in post:
        faqs_html = '<section><h2>❓ Preguntas frecuentes</h2><div class="faq-block">'
        for f in post["faqs"]:
            faqs_html += f'<div class="faq-item"><strong>{f["q"]}</strong><p>{f["a"]}</p></div>'
        faqs_html += "</div></section>"

    itemlist_html = ""
    if "list_items" in post:
        itemlist_html = '<section><h2>📋 Resumen rápido</h2><div class="itemlist-block"><ol>'
        for item in post["list_items"]:
            itemlist_html += f'<li><strong>{item["name"]}:</strong> {item["description"]}</li>'
        itemlist_html += "</ol></div></section>"

    related_html = '<div class="related-block"><h3>Artículos relacionados</h3><ul>'
    for slug in post["related_posts"]:
        rp = all_posts.get(slug)
        if rp:
            related_html += f'<li><a href="/blog/{slug}">{rp["title"]}</a></li>'
    related_html += "</ul></div>"

    cities_html = '<div class="related-block"><h3>Compra camisas polo en tu ciudad</h3><div class="cities-block">'
    for c in post["related_cities"]:
        cities_html += f'<a href="/camisas-polo-{c}">{CITY_NAMES[c]}</a>'
    cities_html += "</div></div>"

    cta_html = '''<div class="cta-block">
    <h3>¿Listo para tu próxima camisa polo?</h3>
    <p>+998 clientes ya pidieron las suyas con pago contraentrega y envío gratis a toda Colombia.</p>
    <a href="/">Ver packs disponibles →</a>
    </div>'''

    return f'''<!DOCTYPE html>
<html lang="es-CO">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{post["title"]} | Blog Camisas Colombia</title>
<meta name="description" content="{post["meta_description"]}">
<meta name="author" content="{post["author"]}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{BASE_URL}/blog/{post["slug"]}">

<meta property="og:type" content="article">
<meta property="og:site_name" content="Camisas Colombia">
<meta property="og:title" content="{post["title"]}">
<meta property="og:description" content="{post["meta_description"]}">
<meta property="og:image" content="{post["cover_image"]}">
<meta property="og:url" content="{BASE_URL}/blog/{post["slug"]}">
<meta property="og:locale" content="es_CO">
<meta property="article:published_time" content="{post["publish_date"]}">
<meta property="article:modified_time" content="{post["modified_date"]}">
<meta property="article:author" content="{post["author"]}">
<meta property="article:section" content="{post["category"]}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{post["title"]}">
<meta name="twitter:description" content="{post["meta_description"]}">
<meta name="twitter:image" content="{post["cover_image"]}">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">

{schema_html}

<style>{BLOG_CSS}</style>
</head>
<body>
<nav class="blog-header">
  <a href="/" class="brand">Camisas Colombia</a>
  <a href="/blog">← Blog</a>
</nav>

<main class="blog-container">
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="/">Inicio</a> › <a href="/blog">Blog</a> › <span>{post["title"]}</span>
  </nav>

  <article>
    <span class="post-category">{post["category"]}</span>
    <h1 class="post-title">{post["title"]}</h1>
    <div class="post-meta">
      <time datetime="{post["publish_date"]}">{format_date_es(post["publish_date"])}</time> · Por {post["author"]} · {post["read_time"]} min de lectura
    </div>
    <p class="post-lead">{post["intro"]}</p>

    <img class="post-cover" src="{post["cover_image"]}" alt="{post["title"]}" loading="lazy">

    <div class="post-body">
      {sections_html}
      {howto_html}
      {faqs_html}
      {itemlist_html}

      <div class="post-conclusion">
        <h2>Conclusión</h2>
        <p>{post["conclusion"]}</p>
      </div>
    </div>

    {related_html}
    {cities_html}
    {cta_html}
  </article>
</main>

<footer class="blog-footer">
  © Camisas Colombia · <a href="/">Inicio</a> · <a href="/blog">Blog</a> · <a href="/sitemap.xml">Sitemap</a>
</footer>
</body>
</html>'''


def render_index(posts: list) -> str:
    cards_html = ""
    for p in posts:
        cards_html += f'''<article class="post-card">
          <a href="/blog/{p["slug"]}">
            <img src="{p["cover_image"]}" alt="{p["title"]}" loading="lazy">
            <div class="post-card-body">
              <span class="post-card-category">{p["category"]}</span>
              <h2>{p["title"]}</h2>
              <p>{p["meta_description"]}</p>
              <div class="post-card-meta">{format_date_es(p["publish_date"])} · {p["read_time"]} min</div>
            </div>
          </a>
        </article>'''

    blog_schema = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "Blog Camisas Colombia",
        "description": "Guías de tallas, estilo, materiales y cuidados de camisas polo en Colombia.",
        "url": f"{BASE_URL}/blog",
        "publisher": {"@type": "Organization", "name": "Camisas Colombia"},
        "blogPost": [
            {"@type": "BlogPosting", "headline": p["title"], "url": f"{BASE_URL}/blog/{p['slug']}",
             "datePublished": p["publish_date"], "author": {"@type": "Person", "name": p["author"]}}
            for p in posts
        ]
    }
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{BASE_URL}/blog"}
        ]
    }

    return f'''<!DOCTYPE html>
<html lang="es-CO">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blog Camisas Colombia | Guías de Estilo, Tallas y Cuidado de Polos</title>
<meta name="description" content="Blog de Camisas Colombia: guías de tallas, comparativas de marcas, estilos de polos, cuidados y consejos de moda masculina en Colombia.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{BASE_URL}/blog">

<meta property="og:type" content="website">
<meta property="og:title" content="Blog Camisas Colombia">
<meta property="og:description" content="Guías de tallas, estilo, materiales y cuidados de camisas polo en Colombia.">
<meta property="og:url" content="{BASE_URL}/blog">
<meta property="og:image" content="https://media.paquetecompleto.com.co/landing/hero-camisa.jpg">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">

<script type="application/ld+json">{json.dumps(blog_schema, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(breadcrumb_schema, ensure_ascii=False)}</script>

<style>{BLOG_CSS}</style>
</head>
<body>
<nav class="blog-header">
  <a href="/" class="brand">Camisas Colombia</a>
  <a href="/">← Inicio</a>
</nav>

<header class="blog-index-header">
  <h1>Blog Camisas Colombia</h1>
  <p>Guías de tallas, estilo, materiales y cuidados de camisas polo para hombres en Colombia.</p>
</header>

<main class="posts-grid">
  {cards_html}
</main>

<footer class="blog-footer">
  © Camisas Colombia · <a href="/">Inicio</a> · <a href="/blog">Blog</a> · <a href="/sitemap.xml">Sitemap</a>
</footer>
</body>
</html>'''


def render_pillar(pillar: dict, all_posts: dict) -> str:
    """Pillar pages: same template as posts but with table of contents."""
    html = render_post(pillar, all_posts)
    if "table_of_contents" in pillar:
        toc_html = '<div class="post-toc"><h3>📑 Tabla de contenidos</h3><ol>'
        for item in pillar["table_of_contents"]:
            anchor = re.sub(r'[^a-z0-9]+', '-', item.lower()).strip('-')
            toc_html += f'<li><a href="#{anchor}">{item}</a></li>'
        toc_html += '</ol></div>'
        html = html.replace('<p class="post-lead">', toc_html + '<p class="post-lead">')
    return html


def render_guias_hub(posts: list, pillars: list) -> str:
    """Hub /guias/ que agrupa posts por topic clusters."""
    clusters = {
        "Tallas y Medidas": ["como-elegir-talla-camisa-polo", "tallas-grandes-3xl-4xl-5xl"],
        "Estilo y Combinaciones": ["como-combinar-camisa-polo", "estilos-camisa-polo", "ocasiones-camisa-polo", "tendencias-2026-camisas-polo-colombia"],
        "Materiales y Tejidos": ["algodon-pique-vs-liso", "historia-origen-camisa-polo"],
        "Comparativas": ["camisa-polo-ralph-lauren-original-vs-alternativa", "polo-vs-camisa-cuello-botones", "manga-larga-vs-corta", "mejores-tiendas-online-camisas-hombre-colombia"],
        "Cuidados y Mantenimiento": ["cuidados-camisa-polo", "como-lavar-camisa-blanca-sin-amarillear"],
        "Compras Seguras": ["pago-contraentrega-seguro"]
    }

    posts_by_slug = {p["slug"]: p for p in posts}

    # Pillar destacada arriba
    pillar_html = ""
    if pillars:
        p = pillars[0]
        pillar_html = f'''<div class="pillar-featured">
          <span class="pillar-badge">Guía Definitiva</span>
          <h2><a href="/guias/{p["slug"]}">{p["title"]}</a></h2>
          <p>{p["meta_description"]}</p>
          <p class="pillar-meta">{estimate_word_count(p):,} palabras · {p["read_time"]} min de lectura</p>
        </div>'''

    clusters_html = ""
    for cluster_name, slugs in clusters.items():
        clusters_html += f'<section class="cluster"><h2>{cluster_name}</h2><div class="cluster-posts">'
        for slug in slugs:
            p = posts_by_slug.get(slug)
            if p:
                clusters_html += f'<a href="/blog/{slug}" class="cluster-card"><h3>{p["title"]}</h3><p>{p["meta_description"]}</p><span class="cluster-meta">{p["read_time"]} min</span></a>'
        clusters_html += '</div></section>'

    extra_css = """
    .pillar-featured { background:#0e1828; color:white; padding:28px 24px; border-radius:14px; margin:24px 20px; max-width:720px; box-shadow:0 6px 24px rgba(0,0,0,0.12); }
    @media(min-width:760px) { .pillar-featured { margin: 24px auto; } }
    .pillar-badge { display:inline-block; background:#C4A35A; color:#0e1828; padding:4px 10px; border-radius:4px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px; }
    .pillar-featured h2 { font-family:'Cormorant Garamond',serif; font-size:24px; line-height:1.3; margin-bottom:10px; }
    .pillar-featured h2 a { color:white; text-decoration:none; }
    .pillar-featured h2 a:hover { color:#C4A35A; }
    .pillar-featured p { color:rgba(255,255,255,0.85); font-size:14px; line-height:1.6; margin-bottom:10px; }
    .pillar-meta { color:#C4A35A !important; font-size:12px !important; font-weight:600; }
    .cluster { max-width:720px; margin:32px auto 0; padding:0 20px; }
    .cluster h2 { font-family:'Cormorant Garamond',serif; font-size:24px; color:#0e1828; margin-bottom:14px; padding-bottom:8px; border-bottom:2px solid #C4A35A; }
    .cluster-posts { display:grid; grid-template-columns:1fr; gap:12px; }
    @media(min-width:600px) { .cluster-posts { grid-template-columns:1fr 1fr; } }
    .cluster-card { background:white; padding:14px 16px; border-radius:10px; text-decoration:none; color:inherit; box-shadow:0 2px 8px rgba(0,0,0,0.04); transition:transform 0.15s; }
    .cluster-card:hover { transform:translateY(-2px); box-shadow:0 4px 14px rgba(0,0,0,0.08); }
    .cluster-card h3 { font-family:'Outfit',sans-serif; font-size:14.5px; color:#0e1828; margin-bottom:6px; line-height:1.35; }
    .cluster-card p { font-size:12px; color:#5a5448; line-height:1.5; margin-bottom:8px; }
    .cluster-meta { font-size:11px; color:#8a7d6b; }
    """

    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Guías", "item": f"{BASE_URL}/guias"}
        ]
    }
    collection_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Guías sobre camisas polo en Colombia",
        "description": "Hub de guías sobre tallas, estilos, materiales, cuidados, comparativas y compras seguras de camisas polo en Colombia.",
        "url": f"{BASE_URL}/guias"
    }

    return f'''<!DOCTYPE html>
<html lang="es-CO">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Guías de Camisas Polo en Colombia | Hub de Contenido</title>
<meta name="description" content="Hub de guías sobre camisas polo en Colombia: tallas, estilos, cuidados, comparativas, materiales y compras seguras. 11 guías + 1 guía definitiva.">
<link rel="canonical" href="{BASE_URL}/guias">

<meta property="og:type" content="website">
<meta property="og:title" content="Guías de Camisas Polo en Colombia">
<meta property="og:description" content="Hub de guías sobre camisas polo en Colombia.">
<meta property="og:url" content="{BASE_URL}/guias">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">

<script type="application/ld+json">{json.dumps(collection_schema, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(breadcrumb_schema, ensure_ascii=False)}</script>

<style>{BLOG_CSS}{extra_css}</style>
</head>
<body>
<nav class="blog-header">
  <a href="/" class="brand">Camisas Colombia</a>
  <a href="/">← Inicio</a>
</nav>

<header class="blog-index-header">
  <h1>Guías de Camisas Polo</h1>
  <p>Topic clusters organizados por tema. Encuentra exactamente la información que buscas.</p>
</header>

{pillar_html}

{clusters_html}

<footer class="blog-footer">
  © Camisas Colombia · <a href="/">Inicio</a> · <a href="/blog">Blog</a> · <a href="/guias">Guías</a> · <a href="/sitemap.xml">Sitemap</a>
</footer>
</body>
</html>'''


def main():
    posts = json.loads(POSTS_FILE.read_text(encoding="utf-8"))
    posts_by_slug = {p["slug"]: p for p in posts}

    pillars = []
    if PILLARS_FILE.exists():
        pillars = json.loads(PILLARS_FILE.read_text(encoding="utf-8"))

    print(f"Building {len(posts)} blog posts + {len(pillars)} pillars...")

    for p in posts:
        html = render_post(p, posts_by_slug)
        out = OUTPUT_DIR / f"{p['slug']}.html"
        out.write_text(html, encoding="utf-8")
        wc = estimate_word_count(p)
        print(f"  blog/{p['slug']:50} ({wc} words, {len(html):,} bytes)")

    for p in pillars:
        html = render_pillar(p, posts_by_slug)
        out = GUIAS_DIR / f"{p['slug']}.html"
        out.write_text(html, encoding="utf-8")
        wc = estimate_word_count(p)
        print(f"  guias/{p['slug']:50} ({wc} words, {len(html):,} bytes)")

    index_html = render_index(posts)
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"\n  blog/index.html ({len(index_html):,} bytes)")

    guias_index = render_guias_hub(posts, pillars)
    (GUIAS_DIR / "index.html").write_text(guias_index, encoding="utf-8")
    print(f"  guias/index.html ({len(guias_index):,} bytes)")

    print(f"\n[OK] Generated {len(posts)} posts + {len(pillars)} pillars + 2 hubs")


if __name__ == "__main__":
    main()
