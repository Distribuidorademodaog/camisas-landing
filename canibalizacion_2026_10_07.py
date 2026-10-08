# -*- coding: utf-8 -*-
"""
Arregla la canibalizacion de camisascolombia.com — 2026-10-07.

Medido en Search Console (8-jul a 5-oct, 90 dias): 43 consultas con >=20
impresiones se reparten entre dos o mas paginas. Al abrir el reparto aparecen
DOS problemas distintos, y el grande no era el que decia el informe.

── FASE A · las 36 paginas de ciudad comparten el H1 nacional ──────────────────

El H1 de estas paginas lleva el texto SEO en un <span> oculto para lectores de
pantalla. Las 36 ciudades tenian ahi uno de solo DOS textos, y ninguno nombra su
ciudad:

    25 ciudades: «Camisas Polo para Hombre estilo clasico en Colombia ...»
    11 ciudades: «Camisas Polo para Hombre Estilo Premium en Colombia ...»

O sea: 36 paginas con el mismo H1 pelean por «camisas polo para hombre», que es
el termino que debe poseer el home. Lo confirma el dato: la pagina MEJOR colocada
del sitio para «camisas polo» es /camisas-polo-bogota (posicion 32), por delante
del home y del pilar, porque su H1 ES el termino nacional. Y las 14 paginas que
se reparten ese clustre estan todas entre la posicion 30 y la 74.

El title, el breadcrumb y la meta description de cada ciudad SI eran especificos
y estaban bien escritos (temperatura real, departamento, barrios de reparto). El
H1 era lo unico generico, asi que aqui se redacta desde el dato que ya tenia cada
pagina en su propia meta — no se inventa nada.

Esto ademas refuerza cada ciudad para SU termino local, que es de donde sale el
trafico que si convierte: las paginas de ciudad tienen un CTR del 2,80 % frente
al 0,56 % del blog.

── FASE B · cinco paginas se reparten el eje formal/elegante ───────────────────

/camisas-elegantes-hombre, /camisas-semiformales-hombre, /camisas-formales-hombre,
/camisas-para-oficina-hombre-colombia y /camisas-casuales-hombre-colombia decian
todas alguna version de «el polo como prenda semiformal / business casual», y se
robaban los terminos en el meta keywords. Reparto por evidencia (quien rankea
mejor para que):

    elegantes     pos 45,4 · 243 impr · 3 clics   -> POSEE «camisas elegantes hombre»
    casuales      pos 61,3 · 107 impr             -> POSEE «camisas casuales»
    oficina       pos 51,9 ·  38 impr             -> POSEE «business casual / oficina»
    semiformales  (sin impresiones propias)       -> POSEE «smart casual»
    formales      sin indexar                     -> POSEE «camisas formales»

Cada una deja de reclamar el termino de las otras. No se borra ni se redirige
ninguna pagina: el contenido de cada una es distinto y suficiente, el problema era
solo que todas apuntaban al mismo sitio.

── Lo que NO toca ─────────────────────────────────────────────────────────────

/polos-hombre-colombia aparece con 255 impresiones en posicion 70,7 pero YA es un
308 al pilar y no esta en el sitemap: Google lo sigue mostrando porque no lo ha
vuelto a rastrear. No hay nada que arreglar ahi; se resuelve con el recrawl.

/camisas-hombre-colombia (598 impr) y /camisas-polo-juveniles-hombre (324 impr)
recogen el termino cabeza de rebote, pero su title y su H1 apuntan a cosas
distintas de verdad («camisas para hombre», «juveniles»), asi que se dejan.

── Despues de correr esto ─────────────────────────────────────────────────────

    python sincronizar_landings_2026_09_04.py     # HTML -> _landings (la verdad es el HTML)
    python build_landings.py                      # debe dar git diff VACIO
    python verificar_cambios.py

Uso:  python canibalizacion_2026_10_07.py [--dry-run]
"""
import io
import json
import os
import re
import shutil
import sys
import time

DRY = "--dry-run" in sys.argv
STAMP = time.strftime("%Y%m%d-%H%M")

# El <span> oculto del H1: prefijo y sufijo exactos que lo rodean en todas las paginas.
SR_PRE = ('<h1 class="hero-title"><span style="position:absolute;width:1px;height:1px;'
          'padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;'
          'border:0;">')
SR_RE = re.compile(re.escape(SR_PRE) + r"(.*?)</span>", re.S)

