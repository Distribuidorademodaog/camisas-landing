# -*- coding: utf-8 -*-
"""
Pone en el sitemap el lastmod REAL de cada URL (fecha del ultimo commit que
toco su archivo) en vez de la fecha de la ultima ejecucion del build.

Por que importa (2026-08-14): las 84 URLs declaraban lastmod 2026-08-14, todas
la misma. Un sitemap que dice "las 84 paginas cambiaron hoy" cada vez que se
regenera entrena a Google a ignorar la senal. Y el rastreo esta claramente
degradado: la inspeccion de URL de Search Console devuelve, para las 21 paginas
de ciudad, 9 indexadas y 12 no:

    Crawled - currently not indexed  (4)  ultimo rastreo 2026-05-13
        medellin, cartagena, monteria, valledupar
    Discovered - currently not indexed (5) nunca rastreadas
        neiva, pasto, armenia, itagui, envigado
    URL is unknown to Google (3)          nunca descubiertas
        santa-marta, villavicencio, popayan

Uso:  python sitemap_lastmod_real.py [--dry-run]
"""
import io
import re
import subprocess
import sys
from datetime import date

SITEMAP = "sitemap.xml"
BASE = "https://www.camisascolombia.com"


def archivo_de(url):
    """URL -> archivo en el repo (Vercel usa cleanUrls=true)."""
    ruta = url[len(BASE):].strip("/")
    if ruta == "":
        return "index.html"
    for cand in (ruta + ".html", ruta + "/index.html"):
        if subprocess.run(["git", "ls-files", "--error-unmatch", cand],
                          capture_output=True).returncode == 0:
            return cand
    return None


def ultima_fecha(path):
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path],
                         capture_output=True, text=True).stdout.strip()
    return out or None


def main():
    dry = "--dry-run" in sys.argv
    s = io.open(SITEMAP, encoding="utf-8").read()
    hoy = date.today().isoformat()

    cambios, sin_archivo, por_fecha = 0, [], {}

    def sub(m):
        nonlocal cambios
        bloque, url = m.group(0), m.group(1)
        f = archivo_de(url)
        if not f:
            sin_archivo.append(url)
            return bloque
        fecha = ultima_fecha(f) or hoy
        por_fecha[fecha] = por_fecha.get(fecha, 0) + 1
        nuevo, n = re.subn(r"<lastmod>[^<]*</lastmod>",
                           "<lastmod>%s</lastmod>" % fecha, bloque, count=1)
        if n and nuevo != bloque:
            cambios += 1
        return nuevo

    s2 = re.sub(r"<url>\s*<loc>([^<]+)</loc>.*?</url>", sub, s, flags=re.S)

    if sin_archivo:
        print("!! URLs del sitemap sin archivo en el repo (%d):" % len(sin_archivo))
        for u in sin_archivo:
            print("     " + u)
    print("lastmod actualizados: %d" % cambios)
    print("distribucion de fechas:")
    for f, n in sorted(por_fecha.items()):
        print("   %s  %2d URLs" % (f, n))

    if not dry:
        io.open(SITEMAP, "w", encoding="utf-8", newline="").write(s2)
        print("\n%s escrito" % SITEMAP)
    else:
        print("\nDRY-RUN: no se escribio nada")


if __name__ == "__main__":
    main()
