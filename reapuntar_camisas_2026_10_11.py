# -*- coding: utf-8 -*-
"""
Pasos 1, 2 y 3 · Reapuntar el sitio de «camisas polo» a «camisas» — 2026-10-11.

Hallazgo que lo motiva (cruce de items_pedido con Search Console, 90 dias):
el negocio **vende oxford y tipo lino**, pero el SEO entero apunta a **polo**.

    oxford      656 lineas vendidas   ->   2 paginas
    tipo lino   218 lineas            ->   1 pagina
    polo        (el resto)            ->  57-68 paginas

Y `/camisas-oxford-100-algodon` hace el **mejor CTR del sitio, 6,04 %**, con solo
265 impresiones en 90 dias: la unica pagina apuntada al best-seller y sin alimentar.

Demanda (Google Ads, Colombia): `camisas para hombre` 8.100 · `camisa manga larga`
4.400 · `camisa blanca hombre` 2.400 · `camisa oxford` 1.900 + `camisas oxford`
1.900 · `camisa de lino` 1.600 · `camisa negra hombre` 1.300.

── Lo que NO se hace, y por que ────────────────────────────────────────────────

El plan original decia «cambiar el pilar Y la home de camisas polo a camisas».
No se hace:

 1. **El pilar no se toca.** Si la home y el pilar dejan «camisas polo», nadie se
    queda ese termino (2.900/mes) y el negocio si vende polos. El pilar sigue
    siendo el hub de polo. Ademas ES la plantilla de build_landings.py: cambiarle
    el title obliga a actualizar RL_TITLE/RL_OG_TITLE/RL_TW_TITLE/RL_WEBPAGE_NAME
    o el build aborta, y ya paso dos veces.
 2. **El title de la home no se toca.** Es la pagina que mejor convierte del sitio
    (48,2 clics/1.000). Solo se le añade oxford y tipo lino al H1 y a la meta para
    que el producto real se vea, sin arriesgar lo que ya funciona.
 3. **`/camisas-hombre-colombia` ya estaba bien apuntada**: su title, meta y H1 ya
    nombran «manga corta y larga, tipo lino, Oxford, cuadros y rayas». No necesita
    reescritura, necesita enlaces. Se deja y se le enlaza desde la home.

── FASE A · quitar «polo» de las paginas cuyo producto NO es polo ──────────────

Tres paginas se describian como «camisas polo» algo, cuando el producto que se
vende ahi es camisa oxford o tipo lino. Eso las dejaba fuera de 4.400 + 1.600 +
1.300 busquedas/mes de su propio termino.

── FASE B · resolver la canibalizacion de oxford ───────────────────────────────

Dos paginas persiguen «camisas oxford». Reparto por evidencia:

    /camisas-oxford-100-algodon      pos 10,8 · 265 impr · 16 clics · 6,04 %  GANA
    /camisas-oxford-hombre-colombia  pos 18,2 · 272 impr ·  5 clics · 1,84 %

La ganadora se queda el eje **tela** («oxford 100% algodon»), que es por lo que
rankea. La otra pasa al eje **color y talla** y deja de reclamar los terminos de
la primera en su meta keywords.

── FASE C · la home enseña el producto real ────────────────────────────────────

── FASE D · piloto de 4 ciudades ──────────────────────────────────────────────

Las 29 ciudades son el segundo tipo que mejor convierte (27,9 clics/1.000 frente
a 5,6 del blog) y no mencionan oxford ni lino. Se prueba en las 4 que mas clics
traen — Cali 36, Bucaramanga 27, Cucuta 19, Barranquilla 17, el 20 % de los clics
del sitio — y se mide 4 semanas antes de tocar las otras 25.

⚠️ El title **conserva «Polo»** y añade oxford y tipo lino: es aditivo, no
sustitutivo. Quitar «Polo» arriesgaria «camisas polo <ciudad>», que es por lo que
estas paginas rankean hoy. Y se conserva el detalle local (temperatura, barrios),
que es lo que las hace unicas.

`camisas-manga-corta-hombre` es GENERADA: despues de este script hay que correr
sincronizar_landings_2026_09_04.py y build_landings.py.

Uso:  python reapuntar_camisas_2026_10_11.py [--dry-run]
"""
import io
import os
import re
import shutil
import sys
import time

