# -*- coding: utf-8 -*-
"""
Correcciones del audit de GEO Optimizer — 2026-10-15.

Puntaje de partida: **75/100** (banda «good», rubrica v2). Desglose:

    content        14/14  ✓
    meta           11/11  ✓
    google_ai      19/20   (G-DATES en warn)
    robots         11/14
    schema         12/14
    llms            5/6
    signals         3/6
    brand_entity    3/12  <- el hueco grande
    ai_discovery    0/3
    penalizacion   -3      (senales negativas)

De las recomendaciones del audit se aplican las que son reales en este sitio. Las
que NO se aplican, y por que, estan al final — importa tanto como lo que se hace.

── FASE A · robots.txt: nombrar los bots de BUSQUEDA ──────────────────────────

El robots.txt nombraba GPTBot, ClaudeBot y PerplexityBot, que son los bots de
ENTRENAMIENTO y de indice. Faltaban los de BUSQUEDA, que son los que deciden si
el sitio puede aparecer en una respuesta de IA: **OAI-SearchBot** (ChatGPT) y
**Claude-SearchBot**.

⚠️ Honestidad sobre el efecto: el fichero empieza con `User-agent: *` / `Allow: /`,
asi que esos bots YA tenian acceso por el comodin. Nombrarlos no les abre nada
nuevo; quita la ambiguedad (un crawler aplica el bloque mas especifico que
encuentra) y es lo que el audit puntua. No esperar un cambio de trafico por esto.

── FASE B · G-DATES: el sitio no declaraba ninguna fecha ──────────────────────

Ni `datePublished` ni `dateModified` en el WebPage. Se añade `dateModified`
tomado del **`<lastmod>` que el propio sitemap declara para esa URL**, no la fecha
de hoy a bulto: asi la fecha del schema y la del sitemap no se contradicen.

No se añade una fecha VISIBLE. El check la premia, pero una fecha de publicacion
en la portada de una tienda no significa nada y envejece mal.

── FASE C · formularios sin etiqueta ──────────────────────────────────────────

Los dos radios de metodo de pago y los contadores de cantidad de los order bumps
no tenian `label` ni `aria-label`: un agente de IA (o un lector de pantalla) no
sabe que son. Se les pone `aria-label`. Los campos de nombre y celular ya tenian
`placeholder`, se dejan.

── FASE D · el video del hero sin VideoObject ─────────────────────────────────

Hay un `<video>` en el hero y ningun schema que lo describa.

⚠️ El audit tambien pide subtitulos o transcripcion para ese video. **No aplica**:
el video es `muted`, decorativo, sin voz. No hay nada que transcribir.

── FASE E · feed RSS ──────────────────────────────────────────────────────────

El sitio tiene blog y no tenia feed. Se genera `/feed.xml` con las entradas que
siguen indexables (las 4 podadas el 11-oct quedan fuera) y se declara en el head.

── FASE F · endpoints de descubrimiento para IA ───────────────────────────────

`ai_discovery` daba 0/3. Se crean `/.well-known/ai.txt`, `/ai/summary.json` y
`/ai/faq.json`.

⚠️ Son **convenciones emergentes, no estandares** como robots.txt o el sitemap.
Cuestan tres ficheros estaticos y los puntua el audit; no prometen nada por si
solos.

── FASE G · llms-full.txt ─────────────────────────────────────────────────────

Daba 404. Se genera desde las **316 preguntas reales** del FAQPage ya desplegado
en el sitio: contenido existente y verificado, no inventado para la ocasion.

── Lo que NO se aplica, y por que ─────────────────────────────────────────────

🚫 **«Keyword stuffing: camisas al 3,5 % — diversifica el vocabulario».** No se
toca. La tabla de la propia investigacion que cita el skill (Princeton KDD 2024)
pone el keyword stuffing con efecto ~0 y dice explicitamente que NO se aplique.
Aqui el aviso salta porque el producto SE LLAMA camisas: escribir con menos
claridad sobre lo que se vende para bajar una densidad es cambiar algo que
funciona por un punto de un marcador.

🚫 **«Hidden text detected — patron de cloaking».** Comprobado: el texto visible
de la portada SI nombra camisa, oxford, lino, polo y «Camisas Colombia». No hay
cloaking; el `<span>` oculto del H1 es el patron estandar de lectores de pantalla
y repite lo que ya esta visible. Lo que si queda es que el H1 VISIBLE es un lema
(«Vístete bien. Paga al llegar.») en vez de decir el producto — y esa es la pagina
que mejor convierte del sitio (48,2 clics/1.000). Rediseñar su hero no es una
correccion de GEO, es una decision de negocio: se deja señalado, sin tocar.

🚫 **`sameAs` de la Organization.** Sigue vacio. Es el hueco mas caro de
`brand_entity`, pero la unica pagina de Facebook de la cuenta de Meta de este
negocio se llama «Infinity Store». `sameAs` afirma «esta es la MISMA entidad»:
poner ahi otra marca confunde la entidad. Hace falta que el negocio diga sus
perfiles reales. Wikipedia/Wikidata/Crunchbase, que es lo que sugiere el audit,
no aplican a una tienda de este tamaño.

🚫 **Atributos WebMCP** (`toolname`/`tooldescription`). Propuesta de un solo
navegador, sin adopcion. No se añade marcado especulativo.

Uso:  python geo_optimizer_2026_10_15.py [--dry-run]
"""
import glob
import io
import json
import os
import re
import shutil
import sys
import time