# ── FASE A ────────────────────────────────────────────────────────────────────
# {slug: (nombre tal como lo usa su propio breadcrumb, angulo sacado de su propia
#  meta description)}. El H1 se arma con PLANTILLA_CIUDAD.
PLANTILLA_CIUDAD = ("Camisas polo para hombre en {ciudad}: {angulo}, tallas S a 5XL "
                    "y +20 colores, pago contraentrega y envío gratis. ")

CIUDADES = {
    "apartado":          ("Apartadó",            "algodón piqué que respira con la humedad del Urabá"),
    "armenia":           ("Armenia, Quindío",    "algodón premium con envío gratis a todo el Eje Cafetero"),
    "barranquilla":      ("Barranquilla",        "tela fresca para los 30 °C"),
    "bello":             ("Bello",               "tela para los 22 °C del norte del Aburrá"),
    "bogota":            ("Bogotá",              "manga larga o corta para los 13 °C"),
    "bucaramanga":       ("Bucaramanga",         "tela para los 23 °C de la ciudad"),
    "buenaventura":      ("Buenaventura",        "algodón piqué que seca rápido con la humedad del Pacífico"),
    "cali":              ("Cali",                "tela fresca para los 30 °C del Valle"),
    "cartagena":         ("Cartagena",           "tela fresca para los 30 °C"),
    "cucuta":            ("Cúcuta",              "tela fresca para los 28 °C"),
    "dosquebradas":      ("Dosquebradas",        "tela para los 21 °C del Eje Cafetero"),
    "envigado":          ("Envigado, Antioquia", "algodón piqué en estilo premium"),
    "floridablanca":     ("Floridablanca",       "tela para los 23 °C del área metropolitana"),
    "girardot":          ("Girardot",            "algodón piqué para los 33 °C del Alto Magdalena"),
    "ibague":            ("Ibagué, Tolima",      "tela cómoda para los 22 °C"),
    "itagui":            ("Itagüí, Antioquia",   "algodón piqué en estilo premium"),
    "magangue":          ("Magangué",            "algodón piqué para los 30 °C del Magdalena"),
    "maicao":            ("Maicao",              "algodón piqué para los 30 °C de La Guajira"),
    "manizales":         ("Manizales",           "manga larga para los 17 °C"),
    "medellin":          ("Medellín",            "tela cómoda para los 22 °C de todo el año"),
    "monteria":          ("Montería, Córdoba",   "algodón piqué en estilo premium"),
    "neiva":             ("Neiva, Huila",        "algodón piqué fresco en estilo clásico"),
    "palmira":           ("Palmira",             "algodón piqué para los 24 °C de la Villa de las Palmas"),
    "pasto":             ("Pasto, Nariño",       "ideales para vestir en capas por el clima frío"),
    "pereira":           ("Pereira",             "tela cómoda para los 21 °C"),
    "popayan":           ("Popayán, Cauca",      "algodón piqué en estilo premium para la Ciudad Blanca"),
    "riohacha":          ("Riohacha",            "algodón piqué para los 29 °C y la brisa de La Guajira"),
    "santa-marta":       ("Santa Marta",         "tela fresca para los 32 °C"),
    "sincelejo":         ("Sincelejo",           "algodón piqué para los 28 °C de las sabanas de Sucre"),
    "soacha":            ("Soacha",              "tela para el frío de la sabana"),
    "tunja":             ("Tunja",               "manga larga y corta para los 13 °C de Boyacá"),
    "turbo":             ("Turbo",               "algodón piqué que seca rápido con la humedad del golfo"),
    "valledupar":        ("Valledupar, Cesar",   "estilo clásico en calidad premium"),
    "villa-del-rosario": ("Villa del Rosario",   "algodón piqué para los 28 °C del área de Cúcuta"),
    "villavicencio":     ("Villavicencio, Meta", "tela fresca para los 33 °C del Llano"),
    "yopal":             ("Yopal",               "algodón piqué para el calor del Llano"),
}

# Los dos H1 genericos que se esperan encontrar. Si aparece otro, se avisa y no se toca.
H1_GENERICOS = {
    "Camisas Polo para Hombre estilo clásico en Colombia con Pago Contraentrega y Envío Gratis. ",
    "Camisas Polo para Hombre Estilo Premium en Colombia con Pago Contraentrega y Envío Gratis. ",
}

