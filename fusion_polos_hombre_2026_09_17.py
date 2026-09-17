# -*- coding: utf-8 -*-
"""
Fusion de /polos-hombre-colombia en la pilar + limpieza de camisas-hombre-colombia
— 2026-09-17.

Motivo (GSC 19 ago - 15 sep 2026, dimension query+page):
  * «polos para hombre», «polos hombre», «camisas polo», «camisa polo»… (750
    impresiones, posicion media 52) se reparten entre CINCO paginas propias y
    la pilar reescrita el 10-sep no aparece para ninguna.
  * /polos-hombre-colombia es la duplicada por diseno: title «Polos Hombre
    Colombia | Camisas Polo de Moda desde $86.000», 348 impresiones en
    posicion 69 y 0 clics. El 27-ago se dejo viva porque acababa de entrar al
    indice; tres semanas despues ya se ve que solo divide la senal.
  * Se fusiona con 301 hacia /camisas-polo-premium-colombia, que es la cabeza
    del cluster. Los 15 enlaces internos que la apuntaban (ancla «Polos para
    hombre») pasan a la pilar: es exactamente el ancla que la pilar necesita.

Ademas, /camisas-hombre-colombia (la que mas impresiones captura del termino
cabeza, 564) arrastraba restos del de-branding: «polos premium estilo premium»,
«tallas S a 3XL» (son S a 5XL), «packs de 3 y 6» (el pack es de 5 desde el
16-sep; lo protegio el centinela «3 y 6» de plazos) y un «..  clientes.» roto en
el JSON-LD. Lo mismo «estilo premium estilo premium» en 8 ciudades.

Uso:  python fusion_polos_hombre_2026_09_17.py [--dry-run]
"""
import glob
import io
import json
import os
import re
import sys

DRY = "--dry-run" in sys.argv
BASE = "https://www.camisascolombia.com"
FUERA = "polos-hombre-colombia"
PILAR = "/camisas-polo-premium-colombia"


def paginas():
    return sorted(set(p.replace(os.sep, "/") for p in
                  glob.glob("*.html") + glob.glob("blog/*.html") + glob.glob("guias/*.html")))


def escribir(f, h):
    if not DRY:
        io.open(f, "w", encoding="utf-8", newline="").write(h)


def main():
    # 1. redirect 301
    vj = json.load(io.open("vercel.json", encoding="utf-8"))
    if not any(r.get("source") == "/" + FUERA for r in vj["redirects"]):
        vj["redirects"].append({"source": "/" + FUERA, "destination": PILAR, "permanent": True})
        if not DRY:
            io.open("vercel.json", "w", encoding="utf-8", newline="").write(
                json.dumps(vj, ensure_ascii=False, indent=2))
    print("1. redirect /%s -> %s" % (FUERA, PILAR))

    # 2. enlaces internos: hacia la pilar; sin duplicar en cc-relacionados; sin autoenlace
    tocados = quitados = 0
    for f in paginas():
        if f == FUERA + ".html":
            continue
        h = io.open(f, encoding="utf-8").read()
        orig = h
        es_pilar = (f == PILAR.strip("/") + ".html")
        if es_pilar:
            # en la pilar el enlace seria un autoenlace: se desenlaza (queda el texto)
            h, n = re.subn(r'<a href="/%s"[^>]*>(.*?)</a>' % FUERA, r"\1", h, flags=re.S)
            quitados += n
        h = re.sub(r'href="(?:%s)?/%s(?:\.html)?"' % (re.escape(BASE), FUERA), 'href="%s"' % PILAR, h)
        # dedupe: dentro de cada <ul> de cc-relacionados, un solo <li> hacia la pilar
        def dedupe(m):
            ul = m.group(0)
            lis = re.findall(r"\s*<li>.*?</li>", ul, re.S)
            dup = [li for li in lis if 'href="%s"' % PILAR in li]
            if len(dup) < 2:
                return ul
            for li in dup[1:]:
                ul = ul.replace(li, "", 1)
            return ul
        h = re.sub(r'<nav class="cc-relacionados"[^>]*>.*?</nav>', dedupe, h, flags=re.S)
        if h != orig:
            tocados += 1
            escribir(f, h)
    print("2. enlaces reescritos en %d paginas (%d desenlazados en la pilar)" % (tocados, quitados))

    # 3. sitemap
    sm = io.open("sitemap.xml", encoding="utf-8").read()
    antes = sm.count("<url>")
    sm = re.sub(r"\s*<url>(?:(?!</url>).)*?<loc>%s/%s</loc>.*?</url>" % (re.escape(BASE), FUERA), "", sm, flags=re.S)
    if not DRY:
        io.open("sitemap.xml", "w", encoding="utf-8", newline="").write(sm)
    print("3. sitemap %d -> %d URLs" % (antes, sm.count("<url>")))

    # 4. borrar html + apartar las fuentes (un build sin argumentos la resucitaria)
    if not DRY:
        if os.path.exists(FUERA + ".html"):
            os.remove(FUERA + ".html")
        for ext in (".meta.json", ".section.html"):
            src = os.path.join("_landings", FUERA + ext)
            if os.path.exists(src):
                os.replace(src, src + ".fusionada-301")
    print("4. %s.html borrado; fuentes apartadas a .fusionada-301" % FUERA)

    # 5. restos de texto en camisas-hombre-colombia y ciudades
    R = [
        ("polos premium estilo premium", "camisas polo estilo premium"),
        ("Camisas polo premium estilo premium", "Camisas polo estilo premium"),
        ("tallas S a 3XL", "tallas S a 5XL"),
        ("packs de 3 y 6", "packs de 3 y 5"),
        ("a todo el pais..  clientes.", "a todo el pais."),
    ]
    for f in paginas():
        h = io.open(f, encoding="utf-8").read()
        orig = h
        for v, n in R:
            h = h.replace(v, n)
        if h != orig:
            print("   5. %s: %s" % (f, ", ".join("%s x%d" % (v[:28], orig.count(v)) for v, _ in R if v in orig)))
            escribir(f, h)
    print("\n%s" % ("(DRY-RUN)" if DRY else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