DRY = "--dry-run" in sys.argv
STAMP = time.strftime("%Y%m%d-%H%M")
BASE = "https://www.camisascolombia.com"
HOY = time.strftime("%Y-%m-%d")


def paginas():
    return (sorted(glob.glob("*.html")) + sorted(glob.glob("blog/*.html"))
            + sorted(glob.glob("guias/*.html")))


def guardar(path, texto):
    if DRY:
        return
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    if os.path.exists(path):
        shutil.copy(path, path + ".bak-geoopt-" + STAMP)
    tmp = path + ".tmp"
    io.open(tmp, "w", encoding="utf-8", newline="").write(texto)
    os.replace(tmp, path)


def ruta_de(path):
    r = path.replace(os.sep, "/")
    r = re.sub(r"\.html$", "", r)
    return "/" if r == "index" else "/" + r


def lastmods():
    s = io.open("sitemap.xml", encoding="utf-8").read()
    out = {}
    for b in re.findall(r"<url>(.*?)</url>", s, re.S):
        loc = re.search(r"<loc>([^<]+)</loc>", b)
        lm = re.search(r"<lastmod>([^<]+)</lastmod>", b)
        if loc:
            out[loc.group(1).replace(BASE, "").rstrip("/") or "/"] = (lm.group(1)[:10] if lm else None)
    return out


# ══════════════════════════ FASE A ══════════════════════════
def fase_a():
    print("\n=== FASE A · robots.txt: bots de busqueda ===")
    p = "robots.txt"
    s = io.open(p, encoding="utf-8").read()
    if "OAI-SearchBot" in s:
        print("  = ya estaban")
        return 0
    ancla = "User-agent: PerplexityBot\nAllow: /\n"
    if ancla not in s:
        print("  !! no encuentro el bloque de PerplexityBot")
        return 0
    nuevo = ancla + """
# Bots de BUSQUEDA: son los que deciden si este sitio puede aparecer en una
# respuesta de IA, y son distintos de los de entrenamiento de arriba.
# (El `User-agent: *` del principio ya los permitia; se nombran para que no
#  haya ambiguedad sobre cual bloque les aplica.)
User-agent: OAI-SearchBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Googlebot
Allow: /
"""
    guardar(p, s.replace(ancla, nuevo, 1))
    print("  + añadidos OAI-SearchBot, Claude-SearchBot y Googlebot")
    return 1


# ══════════════════════════ FASE B ══════════════════════════
def fase_b():
    print("\n=== FASE B · dateModified en el WebPage ===")
    lm = lastmods()
    n = ya = sin_lm = 0
    for p in paginas():
        h = io.open(p, encoding="utf-8", errors="replace").read()
        if '"dateModified"' in h:
            ya += 1
            continue
        m = re.search(r'(\{"@context": "https://schema\.org", "@type": "WebPage",)', h)
        if not m:
            continue
        fecha = lm.get(ruta_de(p))
        if not fecha:
            fecha = HOY
            sin_lm += 1
        h2 = h[:m.end()] + ' "dateModified": "%s",' % fecha + h[m.end():]
        guardar(p, h2)
        n += 1
    print("  + %d paginas  (ya la tenian: %d; sin lastmod en el sitemap, se usa hoy: %d)"
          % (n, ya, sin_lm))
    return n


