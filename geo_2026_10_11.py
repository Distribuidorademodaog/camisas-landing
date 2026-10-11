# -*- coding: utf-8 -*-
"""
Mejoras de GEO (visibilidad en asistentes de IA) — 2026-10-11.

Por que aqui: este sitio YA gana en el canal de IA. ChatGPT lo cita en 5 de 5
respuestas, Perplexity en 4 de 5, y es el dominio mas citado del conjunto (9
citas, por delante de Dafiti y Mercado Libre). Bing — que es el indice del que
recuperan ChatGPT y Copilot — tiene 104 paginas y rastrea 19-51 al dia, contra
las 82 de Google con mediana de 21 dias. Es el unico canal donde el sitio va
primero, y estaba desatendido.

── FASE A · el pack de 6 ya no existe: es un pack de 5 a $430.000 ─────────────

🚨 Lo mas grave de todo. La home ya estaba bien («5 Camisas», $86.000 por
camisa), pero DOS paginas seguian anunciando un pack de **6** al precio del de 5.
La aritmetica lo delata: 430.000/6 = 71.666, y el sitio dice 86.000, que es
430.000/5. O sea que la cantidad es el dato viejo y el precio es el bueno.

Un cliente que pidiera esperando 6 camisas por $430.000 recibe 5. Son 11
apariciones en title, og:title, og:description, twitter:description, el `name` y
la `description` del WebPage, y el cuerpo:

    pack-camisas-polo-hombre.html     9
    camisas-polo-colores-hombre.html  2

── FASE B · el llms.txt estaba dando un precio equivocado ─────────────────────

El sitio tiene un `/llms.txt` publicado (el fichero que leen los asistentes) y
estaba peor que desactualizado:

  - decia **$495.000 por 6 camisas**; son **$430.000 por 5**
  - decia «ahorras $195.000»: falso
  - una seccion entera, «Marcas autenticas disponibles como add-on», listaba
    **Psycho Bunny** y **Harmont & Blaine** — marcas ajenas, y encima productos
    que ya NO se venden (el bump de psychobunny se borro el 3-oct)
  - llamaba «Polo Oxford» y «Polo Tipo Lino» a lo que son camisas oxford y tipo
    lino, el best-seller real (656 y 218 lineas vendidas en 90 dias)
  - afirmaba «+998 clientes con 4,9/5», dato que no se puede sostener
  - listaba 10 ciudades de 36

Se reescribe entero con lo que el sitio puede demostrar, y se le mete el activo
citable que nadie mas publica: **la tabla de medidas real en centimetros**.

── FASE C · hacerlo descubrible ───────────────────────────────────────────────

El llms.txt existia pero NINGUNA pagina lo declaraba. Se añade
`<link rel="describedby">` en todas, que es el mecanismo que nombra la propia
especificacion de llmstxt.org.

── FASE D · telefono en la entidad de marca ───────────────────────────────────

`Organization` no tenia `telephone`. Se añade el que el propio sitio ya publica
en su enlace de WhatsApp (+57 320 754 4636): dato verificable, no inventado.

⚠️ **`sameAs` se queda vacio a proposito.** Es el hueco mas caro de la entidad,
pero la unica pagina de Facebook que cuelga de la cuenta de Meta de este negocio
se llama **«Infinity Store»**, no Camisas Colombia. `sameAs` afirma «esta es la
MISMA entidad»: enlazar ahi una pagina con otro nombre confunde la entidad en vez
de aclararla. Hace falta que el negocio diga cuales son sus perfiles reales.

Uso:  python geo_2026_10_11.py [--dry-run]
      python sincronizar_landings_2026_09_04.py && python build_landings.py
      python indexnow.py          # avisar a Bing, que es quien alimenta la IA
"""
import glob
import io
import os
import re
import shutil
import sys
import time

DRY = "--dry-run" in sys.argv
STAMP = time.strftime("%Y%m%d-%H%M")

# ── FASE A ───────────────────────────────────────────────────────────────────
PACK = {
    "pack-camisas-polo-hombre.html": [
        ("3 x $295.000 o 6 x $430.000", "3 x $295.000 o 5 x $430.000", 4),
        ("6 por $430.000 ($86.000 c/u)", "5 por $430.000 ($86.000 c/u)", 1),
        ("3 por $295.000 o 6 por $430.000", "3 por $295.000 o 5 por $430.000", 1),
        ("3 camisas por 295.000 pesos o 6 por 430.000 pesos",
         "3 camisas por 295.000 pesos o 5 por 430.000 pesos", 2),
        ("el pack de 3 y el de 6", "el pack de 3 y el de 5", 1),
    ],
    "camisas-polo-colores-hombre.html": [
        ("En el pack de 3 y en el de 6", "En el pack de 3 y en el de 5", 2),
    ],
}