DRY = "--dry-run" in sys.argv
STAMP = time.strftime("%Y%m%d-%H%M")

# {archivo: [(viejo, nuevo, n_esperado), ...]}
FASES = {}

# ── FASE A ───────────────────────────────────────────────────────────────────
FASES["A · quitar «polo» donde el producto no es polo"] = {
    "camisas-tipo-lino-hombre.html": [
        ("Camisas polo tipo lino para hombre en Colombia: frescas y elegantes para clima cálido",
         "Camisas tipo lino para hombre en Colombia: oxford y tipo lino frescos para clima cálido", 4),
    ],
    "camisas-manga-larga-contraentrega.html": [
        ("Camisas polo manga larga para hombre con pago contraentrega en Colombia.",
         "Camisas manga larga para hombre en Colombia: oxford y tipo lino con pago contraentrega.", 4),
        ("Camisas polo manga larga para hombre en Colombia con pago contraentrega: pagas al recibir,",
         "Camisas manga larga para hombre en Colombia, oxford y tipo lino, con pago contraentrega: pagas al recibir,", 1),
    ],
    # Esta pagina es GENERADA y cada campo tiene su propio texto, asi que hay que
    # tocarlos uno a uno: son 1 ocurrencia cada uno, no 4. Todos decian «algodon
    # pique», que es la tela del POLO, en la pagina de «camisa manga corta»
    # (1.300 busquedas/mes) cuyo producto real es oxford y tipo lino.
    "camisas-manga-corta-hombre.html": [
        ("Camisas manga corta para hombre en algodon pique fresco: la opcion mas versatil para el clima calido de Colombia.",
         "Camisas manga corta para hombre en Colombia: oxford, tipo lino y algodon pique, la opcion mas versatil para el clima calido.", 1),
        ("Camisas manga corta para hombre en Colombia: algodon pique fresco, la opcion mas versatil para el clima calido,",
         "Camisas manga corta para hombre en Colombia: oxford, tipo lino y algodon pique fresco, la opcion mas versatil para el clima calido,", 1),
        ("Camisas Manga Corta para Hombre | Polo Fresco, Pago Contraentrega",
         "Camisas Manga Corta Hombre | Oxford, Tipo Lino y Polo", 1),
        ("Camisas manga corta en algodon pique premium: frescas, versatiles y perfectas para el calor de Colombia.",
         "Camisas manga corta en oxford, tipo lino y algodon pique: frescas y perfectas para el calor de Colombia.", 1),
        ("Camisas manga corta frescas en algodon pique. La opcion mas versatil para el clima calido.",
         "Camisas manga corta en oxford, tipo lino y algodon pique. La opcion mas versatil para el clima calido.", 1),
        ("Camisas manga corta para hombre en Colombia con algodon pique fresco: la opcion mas versatil para el clima calido,",
         "Camisas manga corta para hombre en Colombia en oxford, tipo lino y algodon pique: la opcion mas versatil para el clima calido,", 1),
        ("Camisas Manga Corta para Hombre | Frescas para el Clima Colombiano",
         "Camisas Manga Corta Hombre: Oxford, Tipo Lino y Polo", 1),
    ],
}

# ── FASE B ───────────────────────────────────────────────────────────────────
FASES["B · canibalizacion de oxford"] = {
    "camisas-oxford-hombre-colombia.html": [
        ("<title>Camisas Oxford para Hombre en Colombia | Estilo Clásico</title>",
         "<title>Camisas Oxford Hombre: Colores y Tallas S a 5XL</title>", 1),
        # deja de reclamar «camisa oxford hombre» y «camisas oxford», que son de
        # /camisas-oxford-100-algodon, la que rankea mejor
        ("camisas oxford hombre colombia, camisa oxford hombre, polo oxford, camisas oxford,",
         "camisas oxford hombre colombia, camisa oxford blanca, camisa oxford negra, camisas oxford por color,", 1),
        ("Camisas Oxford para hombre en Colombia: estilo clásico versátil, algodón premium, tallas S a 5XL, +20 colores.",
         "Camisas Oxford para hombre en Colombia por color y talla: blanca, negra, celeste, arena y verde oliva, de la S a la 5XL.", 4),
        ("Camisas Oxford para hombre en Colombia: estilo clásico, tallas S a 5XL,",
         "Camisas Oxford para hombre en Colombia por color y talla, de la S a la 5XL,", 1),
    ],
}