# ══════════════════════════ FASE C ══════════════════════════
LABELS = [
    ('<input type="radio" name="metodo_pago" value="contraentrega" checked onchange="onPagoChange()">',
     '<input type="radio" name="metodo_pago" value="contraentrega" checked onchange="onPagoChange()" '
     'aria-label="Pagar contraentrega al recibir el pedido">'),
    ('<input type="radio" name="metodo_pago" value="wompi" onchange="onPagoChange()">',
     '<input type="radio" name="metodo_pago" value="wompi" onchange="onPagoChange()" '
     'aria-label="Pagar ahora en linea con tarjeta o PSE">'),
    ('<input class="ob-qty-num" id="${bump.id}-qty" type="number" value="1" min="1" max="10" readonly />',
     '<input class="ob-qty-num" id="${bump.id}-qty" type="number" value="1" min="1" max="10" readonly '
     'aria-label="Cantidad de este producto adicional" />'),
    ('<input class="ob-qty-num" id="${lineId}-qty" type="number" value="1" min="1" max="10" readonly />',
     '<input class="ob-qty-num" id="${lineId}-qty" type="number" value="1" min="1" max="10" readonly '
     'aria-label="Cantidad de este producto adicional" />'),
]


def fase_c():
    print("\n=== FASE C · aria-label en los campos sin etiqueta ===")
    tot = toc = 0
    for p in paginas():
        h = io.open(p, encoding="utf-8", errors="replace").read()
        orig, n = h, 0
        for viejo, nuevo in LABELS:
            if viejo in h:
                c = h.count(viejo)
                h = h.replace(viejo, nuevo)
                n += c
        if h != orig:
            guardar(p, h)
            toc += 1
            tot += n
    print("  + %d campos etiquetados en %d paginas" % (tot, toc))
    return tot


# ══════════════════════════ FASE D ══════════════════════════
VIDEO_ANCLA = '<video class="hero-video lazyv"'


def fase_d():
    print("\n=== FASE D · VideoObject del video del hero ===")
    lm = lastmods()
    n = ya = 0
    for p in paginas():
        h = io.open(p, encoding="utf-8", errors="replace").read()
        if VIDEO_ANCLA not in h:
            continue
        if '"VideoObject"' in h:
            ya += 1
            continue
        ruta = ruta_de(p)
        fecha = lm.get(ruta) or HOY
        nombre = re.search(r"<title>(.*?)</title>", h)
        nombre = nombre.group(1) if nombre else "Camisas Colombia"
        vo = {
            "@context": "https://schema.org", "@type": "VideoObject",
            "@id": BASE + ruta.rstrip("/") + "#hero-video",
            "name": nombre,
            "description": ("Video del producto: camisas para hombre de Camisas Colombia "
                            "en oxford, tipo lino y polo, tallas S a 5XL. Sin audio."),
            "thumbnailUrl": "https://media.paquetecompleto.com.co/landing/hero-camisa.webp",
            "contentUrl": BASE + "/video.mp4",
            "uploadDate": fecha,
            "isFamilyFriendly": True,
            "inLanguage": "es-CO",
            "publisher": {"@id": BASE + "/#organization"},
        }
        blq = ('\n<script type="application/ld+json">'
               + json.dumps(vo, ensure_ascii=False, separators=(", ", ": "))
               + "</script>")
        m = re.search(r'<link rel="canonical"[^>]*>', h)
        if not m:
            continue
        guardar(p, h[:m.end()] + blq + h[m.end():])
        n += 1
    print("  + %d paginas con VideoObject  (ya lo tenian: %d)" % (n, ya))
    return n


# ══════════════════════════ FASE E ══════════════════════════
RSS_LINK = ('<link rel="alternate" type="application/rss+xml" title="Blog de Camisas Colombia" '
            'href="/feed.xml">')