# ── FASE C ───────────────────────────────────────────────────────────────────
DESCRIBEDBY = ('<link rel="describedby" type="text/markdown" href="/llms.txt" '
               'title="Catálogo, precios y políticas en texto para asistentes de IA">')

# ── FASE D ───────────────────────────────────────────────────────────────────
ORG_VIEJO = ('"url": "https://www.camisascolombia.com/", "logo": {"@type": "ImageObject", '
             '"url": "https://www.camisascolombia.com/logo.png", "width": 512, "height": 512}')
ORG_NUEVO = ('"url": "https://www.camisascolombia.com/", "telephone": "+573207544636", '
             '"logo": {"@type": "ImageObject", '
             '"url": "https://www.camisascolombia.com/logo.png", "width": 512, "height": 512}')


def guardar(path, texto):
    if DRY:
        return
    shutil.copy(path, path + ".bak-geo-" + STAMP)
    tmp = path + ".tmp"
    io.open(tmp, "w", encoding="utf-8", newline="").write(texto)
    os.replace(tmp, path)


def todas_las_paginas():
    return (sorted(glob.glob("*.html")) + sorted(glob.glob("blog/*.html"))
            + sorted(glob.glob("guias/*.html")))


def fase_a():
    print("\n=== FASE A · pack de 6 -> pack de 5 ===")
    tot = 0
    for path, reps in PACK.items():
        h = io.open(path, encoding="utf-8").read()
        orig, n = h, 0
        for viejo, nuevo, esp in reps:
            if viejo not in h:
                if nuevo in h:
                    continue
                print("  !! %s: no encuentro %r" % (path, viejo[:46]))
                continue
            c = h.count(viejo)
            if c != esp:
                print("  !! %s: %d ocurrencias (esperaba %d) de %r" % (path, c, esp, viejo[:40]))
                continue
            h = h.replace(viejo, nuevo, esp)
            n += esp
        if h != orig:
            guardar(path, h)
        print("  %s %-36s %d cambios" % ("+" if n else "=", path, n))
        tot += n
    return tot


def fase_c():
    print("\n=== FASE C · <link rel=describedby> apuntando al llms.txt ===")
    puestos = ya = sin = 0
    for path in todas_las_paginas():
        h = io.open(path, encoding="utf-8", errors="replace").read()
        if 'rel="describedby"' in h:
            ya += 1
            continue
        m = re.search(r'<link rel="canonical"[^>]*>', h)
        if not m:
            sin += 1
            continue
        h2 = h[:m.end()] + "\n" + DESCRIBEDBY + h[m.end():]
        guardar(path, h2)
        puestos += 1
    print("  añadido en %d paginas   (ya lo tenian: %d, sin canonical: %d)" % (puestos, ya, sin))
    return puestos


def fase_d():
    print("\n=== FASE D · telephone en el Organization ===")
    puestos = ya = 0
    for path in todas_las_paginas():
        h = io.open(path, encoding="utf-8", errors="replace").read()
        if '"telephone": "+573207544636"' in h:
            ya += 1
            continue
        if ORG_VIEJO not in h:
            continue
        c = h.count(ORG_VIEJO)
        if c != 1:
            print("  !! %s: %d ocurrencias del bloque Organization" % (path, c))
            continue
        guardar(path, h.replace(ORG_VIEJO, ORG_NUEVO, 1))
        puestos += 1
    print("  añadido en %d paginas   (ya lo tenian: %d)" % (puestos, ya))
    return puestos


def comprobar():
    print("\n=== COMPROBACIONES ===")
    # ninguna pagina puede seguir hablando de un pack de 6
    pat = re.compile(r"6 (?:x \$?430|por \$?430|por 430)|pack de 6|el de 6", re.I)
    malas = [p for p in todas_las_paginas()
             if pat.search(io.open(p, encoding="utf-8", errors="replace").read())]
    print("  paginas que siguen anunciando un pack de 6: %d" % len(malas))
    for m_ in malas:
        print("    %s" % m_)
    # el JSON-LD tiene que seguir parseando donde metimos el telephone
    import json
    rotos = []
    for p in todas_las_paginas()[:200]:
        h = io.open(p, encoding="utf-8", errors="replace").read()
        if '"telephone": "+573207544636"' not in h:
            continue
        for b in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S):
            try:
                json.loads(b)
            except Exception:
                rotos.append(p)
                break
    print("  JSON-LD roto tras añadir telephone: %d" % len(rotos))
    for r in rotos[:5]:
        print("    %s" % r)
    return not malas and not rotos


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t = fase_a() + fase_c() + fase_d()
    ok = comprobar()
    print("\n%d cambios %s" % (t, "(DRY-RUN: no se escribio nada)" if DRY
                               else "— backups .bak-geo-%s" % STAMP))
    if not ok and not DRY:
        raise SystemExit("!! quedan comprobaciones en rojo")
    print("\nSiguiente: sincronizar_landings + build_landings + verificar_cambios, "
          "y despues python indexnow.py")
