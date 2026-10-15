# -*- coding: utf-8 -*-
"""
Segunda pasada del audit de GEO Optimizer: 81 -> ? — 2026-10-15.

La primera pasada subio 75 -> 81 cerrando `signals`, `llms` y `ai_discovery`.
Al abrir el detalle de los checks que NO se movieron aparecio un defecto real que
no se veia desde fuera, y que es lo que arregla esta pasada.

── FASE A · el H1 se lee como un churro: «Vístetebien.Paga alllegar.» ─────────

🚨 Esto es lo importante de toda la auditoria. El H1 del hero es:

    <h1><span oculto>…texto SEO…</span>Vístete<br>bien.<br><em>Paga al<br>llegar.</em></h1>

Los `<br>` no llevan espacio delante, asi que **cualquier extractor de texto —y eso
incluye a los motores de IA— lee «Vístetebien.Paga alllegar.»**, con las palabras
pegadas. El audit lo delata en `names_found`:

    "…con pago contraentrega y envío gratis.Vístetebien.Paga alllegar."

Afecta a **70 variantes de H1 en 103 paginas** («Ni de mas,<br>ni de<br>menos.»,
«Manga<br>corta,<br>…», etc.). Se arregla metiendo un espacio ANTES de cada `<br>`
dentro del h1: el navegador colapsa ese espacio al final de la linea, asi que
**no cambia como se ve**, y el texto extraido queda correcto.

── FASE B · el nombre de la marca no estaba en el H1 ──────────────────────────

`brand_name_consistent: false` con `primary_name: "Camisas Colombia"`. El title
dice «Camisas Polo para Hombre en Colombia» y el H1 no nombra la marca, asi que un
motor no tiene de donde sacar la entidad. Se añade al final del texto SEO del H1.

── FASE C · la descripcion del schema no coincidia con la meta ────────────────

`schema_desc_matches_meta: false`. Se iguala la `description` del WebPage a la
meta description de la propia pagina.

── FASE D · hreflang ──────────────────────────────────────────────────────────

`has_hreflang: false`. El sitio es monolingue y apunta a Colombia: se añade el
hreflang autorreferente `es-co` mas `x-default`, que es lo correcto para eso.

── FASE E · robots: los bots de citacion, explicitos ──────────────────────────

`citation_bots_ok: true` pero `citation_bots_explicit: false`: el audit detecta a
los 16 bots como permitidos por el comodin, y quiere un bloque propio para cada
uno. Se añaden.

⚠️ Otra vez: **no les abre nada**, ya tenian acceso por `User-agent: *`. Es
documentar la politica de forma explicita. Incluye a `Google-Extended`, que
gobierna el uso para entrenar Gemini — consistente con la postura que el propio
robots.txt ya declara por escrito en este sitio.

── FASE F · /ai/service.json ──────────────────────────────────────────────────

El ultimo punto de `ai_discovery`.

── Lo que sigue SIN hacerse, y por que ────────────────────────────────────────

🚫 **`has_webapp: false` (2 puntos de `schema`).** Pide un schema
`WebApplication`. Esto es una tienda de camisas: declararla aplicacion web seria
falso. No se toca.

🚫 **`has_about_link: false`.** Pide una pagina /nosotros o /about visible. No se
crea: **el sitio no tiene `<footer>`**, asi que la pagina nacería huerfana; el
presupuesto de rastreo esta agotado (mediana 21 dias); y una pagina «quienes
somos» honesta necesita datos que solo tiene el negocio. Queda propuesto.

🚫 **Wikipedia / Wikidata / LinkedIn / Crunchbase** (`kg_pillar_count: 0`). No
aplican a una tienda de este tamaño, y no se inventan.

🚫 **Keyword stuffing y «hidden text = cloaking»**: ver el encabezado de
geo_optimizer_2026_10_15.py.

Uso:  python geo_optimizer2_2026_10_15.py [--dry-run]
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
MARCA = " — Camisas Colombia"

CITATION_BOTS = [
    ("ChatGPT-User", "ChatGPT cuando un usuario pide abrir un enlace"),
    ("OAI-SearchBot", "indice de busqueda de ChatGPT"),
    ("GPTBot", "entrenamiento de OpenAI"),
    ("Claude-SearchBot", "indice de busqueda de Claude"),
    ("Claude-User", "Claude cuando un usuario pide abrir un enlace"),
    ("ClaudeBot", "entrenamiento de Anthropic"),
    ("PerplexityBot", "indice de Perplexity"),
    ("Perplexity-User", "Perplexity abriendo un enlace a peticion del usuario"),
    ("Googlebot", "Google Search, que alimenta los AI Overviews"),
    ("Google-Extended", "uso para entrenar y fundamentar Gemini"),
    ("Google-CloudVertexBot", "Vertex AI"),
    ("Bingbot", "Bing, que es el indice del que recuperan ChatGPT y Copilot"),
    ("Applebot-Extended", "Apple Intelligence"),
    ("DuckAssistBot", "DuckDuckGo AI"),
    ("cohere-ai", "Cohere"),
    ("Bytespider", "ByteDance"),
]


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
        shutil.copy(path, path + ".bak-geo2-" + STAMP)
    tmp = path + ".tmp"
    io.open(tmp, "w", encoding="utf-8", newline="").write(texto)
    os.replace(tmp, path)


H1 = re.compile(r"(<h1\b[^>]*>)(.*?)(</h1>)", re.S)


def fases_abcd():
    print("\n=== FASES A-D sobre las paginas ===")
    n_br = n_marca = n_desc = n_hl = 0
    toc = 0
    for p in paginas():
        h = io.open(p, encoding="utf-8", errors="replace").read()
        orig = h

        # ── A · espacio antes de cada <br> dentro del h1 ──────────────────
        def arregla_h1(m):
            cuerpo = m.group(2)
            nuevo = re.sub(r"(?<![\s>])<br\s*/?>", " <br>", cuerpo)
            return m.group(1) + nuevo + m.group(3)
        h2 = H1.sub(arregla_h1, h)
        if h2 != h:
            n_br += 1
            h = h2

        # ── B · la marca, al final del texto SEO del h1 ───────────────────
        m = re.search(r'(border:0;">)(.*?)(</span>)', h, re.S)
        if m and MARCA not in m.group(2):
            txt = m.group(2).rstrip()
            sep = "" if txt.endswith((".", "!", "?")) else "."
            h = h[:m.start(2)] + txt + sep + MARCA + "." + h[m.end(2):]
            n_marca += 1

        # ── C · description del WebPage = meta description ────────────────
        md = re.search(r'<meta name="description" content="(.*?)">', h)
        if md:
            meta = md.group(1)
            wp = re.search(r'("@type": "WebPage",(?:[^{}]|\{[^{}]*\})*?"description": ")(.*?)(")', h, re.S)
            if wp and wp.group(2) != meta and '"' not in meta and "\\" not in meta:
                h = h[:wp.start(2)] + meta + h[wp.end(2):]
                n_desc += 1

        # ── D · hreflang autorreferente ───────────────────────────────────
        if 'hreflang="es-co"' not in h:
            mc = re.search(r'<link rel="canonical" href="([^"]+)"[^>]*>', h)
            if mc:
                u = mc.group(1)
                bloque = ('\n<link rel="alternate" hreflang="es-co" href="%s">'
                          '\n<link rel="alternate" hreflang="x-default" href="%s">' % (u, u))
                h = h[:mc.end()] + bloque + h[mc.end():]
                n_hl += 1

        if h != orig:
            guardar(p, h)
            toc += 1
    print("  A  espacio antes de <br> en el h1 : %d paginas" % n_br)
    print("  B  marca añadida al h1           : %d paginas" % n_marca)
    print("  C  description del WebPage = meta: %d paginas" % n_desc)
    print("  D  hreflang es-co + x-default    : %d paginas" % n_hl)
    print("  (%d archivos tocados)" % toc)
    return toc


def fase_e():
    print("\n=== FASE E · robots.txt: bots de citacion explicitos ===")
    p = "robots.txt"
    s = io.open(p, encoding="utf-8").read()
    if "Bytespider" in s:
        print("  = ya estaban")
        return 0
    # se reemplaza el bloque de bots por la lista completa
    ini = s.find("# Bots de IA:")
    fin = s.find("Sitemap:")
    if ini < 0 or fin < 0:
        print("  !! no encuentro los limites del bloque de bots")
        return 0
    nuevo = ["""# ───────── Rastreadores de IA ─────────