def fase_e():
    print("\n=== FASE E · feed RSS ===")
    # entradas: los blogs que siguen indexables
    posts = []
    lm = lastmods()
    for p in sorted(glob.glob("blog/*.html")):
        h = io.open(p, encoding="utf-8", errors="replace").read()
        rb = re.search(r'<meta name="robots" content="([^"]*)"', h)
        if rb and "noindex" in rb.group(1):
            continue
        t = re.search(r"<title>(.*?)</title>", h)
        de = re.search(r'<meta name="description" content="(.*?)">', h)
        ruta = ruta_de(p)
        if ruta == "/blog":
            continue
        posts.append({"ruta": ruta, "titulo": (t.group(1) if t else ruta),
                      "desc": (de.group(1) if de else ""), "fecha": lm.get(ruta) or HOY})
    posts.sort(key=lambda x: x["fecha"], reverse=True)
    esc = lambda s: (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    items = "".join(
        "  <item>\n    <title>%s</title>\n    <link>%s%s</link>\n"
        "    <guid isPermaLink=\"true\">%s%s</guid>\n    <description>%s</description>\n"
        "    <pubDate>%s</pubDate>\n  </item>\n"
        % (esc(x["titulo"]), BASE, x["ruta"], BASE, x["ruta"], esc(x["desc"]),
           time.strftime("%a, %d %b %Y 00:00:00 +0000", time.strptime(x["fecha"], "%Y-%m-%d")))
        for x in posts)
    feed = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
            '  <title>Blog de Camisas Colombia</title>\n'
            '  <link>%s/blog</link>\n'
            '  <atom:link href="%s/feed.xml" rel="self" type="application/rss+xml" />\n'
            '  <description>Guias sobre camisas para hombre en Colombia: oxford, tipo lino, '
            'tallas y cuidados.</description>\n'
            '  <language>es-CO</language>\n  <lastBuildDate>%s</lastBuildDate>\n%s</channel>\n</rss>\n'
            % (BASE, BASE, time.strftime("%a, %d %b %Y 00:00:00 +0000"), items))
    guardar("feed.xml", feed)
    print("  + feed.xml con %d entradas" % len(posts))
    n = 0
    for p in paginas():
        h = io.open(p, encoding="utf-8", errors="replace").read()
        if 'type="application/rss+xml"' in h:
            continue
        m = re.search(r'<link rel="canonical"[^>]*>', h)
        if not m:
            continue
        guardar(p, h[:m.end()] + "\n" + RSS_LINK + h[m.end():])
        n += 1
    print("  + declarado en el head de %d paginas" % n)
    return n


# ══════════════════════════ FASE F ══════════════════════════
def fase_f():
    print("\n=== FASE F · endpoints de descubrimiento para IA ===")
    ai_txt = """# ai.txt — permisos para rastreadores de IA de camisascolombia.com
# Convencion emergente (no es un estandar). Las reglas efectivas estan en
# https://www.camisascolombia.com/robots.txt

User-agent: *
Allow: /
Disallow: /gracias

# Este sitio permite a proposito los bots de busqueda de IA: aparecer en las
# respuestas de los asistentes es un canal de descubrimiento real para esta marca
# y no hay contenido que proteger de ellos.
Contact: https://wa.me/573207544636
Sitemap: https://www.camisascolombia.com/sitemap.xml
Llms-txt: https://www.camisascolombia.com/llms.txt
Llms-full-txt: https://www.camisascolombia.com/llms-full.txt
Preferred-citation: https://www.camisascolombia.com/
Last-updated: %s
""" % HOY
    guardar(".well-known/ai.txt", ai_txt)
    print("  + /.well-known/ai.txt")

    resumen = {
        "name": "Camisas Colombia",
        "url": BASE + "/",
        "description": ("Tienda online colombiana de camisas para hombre: oxford, tipo lino, "
                        "cuadros, rayas y polo, en manga corta y larga. Tallas S a 5XL con "
                        "tallaje colombiano real, pago contraentrega y envio gratis a todo el pais."),
        "inLanguage": "es-CO",
        "currency": "COP",
        "country": "CO",
        "packs": [
            {"unidades": 1, "precio_cop": 115000, "precio_por_camisa_cop": 115000},
            {"unidades": 3, "precio_cop": 295000, "precio_por_camisa_cop": 98333},
            {"unidades": 5, "precio_cop": 430000, "precio_por_camisa_cop": 86000},
        ],
        "tipos_de_camisa": ["oxford", "tipo lino", "cuadros", "rayas", "manga corta", "manga larga", "polo"],
        "tallas": ["S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL"],
        "pago": ["contraentrega (al recibir)", "tarjeta o PSE en linea"],
        "envio": {"costo": "gratis", "cobertura": "32 departamentos de Colombia",
                  "plazo_dias_habiles": "1 a 3 en ciudades principales, 3 a 6 en municipios alejados"},
        "cambios": "por talla, gratuitos, dentro de los 30 dias",
        "contacto_whatsapp": "+573207544636",
        "llms_txt": BASE + "/llms.txt",
        "sitemap": BASE + "/sitemap.xml",
        "last_updated": HOY,
    }
    guardar("ai/summary.json", json.dumps(resumen, ensure_ascii=False, indent=1) + "\n")
    print("  + /ai/summary.json")

    faqs = json.load(io.open(r"C:\tmp\faqs.json", encoding="utf-8"))
    sel = [{"question": q, "answer": re.sub(r"\s+", " ", a).strip()}
           for q, a in list(faqs.items())[:120]]
    guardar("ai/faq.json", json.dumps(
        {"name": "Camisas Colombia", "url": BASE + "/", "inLanguage": "es-CO",
         "count": len(sel), "last_updated": HOY, "faq": sel},
        ensure_ascii=False, indent=1) + "\n")
    print("  + /ai/faq.json con %d preguntas" % len(sel))
    return 3