# ── FASE C ───────────────────────────────────────────────────────────────────
FASES["C · la home enseña el producto real"] = {
    "index.html": [
        ("Camisas polo para hombre en Colombia: más de 20 colores en algodón piqué, tallas S a 5XL, pago contraentrega y envío gratis.",
         "Camisas para hombre en Colombia: oxford, tipo lino, manga larga y polo, en más de 20 colores y tallas S a 5XL, con pago contraentrega y envío gratis.", 1),
        ("Camisas polo para hombre en Colombia: +20 colores en algodón piqué, tallas S a 5XL y polos desde $86.000 en pack.",
         "Camisas para hombre en Colombia: oxford, tipo lino, manga larga y polo. +20 colores, tallas S a 5XL y packs desde $86.000.", 3),
    ],
}

# ── FASE D ───────────────────────────────────────────────────────────────────
# (archivo, ciudad, angulo local que ya tenia)
PILOTO = [
    ("camisas-polo-cali.html",         "Cali",         "tela fresca para los 30 °C del Valle"),
    ("camisas-polo-bucaramanga.html",  "Bucaramanga",  "tela para los 23 °C de la ciudad"),
    ("camisas-polo-cucuta.html",       "Cúcuta",       "tela fresca para los 28 °C"),
    ("camisas-polo-barranquilla.html", "Barranquilla", "tela fresca para los 30 °C"),
]
TITLES_PILOTO = {
    "camisas-polo-cali.html":
        ("<title>Camisas Polo en Cali: Tela Fresca para el Calor del Valle</title>",
         "<title>Camisas en Cali: Oxford, Tipo Lino y Polo | Contraentrega</title>"),
    "camisas-polo-bucaramanga.html":
        ("<title>Camisas Polo en Bucaramanga | Tallas S a 5XL, Paga al Recibir</title>",
         "<title>Camisas en Bucaramanga: Oxford, Tipo Lino y Polo, S a 5XL</title>"),
    "camisas-polo-cucuta.html":
        ("<title>Camisas Polo en Cúcuta | Tela Fresca y Pagas al Recibir</title>",
         "<title>Camisas en Cúcuta: Oxford, Tipo Lino y Polo | Paga al Recibir</title>"),
    "camisas-polo-barranquilla.html":
        ("<title>Camisas Polo en Barranquilla | Tela Fresca para el Calor</title>",
         "<title>Camisas en Barranquilla: Oxford, Tipo Lino y Polo, S a 5XL</title>"),
}
SR_PRE = ('<h1 class="hero-title"><span style="position:absolute;width:1px;height:1px;'
          'padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;'
          'border:0;">')


def guardar(path, texto):
    if DRY:
        return
    shutil.copy(path, path + ".bak-reap-" + STAMP)
    tmp = path + ".tmp"
    io.open(tmp, "w", encoding="utf-8", newline="").write(texto)
    os.replace(tmp, path)


def aplicar(path, reps):
    h = io.open(path, encoding="utf-8").read()
    orig, n, ya = h, 0, 0
    for viejo, nuevo, esp in reps:
        if viejo not in h:
            if nuevo in h:
                ya += 1
                continue
            print("     !! no encuentro: %s" % viejo[:62])
            continue
        c = h.count(viejo)
        if c != esp:
            print("     !! %d ocurrencias (esperaba %d): %s" % (c, esp, viejo[:48]))
            continue
        h = h.replace(viejo, nuevo, esp)
        n += esp
    if h != orig:
        guardar(path, h)
    return n, ya, h != orig


