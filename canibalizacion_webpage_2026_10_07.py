# -*- coding: utf-8 -*-
"""
Completa el arreglo de canibalizacion: el WebPage.name de las ciudades — 2026-10-07.

canibalizacion_2026_10_07.py cambio el H1 de las 36 ciudades, pero el `name` del
nodo WebPage del JSON-LD seguia llevando el H1 VIEJO: las mismas 36 paginas seguian
declarandose «Camisas Polo para Hombre estilo clasico en Colombia» ante Google, en
el campo que mas peso tiene para decir de que es la pagina. Verificado en vivo
sobre /camisas-polo-bogota despues del deploy: el H1 ya decia Bogota y el schema
no.

Es el mismo patron que ya costo caro antes: cambiar el texto visible y dejar la
copia del schema apuntando al termino anterior deja el bug vivo con otra cara.

El `<title>` y el `og:title` de cada ciudad SI eran especificos y estan bien
escritos, asi que el WebPage.name se iguala al title de la propia pagina — que es
lo que hacen las 25 landings generadas (ahi `webpage_name` es un campo propio).

Comprobaciones: 1 solo nodo WebPage por archivo, el name actual tiene que ser uno
de los dos genericos conocidos, y el JSON-LD tiene que seguir parseando despues.

Uso:  python canibalizacion_webpage_2026_10_07.py [--dry-run]
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

GENERICOS = {
    "Camisas Polo para Hombre estilo clásico en Colombia con Pago Contraentrega y "
    "Envío Gratis. Vístete bien. Paga al llegar.",
    "Camisas Polo para Hombre Estilo Premium en Colombia con Pago Contraentrega y "
    "Envío Gratis. Vístete bien. Paga al llegar.",
}
WP_RE = re.compile(r'("@type": "WebPage".*?"name": ")(.*?)(")', re.S)


def bloques_jsonld(h):
    return re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S)


def main():
    files = [f for f in sorted(glob.glob("camisas-polo-*.html"))
             if not re.search(r"-(hombre|colombia)\.html$", f)]
    print("paginas de ciudad: %d\n" % len(files))
    hechas = saltadas = 0
    for f in files:
        h = io.open(f, encoding="utf-8").read()
        ms = WP_RE.findall(h)
        if len(ms) != 1:
            print("  !! %-36s %d nodos WebPage, esperaba 1 — SIN TOCAR" % (f, len(ms)))
            continue
        actual = ms[0][1]
        ti = re.search(r"<title>(.*?)</title>", h)
        if not ti:
            print("  !! %-36s sin <title> — SIN TOCAR" % f)
            continue
        nuevo = ti.group(1)
        if actual == nuevo:
            print("  =  %-36s ya aplicado" % f)
            saltadas += 1
            continue
        if actual not in GENERICOS:
            print("  !! %-36s name inesperado, SIN TOCAR: %s" % (f, actual[:60]))
            continue
        if '"' in nuevo or "\\" in nuevo:
            print("  !! %-36s el title tiene comillas, rompería el JSON — SIN TOCAR" % f)
            continue
        h2 = WP_RE.sub(lambda m: m.group(1) + nuevo + m.group(3), h, count=1)
        assert h2 != h, f
        # el JSON-LD tiene que seguir parseando
        roto = [i for i, b in enumerate(bloques_jsonld(h2))
                if not _parsea(b)]
        if roto:
            print("  !! %-36s el JSON-LD quedaría roto (bloque %s) — SIN TOCAR" % (f, roto))
            continue
        if not DRY:
            shutil.copy(f, f + ".bak-wp-" + STAMP)
            tmp = f + ".tmp"
            io.open(tmp, "w", encoding="utf-8", newline="").write(h2)
            os.replace(tmp, f)
        print("  +  %-36s %s" % (f, nuevo[:62]))
        hechas += 1

    print("\n  %d reescritas, %d ya estaban, %d sin tocar"
          % (hechas, saltadas, len(files) - hechas - saltadas))

    print("\n=== COMPROBACION ===")
    quedan = []
    for f in sorted(glob.glob("*.html")):
        h = io.open(f, encoding="utf-8").read()
        for g in GENERICOS:
            if g in h:
                quedan.append(f)
                break
    print("  paginas que todavía declaran el término nacional: %d" % len(quedan))
    for q in quedan:
        print("    %s" % q)
    if not quedan:
        print("  OK — ni el H1 ni el schema de ninguna ciudad reclaman «camisas polo para hombre»")
    print("\n%s" % ("(DRY-RUN: no se escribió nada)" if DRY
                    else "aplicado — backups .bak-wp-%s" % STAMP))


def _parsea(b):
    try:
        json.loads(b)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