# ══════════════════════════ FASE G ══════════════════════════
def fase_g():
    print("\n=== FASE G · llms-full.txt ===")
    faqs = json.load(io.open(r"C:\tmp\faqs.json", encoding="utf-8"))
    cuerpo = ["# Camisas Colombia — corpus completo de preguntas y respuestas",
              "",
              "> Las %d preguntas frecuentes publicadas en camisascolombia.com, tal como "
              "aparecen en el sitio. Tienda online colombiana de camisas para hombre: oxford, "
              "tipo lino, cuadros, rayas y polo, tallas S a 5XL, pago contraentrega y envio "
              "gratis a todo Colombia." % len(faqs),
              "",
              "Precios vigentes: 1 camisa $115.000 COP · 3 camisas $295.000 ($98.333 c/u) · "
              "5 camisas $430.000 ($86.000 c/u).",
              "",
              "Resumen corto: %s/llms.txt" % BASE,
              "",
              "## Preguntas y respuestas",
              ""]
    for q, a in faqs.items():
        cuerpo.append("### %s" % q.strip())
        cuerpo.append("")
        cuerpo.append(re.sub(r"\s+", " ", a).strip())
        cuerpo.append("")
    cuerpo.append("---")
    cuerpo.append("")
    cuerpo.append("Ultima actualizacion: %s" % HOY)
    txt = "\n".join(cuerpo) + "\n"
    guardar("llms-full.txt", txt)
    print("  + llms-full.txt: %d preguntas, %d bytes" % (len(faqs), len(txt.encode())))

    # declararlo en el llms.txt
    p = "llms.txt"
    s = io.open(p, encoding="utf-8").read()
    if "llms-full.txt" not in s:
        s = s.replace("- [robots.txt](%s/robots.txt)" % BASE,
                      "- [robots.txt](%s/robots.txt)\n- [Corpus completo de preguntas y respuestas]"
                      "(%s/llms-full.txt)" % (BASE, BASE), 1)
        guardar(p, s)
        print("  + declarado en llms.txt")
    return 1


def comprobar():
    print("\n=== COMPROBACIONES ===")
    ok = True
    r = io.open("robots.txt", encoding="utf-8").read()
    for b in ("OAI-SearchBot", "Claude-SearchBot", "Googlebot"):
        if b not in r:
            print("  !! falta %s en robots.txt" % b); ok = False
    print("  robots: bots de busqueda nombrados")
    # JSON-LD de todas las paginas tiene que seguir parseando
    rotos = []
    for p in paginas():
        h = io.open(p, encoding="utf-8", errors="replace").read()
        for b in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S):
            try:
                json.loads(b)
            except Exception:
                rotos.append(p); break
    print("  JSON-LD roto: %d" % len(rotos))
    for x in rotos[:5]:
        print("    %s" % x)
    ok = ok and not rotos
    # los ficheros nuevos
    for f in ("feed.xml", "llms-full.txt", ".well-known/ai.txt", "ai/summary.json", "ai/faq.json"):
        existe = os.path.exists(f)
        print("  %-24s %s" % (f, "ok" if existe else "FALTA"))
        ok = ok and existe
    for f in ("ai/summary.json", "ai/faq.json"):
        if os.path.exists(f):
            try:
                json.load(io.open(f, encoding="utf-8"))
            except Exception as e:
                print("  !! %s no es JSON valido: %s" % (f, e)); ok = False
    return ok


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = fase_a() + fase_b() + fase_c() + fase_d() + fase_e() + fase_f() + fase_g()
    ok = comprobar()
    print("\n%s" % ("(DRY-RUN: no se escribio nada)" if DRY
                    else "aplicado — backups .bak-geoopt-%s" % STAMP))
    if not ok and not DRY:
        raise SystemExit("!! comprobaciones en rojo")
