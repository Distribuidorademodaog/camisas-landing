# -*- coding: utf-8 -*-
"""
Resincroniza las fuentes de _landings/ con el HTML desplegado — 2026-09-04.

El problema: las landings se generan con build_landings.py desde
_landings/<slug>.meta.json + <slug>.section.html, pero desde agosto los titles,
descriptions y varios enlaces se reescribieron DIRECTAMENTE sobre el HTML
(seo_titles_2026_08.py, seo_ctr_2026_08_27.py, seo_pilar_*.py...). Las fuentes
se quedaron atras. Medido antes de correr esto, sobre 26 landings:

    faqs                    0  (falsa alarma: el formato del bloque cambio)
    meta_description       22
    title                  19
    breadcrumb_name         6
    section.html            6
    og_title                5
    og_description          2
    twitter_title / desc    2

Los 6 section.html desfasados son los peligrosos: tres apuntan a URLs que ya
NO existen y estan en 301 —  /camisetas-polo-hombre (fusionada) y, peor,
/camisas-polo-ralph-lauren-colombia (el slug PRE de-branding). Regenerar desde
esas fuentes reintroducia enlaces a la marca ajena en el sitio.

Que hace: para cada landing con HTML desplegado, reescribe su meta.json y su
section.html con lo que HAY EN PRODUCCION. El HTML es la verdad; la fuente se
adapta, nunca al reves.

Aparte: _landings/camisetas-polo-hombre.* queda huerfano (esa pagina se fusiono
con la pilar y su HTML se borro, hay 301 en vercel.json). Como build_landings.py
sin argumentos recorre *.meta.json, regenerarla RESUCITARIA la pagina fusionada.
Se aparta renombrandola, no se borra.

Uso:  python sincronizar_landings_2026_09_04.py [--dry-run]
"""
import glob
import io
import json
import os
import re
import sys

CARRUSEL = "  <!-- ═══════ CARRUSEL ═══════ -->"
FUSIONADA = "camisetas-polo-hombre"   # 301 -> /camisas-polo-premium-colombia
MODULO = re.compile(r'\n<style>\n\.cc-relacionados\{.*?</nav>\n(?=</body>)', re.S)
LEAD = re.compile(r'<p class="sec-subtitle sec-subtitle-light" itemprop="description">.*?</p>', re.S)


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
    raise SystemExit("!! corchete sin cerrar")


def uno(pat, h, label, grupo=1):
    m = re.search(pat, h, re.S)
    if not m:
        raise SystemExit("!! [%s] no encontrado" % label)
    return m.group(grupo)


def leer_html(h):
    """Extrae del HTML desplegado exactamente los campos que escribe el build."""
    d = {
        "title": uno(r"<title>(.*?)</title>", h, "title"),
        "meta_description": uno(r'<meta name="description" content="(.*?)">', h, "desc"),
        "keywords": uno(r'<meta name="keywords" content="(.*?)">', h, "keywords"),
        "og_title": uno(r'<meta property="og:title" content="(.*?)">', h, "og:title"),
        "og_description": uno(r'<meta property="og:description" content="(.*?)">', h, "og:desc"),
        "twitter_title": uno(r'<meta name="twitter:title" content="(.*?)">', h, "tw:title"),
        "twitter_description": uno(r'<meta name="twitter:description" content="(.*?)">', h, "tw:desc"),
        "hero_eyebrow": uno(r'<div class="hero-eyebrow">(.*?)</div>', h, "eyebrow"),
    }
    m = re.search(r'<h1 class="hero-title"><span style="[^"]*">(.*?)</span>(.*?)</h1>', h, re.S)
    if not m:
        raise SystemExit("!! [h1] no encontrado")
    d["hero_h1_sr"], d["hero_h1_visible"] = m.group(1), m.group(2)

    w = re.search(r'"@type": "WebPage".*?"name": "([^"]*)".*?"description": "([^"]*)"', h, re.S)
    if not w:
        raise SystemExit("!! [webpage] no encontrado")
    d["webpage_name"], d["webpage_description"] = w.group(1), w.group(2)

    # breadcrumb: la hoja del BreadcrumbList, no cualquier "position": 3
    bc = re.search(r'\{"@context": "https://schema\.org", "@type": "BreadcrumbList".*?\}\]\}', h, re.S)
    if not bc:
        raise SystemExit("!! [breadcrumb] no encontrado")
    d["breadcrumb_name"] = json.loads(bc.group(0))["itemListElement"][-1]["name"]

    # FAQPage: bloque en una linea, se lee con conteo de corchetes
    fm = re.search(r'"@type": "FAQPage", "mainEntity": ', h)
    if not fm:
        raise SystemExit("!! [faqpage] no encontrado")
    ini = fm.end()
    ents = json.loads(h[ini:fin_corchete(h, ini) + 1])
    d["faqs"] = [{"q": e["name"], "a": e["acceptedAnswer"]["text"]} for e in ents]

    # Modulo "cc-relacionados" (css + nav), pegado justo antes de </body>. Lo
    # inyecta el script de enlazado interno DESPUES del build y es DISTINTO en
    # cada pagina: 14 landings lo tienen, 12 no. Sin guardarlo, regenerar le
    # copiaba a todas el de la pilar.
    mod = MODULO.search(h)
    d["related_module"] = mod.group(0) if mod else None

    # Entradilla del hero: viene de la plantilla, pero 3 landings llevan dentro
    # un enlace a la pilar que les puso seo_pilar_2026_08_27.py.
    lead = LEAD.search(h)
    d["hero_lead"] = lead.group(0) if lead else None

    sec = re.search(r'  <section class="sec sec-light" id="[^"]*">.*?(?=\n\n'
                    + re.escape(CARRUSEL) + r')', h, re.S)
    if not sec:
        raise SystemExit("!! [section] no encontrada")
    d["_section"] = sec.group(0)
    return d


def main():
    dry = "--dry-run" in sys.argv
    cambiados = 0
    for p in sorted(glob.glob("_landings/*.meta.json")):
        slug = os.path.basename(p)[:-10]
        html_p = slug + ".html"
        if slug == FUSIONADA or not os.path.exists(html_p):
            continue
        viv = leer_html(io.open(html_p, encoding="utf-8").read())
        sec_nueva = viv.pop("_section")

        meta = json.load(io.open(p, encoding="utf-8"))
        difs = [k for k, v in viv.items() if meta.get(k) != v]
        sec_p = "_landings/%s.section.html" % slug
        sec_vieja = io.open(sec_p, encoding="utf-8").read().rstrip()
        sec_dif = sec_vieja != sec_nueva

        if not difs and not sec_dif:
            continue
        cambiados += 1
        print("%-40s %s%s" % (slug, ", ".join(difs) or "-",
                              "  +section" if sec_dif else ""))
        if dry:
            continue
        meta.update(viv)
        io.open(p, "w", encoding="utf-8", newline="").write(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
        if sec_dif:
            io.open(sec_p, "w", encoding="utf-8", newline="").write(sec_nueva + "\n")

    # apartar la landing fusionada para que el build no la resucite
    huerfanos = glob.glob("_landings/%s.*" % FUSIONADA)
    huerfanos = [f for f in huerfanos if not f.endswith(".fusionada-301")]
    for f in huerfanos:
        print("aparto huerfano: %s -> %s.fusionada-301" % (f, f))
        if not dry:
            os.rename(f, f + ".fusionada-301")

    print("\n%d landings resincronizadas%s" % (cambiados,
          " (DRY-RUN, no se escribio nada)" if dry else ""))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