def main():
    total = 0
    for fase, archivos in FASES.items():
        print("\n=== FASE %s ===" % fase)
        for path, reps in archivos.items():
            if not os.path.exists(path):
                print("  !! no existe %s" % path)
                continue
            n, ya, cambio = aplicar(path, reps)
            print("  %s %-40s %d cambios%s" % ("+" if n else "=", path, n,
                                               ("  (%d ya aplicados)" % ya) if ya else ""))
            total += n

    print("\n=== FASE D · piloto de 4 ciudades ===")
    for path, ciudad, angulo in PILOTO:
        if not os.path.exists(path):
            print("  !! no existe %s" % path)
            continue
        h = io.open(path, encoding="utf-8").read()
        orig = h
        n = 0
        # 1. title (conserva «Polo», añade oxford y tipo lino)
        vt, nt = TITLES_PILOTO[path]
        if vt in h:
            assert h.count(vt) == 1, path
            h = h.replace(vt, nt, 1)
            n += 1
        elif nt not in h:
            print("  !! %s: title inesperado" % path)
        # 2. H1 oculto: nombra las prendas que se venden, conservando el angulo local
        m = re.search(re.escape(SR_PRE) + r"(.*?)</span>", h, re.S)
        if not m:
            print("  !! %s: sin span de H1" % path)
            continue
        viejo_h1 = m.group(1)
        nuevo_h1 = ("Camisas para hombre en %s: oxford, tipo lino, manga larga y polo, "
                    "%s, tallas S a 5XL, pago contraentrega y envío gratis. " % (ciudad, angulo))
        if viejo_h1 != nuevo_h1:
            h = h.replace(SR_PRE + viejo_h1 + "</span>", SR_PRE + nuevo_h1 + "</span>", 1)
            n += 1
        # 3. WebPage.name = el nuevo title
        ti = re.search(r"<title>(.*?)</title>", h).group(1)
        h, k = re.subn(r'("@type": "WebPage".*?"name": ")(.*?)(")',
                       lambda mm: mm.group(1) + ti + mm.group(3), h, count=1, flags=re.S)
        n += k
        if h != orig:
            guardar(path, h)
        print("  + %-34s %d cambios" % (path, n))
        print("      title: %s" % ti)
        print("      H1   : %s" % nuevo_h1.strip()[:104])
        total += n

    print("\n=== COMPROBACIONES ===")
    # ninguna de las tocadas puede quedar con «camisas polo» donde el producto no es polo
    mal = []
    for p in ["camisas-tipo-lino-hombre.html", "camisas-manga-larga-contraentrega.html",
              "camisas-manga-corta-hombre.html"]:
        h = io.open(p, encoding="utf-8").read()
        de = re.search(r'<meta name="description" content="(.*?)">', h)
        if de and re.search(r"[Cc]amisas polo", de.group(1)):
            mal.append(p)
    print("  paginas de no-polo que siguen diciendo «camisas polo» en la meta: %d" % len(mal))
    for m_ in mal:
        print("    %s" % m_)
    # oxford: cada pagina con su termino
    h = io.open("camisas-oxford-hombre-colombia.html", encoding="utf-8").read()
    kw = re.search(r'<meta name="keywords" content="(.*?)">', h)
    cruce = kw and "camisa oxford hombre," in kw.group(1)
    print("  /camisas-oxford-hombre-colombia sigue reclamando «camisa oxford hombre»: %s"
          % ("SI" if cruce else "no"))
    # titles unicos
    import glob
    titles = {}
    for f in glob.glob("*.html") + glob.glob("blog/*.html") + glob.glob("guias/*.html"):
        hh = io.open(f, encoding="utf-8", errors="replace").read()
        t = re.search(r"<title>(.*?)</title>", hh)
        if t:
            titles.setdefault(t.group(1), []).append(f)
    dup = {k: v for k, v in titles.items() if len(v) > 1}
    print("  titles duplicados en el sitio: %d" % len(dup))
    for k, v in list(dup.items())[:4]:
        print("    %s -> %s" % (k[:60], ", ".join(v[:3])))

    print("\n%d cambios en total %s" % (total, "(DRY-RUN: no se escribio nada)" if DRY
                                        else "— backups .bak-reap-%s" % STAMP))
    print("\nSiguiente: python sincronizar_landings_2026_09_04.py  &&  python build_landings.py"
          "  &&  python verificar_cambios.py")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
