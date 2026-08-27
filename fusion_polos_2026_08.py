# -*- coding: utf-8 -*-
"""
Fusion de las dos paginas sinonimas de la pilar — 2026-08-27.

Motivo (datos GSC 28 abr - 25 ago 2026):
  * En la consulta "camisas polo" compiten OCHO paginas propias, todas entre la
    posicion 39 y la 68. Ninguna es la pilar. Google no sabe cual servir.
  * /camisetas-polo-hombre es sinonimo de /camisas-polo-premium-colombia y
    Google NUNCA la ha rastreado pese a llevar meses en el sitemap: ya decidio
    que no aporta nada nuevo. Insistir en indexarla seria pedirle a Google que
    indexe dos veces lo mismo. Se fusiona con 301 hacia la pilar.
  * /polos-hombre-colombia NO se fusiona: el 26 de agosto paso a "Enviada e
    indexada" tras el envio a la Indexing API. Borrar una pagina que Google
    acaba de aceptar seria tirar el activo. Se deja y se diferencia por titulo,
    y se le anade enlace a la pilar con ancla "camisas polo" para que la
    jerarquia quede explicita.

Que hace:
  1. 301 permanentes en vercel.json hacia /camisas-polo-premium-colombia.
  2. Reescribe los enlaces internos que apuntaban a ellas.
  3. Las saca del sitemap.
  4. Borra los dos HTML.

Uso:  python fusion_polos_2026_08.py [--dry-run]
"""
import json
import os
import re
import sys

DRY = "--dry-run" in sys.argv
BASE = "https://www.camisascolombia.com"
DESTINO = "/camisas-polo-premium-colombia"
FUERA = ["camisetas-polo-hombre"]

SKIP = {"_blog", "_cities", "_landings", "output", "src", ".git", "node_modules"}


def html_files():
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in sorted(files):
            if f.endswith(".html"):
                yield os.path.join(root, f).replace("\\", "/").lstrip("./")


def main():
    # ---- 1. redirects en vercel.json ---------------------------------------
    vj = json.load(open("vercel.json", encoding="utf-8"))
    existentes = {r["source"] for r in vj.get("redirects", [])}
    nuevos = 0
    for slug in FUERA:
        src = "/" + slug
        if src in existentes:
            continue
        vj.setdefault("redirects", []).append({
            "source": src, "destination": DESTINO, "permanent": True})
        nuevos += 1
    if not DRY and nuevos:
        json.dump(vj, open("vercel.json", "w", encoding="utf-8", newline=""),
                  ensure_ascii=False, indent=2)
    print("1. vercel.json: %d redirects 301 anadidos" % nuevos)

    # ---- 2. enlaces internos ------------------------------------------------
    tocados = 0
    for f in html_files():
        if f[:-5] in FUERA:
            continue
        h = open(f, encoding="utf-8").read()
        orig = h
        for slug in FUERA:
            # href="/slug"  href="/slug.html"  href="https://.../slug"
            h = re.sub(r'href="(?:%s)?/%s(?:\.html)?"' % (re.escape(BASE), re.escape(slug)),
                       'href="%s"' % DESTINO, h)
        if h != orig:
            tocados += 1
            if not DRY:
                open(f, "w", encoding="utf-8", newline="").write(h)
    print("2. enlaces internos reescritos en %d archivos" % tocados)

    # ---- 3. sitemap ---------------------------------------------------------
    sm = open("sitemap.xml", encoding="utf-8").read()
    antes = len(re.findall(r"<url>", sm))
    for slug in FUERA:
        sm = re.sub(r"\s*<url>(?:(?!</url>).)*?<loc>%s/%s</loc>.*?</url>"
                    % (re.escape(BASE), re.escape(slug)), "", sm, flags=re.S)
    despues = len(re.findall(r"<url>", sm))
    if not DRY:
        open("sitemap.xml", "w", encoding="utf-8", newline="").write(sm)
    print("3. sitemap: %d -> %d URLs" % (antes, despues))

    # ---- 4. borrar los HTML -------------------------------------------------
    for slug in FUERA:
        p = slug + ".html"
        if os.path.exists(p):
            if not DRY:
                os.remove(p)
            print("4. borrado %s" % p)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