# ── FASE B ────────────────────────────────────────────────────────────────────
# {slug: [(viejo, nuevo), ...]}  reemplazos exactos, 1 ocurrencia cada uno.
FORMAL = {
    "camisas-elegantes-hombre": [
        # El title de 29 caracteres desperdiciaba espacio en el SERP.
        ("<title>Camisas Elegantes para Hombre</title>",
         "<title>Camisas Elegantes para Hombre en Colombia | Sin Corbata</title>"),
        # Deja de llamarse «semiformal»: ese termino es de /camisas-semiformales-hombre.
        ("Camisas elegantes para hombre en Colombia: el polo como prenda semiformal que "
         "reemplaza a la camisa formal sin corbata.",
         "Camisas elegantes para hombre en Colombia: el polo que reemplaza a la camisa de "
         "vestir sin necesidad de corbata, en algodon pique premium y tallas S a 5XL."),
        ("camisas elegantes hombre, camisa polo elegante, camisas semiformales hombre, polo elegante colombia",
         "camisas elegantes hombre, camisa polo elegante, camisas elegantes para hombre, polo elegante colombia"),
        ("Camisas polo elegantes para hombre en Colombia: la prenda semiformal que reemplaza "
         "a la camisa formal sin corbata,",
         "Camisas polo elegantes para hombre en Colombia: la camisa elegante que no necesita corbata,"),
    ],
    "camisas-semiformales-hombre": [
        # «business casual» pasa a ser de /camisas-para-oficina-hombre-colombia.
        ("El polo resuelve el business casual y el smart casual sin esfuerzo.",
         "El polo resuelve el look smart casual sin esfuerzo."),
        ("camisas smart casual hombre, camisas business casual hombre, camisa semiformal colombia",
         "camisas smart casual hombre, camisa smart casual, camisa semiformal colombia"),
        ("el polo de algodon pique resuelve el look smart casual y business casual.",
         "el polo de algodon pique resuelve el look smart casual."),
    ],
    "camisas-para-oficina-hombre-colombia": [
        # Deja de reclamar «elegantes», que es de /camisas-elegantes-hombre. Este
        # fragmento esta en meta description, og:description, twitter:description y
        # la description del WebPage: los CUATRO deben cambiar, de ahi el n=4.
        ("polos business casual, elegantes sin corbata, colores sobrios",
         "polos business casual en colores sobrios para ir a trabajar", 4),
        ("camisas para oficina colombia, camisas oficina hombre, camisas business casual, "
         "camisas formales hombre colombia, polo para oficina",
         "camisas para oficina colombia, camisas oficina hombre, camisas business casual, "
         "camisas business casual hombre, polo para oficina"),
        ("Camisas para oficina hombre en Colombia: business casual elegante, tallas S a 5XL",
         "Camisas para oficina hombre en Colombia: business casual para ir a trabajar, tallas S a 5XL"),
    ],
    "camisas-formales-hombre": [
        # Su keywords reclamaba los terminos de elegantes Y de oficina.
        ("polo formal, camisas elegantes hombre, camisa formal sin corbata, camisas para oficina hombre,",
         "polo formal, camisas formales para hombre, camisa formal sin corbata, camisa polo formal hombre,"),
        # La meta description estaba cortada a media frase («algodon pique premium, S a.»).
        ("¿Puede una camisa polo ser formal? Si, con el color, la tela y el ajuste correctos. "
         "Camisas formales para hombre en Colombia: algodon pique premium, S a.",
         "¿Puede una camisa polo ser formal? Si, con el color, la tela y el ajuste correctos. "
         "Camisas formales para hombre en Colombia en algodon pique premium, tallas S a 5XL."),
    ],
    "camisas-casuales-hombre-colombia": [
        # «bien vestido» se solapaba con elegantes; aqui el eje es el diario y el fin de semana.
        ("Camisas casuales para hombre en Colombia: el polo como uniforme del hombre bien vestido a diario.",
         "Camisas casuales para hombre en Colombia: el polo de algodon pique para el dia a dia "
         "y el fin de semana, en tallas S a 5XL con pago contraentrega."),
        ("Camisas casuales para hombre en Colombia: polo de algodon pique premium para vestir "
         "bien todos los dias,",
         "Camisas casuales para hombre en Colombia: polo de algodon pique premium para el dia "
         "a dia y el fin de semana,"),
    ],
}


def guardar(path, texto):
    if DRY:
        return
    shutil.copy(path, path + ".bak-canib-" + STAMP)
    # .tmp + replace: el modo "w" trunca el archivo antes de poder fallar.
    tmp = path + ".tmp"
    io.open(tmp, "w", encoding="utf-8", newline="").write(texto)
    os.replace(tmp, path)