# Se permiten TODOS a proposito: aparecer en las respuestas de los asistentes es
# un canal de descubrimiento real para esta marca y no hay contenido que proteger.
# Ya estaban permitidos por el `User-agent: *` de arriba; se nombran uno a uno
# para que la politica quede explicita y sin ambiguedad sobre que bloque aplica.
"""]
    for bot, para in CITATION_BOTS:
        nuevo.append("# %s — %s\nUser-agent: %s\nAllow: /\n" % (bot, para, bot))
    guardar(p, s[:ini] + "\n".join(nuevo) + "\n" + s[fin:])
    print("  + %d bots nombrados explicitamente" % len(CITATION_BOTS))
    return 1


def fase_f():
    print("\n=== FASE F · /ai/service.json ===")
    srv = {
        "name": "Camisas Colombia",
        "url": BASE + "/",
        "serviceType": "Venta online de camisas para hombre con pago contraentrega",
        "provider": {"name": "Camisas Colombia", "url": BASE + "/", "@id": BASE + "/#organization"},
        "areaServed": {"country": "CO", "detail": "los 32 departamentos de Colombia"},
        "availableLanguage": ["es-CO"],
        "capabilities": [
            {"name": "Comprar camisas por pack",
             "description": "Packs de 1, 3 o 5 camisas; el precio por camisa baja al crecer el pack.",
             "url": BASE + "/pack-camisas-polo-hombre"},
            {"name": "Elegir tipo de camisa",
             "description": "Oxford, tipo lino, cuadros, rayas y polo, en manga corta o larga.",
             "url": BASE + "/camisas-hombre-colombia"},
            {"name": "Consultar la tabla de tallas",
             "description": "Medidas reales en centimetros de la S a la 5XL, espalda y pecho.",
             "url": BASE + "/tallas-de-camisas-hombre-colombia"},
            {"name": "Pagar contraentrega",
             "description": "No se paga nada por adelantado: se paga al recibir, en efectivo, "
                            "Nequi, Daviplata o transferencia."},
            {"name": "Cambiar la talla",
             "description": "Cambio por talla gratuito dentro de los 30 dias siguientes a la compra."},
        ],
        "offers": {"currency": "COP", "packs": [
            {"unidades": 1, "precio": 115000}, {"unidades": 3, "precio": 295000},
            {"unidades": 5, "precio": 430000}]},
        "shipping": {"cost": "gratis", "leadTimeBusinessDays": "1-3 ciudades principales, 3-6 municipios alejados"},
        "contact": {"whatsapp": "+573207544636"},
        "last_updated": HOY,
    }
    guardar("ai/service.json", json.dumps(srv, ensure_ascii=False, indent=1) + "\n")
    print("  + /ai/service.json")
    return 1


def comprobar():
    print("\n=== COMPROBACIONES ===")
    ok = True
    # ningun h1 puede dejar palabras pegadas
    malas = []
    for p in paginas():
        h = io.open(p, encoding="utf-8", errors="replace").read()
        for m in H1.finditer(h):
            if re.search(r"[^\s>]<br", m.group(2)):
                malas.append(p)
                break
    print("  h1 con <br> sin espacio delante: %d" % len(malas))
    for x in malas[:5]:
        print("    %s" % x)
    ok = ok and not malas
    # el texto extraido del h1 de la portada
    h = io.open("index.html", encoding="utf-8").read()
    m = H1.search(h)
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
    print("\n  h1 de la portada, como lo lee una maquina:")
    print("    «...%s»" % txt[-96:])
    print("    contiene «Camisas Colombia»: %s" % ("si" if "Camisas Colombia" in txt else "NO"))
    ok = ok and "Camisas Colombia" in txt
    # JSON-LD
    rotos = []
    for p in paginas():
        hh = io.open(p, encoding="utf-8", errors="replace").read()
        for b in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', hh, re.S):
            try:
                json.loads(b)
            except Exception:
                rotos.append(p)
                break
    print("\n  JSON-LD roto: %d" % len(rotos))
    for x in rotos[:5]:
        print("    %s" % x)
    ok = ok and not rotos
    for f in ("ai/service.json",):
        print("  %-20s %s" % (f, "ok" if os.path.exists(f) else "FALTA"))
        ok = ok and os.path.exists(f)
    r = io.open("robots.txt", encoding="utf-8").read()
    print("  robots: %d bloques User-agent" % r.count("User-agent:"))
    return ok


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    fases_abcd()
    fase_e()
    fase_f()
    ok = comprobar()
    print("\n%s" % ("(DRY-RUN: no se escribio nada)" if DRY
                    else "aplicado — backups .bak-geo2-%s" % STAMP))
    if not ok and not DRY:
        raise SystemExit("!! comprobaciones en rojo")