def fase_a():
    print("\n" + "=" * 78)
    print("FASE A — H1 propio para cada una de las 36 ciudades")
    print("=" * 78)
    hechas = saltadas = 0
    for slug, (ciudad, angulo) in sorted(CIUDADES.items()):
        f = "camisas-polo-%s.html" % slug
        if not os.path.exists(f):
            print("  !! no existe %s" % f)
            continue
        h = io.open(f, encoding="utf-8").read()
        ms = SR_RE.findall(h)
        if len(ms) != 1:
            print("  !! %-34s %d spans de H1, esperaba 1 — SIN TOCAR" % (slug, len(ms)))
            continue
        viejo = ms[0]
        nuevo = PLANTILLA_CIUDAD.format(ciudad=ciudad, angulo=angulo)
        if viejo == nuevo:
            print("  =  %-34s ya aplicado" % slug)
            saltadas += 1
            continue
        if viejo not in H1_GENERICOS:
            print("  !! %-34s H1 inesperado, SIN TOCAR: %s" % (slug, viejo[:62]))
            continue
        h2 = h.replace(SR_PRE + viejo + "</span>", SR_PRE + nuevo + "</span>", 1)
        assert h2 != h, slug
        guardar(f, h2)
        print("  +  %-34s %s" % (slug, nuevo.strip()[:96]))
        hechas += 1
    print("\n  %d ciudades reescritas, %d ya estaban, %d sin tocar" %
          (hechas, saltadas, len(CIUDADES) - hechas - saltadas))
    return hechas


def fase_b():
    print("\n" + "=" * 78)
    print("FASE B — un termino por pagina en el eje formal/elegante")
    print("=" * 78)
    total = 0
    for slug, reps in FORMAL.items():
        f = slug + ".html"
        if not os.path.exists(f):
            print("  !! no existe %s" % f)
            continue
        h = io.open(f, encoding="utf-8").read()
        orig, n, ya = h, 0, 0
        for regla in reps:
            viejo, nuevo = regla[0], regla[1]
            esperadas = regla[2] if len(regla) > 2 else 1
            if viejo not in h:
                if nuevo in h:
                    ya += 1
                    continue
                print("  !! %-38s no encuentro: %s" % (slug, viejo[:58]))
                continue
            c = h.count(viejo)
            if c != esperadas:
                print("  !! %-38s %d ocurrencias (esperaba %d) de %s — SIN TOCAR"
                      % (slug, c, esperadas, viejo[:40]))
                continue
            h = h.replace(viejo, nuevo, esperadas)
            n += esperadas
        if h != orig:
            guardar(f, h)
        print("  %s %-38s %d cambios%s" % ("+" if n else "=", slug, n,
                                           (" (%d ya aplicados)" % ya) if ya else ""))
        total += n
    print("\n  %d reemplazos en %d paginas" % (total, len(FORMAL)))
    return total


def comprobar():
    """Nadie debe quedar con el H1 nacional salvo el home."""
    print("\n" + "=" * 78)
    print("COMPROBACION — quien reclama el termino cabeza en su H1")
    print("=" * 78)
    import glob
    culpables = []
    for f in sorted(glob.glob("*.html")):
        h = io.open(f, encoding="utf-8").read()
        ms = SR_RE.findall(h)
        if not ms:
            continue
        if ms[0] in H1_GENERICOS:
            culpables.append(f)
    print("  paginas con el H1 nacional generico: %d" % len(culpables))
    for c in culpables:
        print("    %s" % c)
    if not culpables:
        print("  OK — ninguna pagina de ciudad pelea ya por «camisas polo para hombre»")
    # keywords cruzadas
    print("\n  terminos cruzados que quedan en meta keywords:")
    CRUCES = {
        "camisas-elegantes-hombre": "camisas semiformales hombre",
        "camisas-semiformales-hombre": "camisas business casual hombre",
        "camisas-formales-hombre": "camisas elegantes hombre",
        "camisas-para-oficina-hombre-colombia": "camisas formales hombre colombia",
    }
    limpio = True
    for slug, termino in CRUCES.items():
        h = io.open(slug + ".html", encoding="utf-8").read()
        kw = re.search(r'<meta name="keywords" content="(.*?)">', h)
        if kw and termino in kw.group(1):
            print("    %-38s sigue reclamando «%s»" % (slug, termino))
            limpio = False
    if limpio:
        print("    ninguno — cada pagina reclama solo su termino")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = fase_a()
    b = fase_b()
    comprobar()
    print("\n%s" % ("(DRY-RUN: no se escribio nada)" if DRY
                    else "aplicado — backups .bak-canib-%s" % STAMP))
    print("\nSiguiente:  python sincronizar_landings_2026_09_04.py"
          "  &&  python build_landings.py  (git diff debe quedar vacio)"
          "  &&  python verificar_cambios.py")
