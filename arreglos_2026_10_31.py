# -*- coding: utf-8 -*-
"""Los tres arreglos aprobados por el user el 2026-10-31, tras la auditoria con
todas las skills (informe en C:\\tmp\\camisas-seo-20261031\\INFORME.md).

A) /gracias: los dos botones de WhatsApp apuntaban a 573001234567, un numero de
   ejemplo. Es la unica pagina donde el comprador contraentrega pregunta por su
   pedido; si no puede preguntar, rechaza el paquete.

B) El blog «cuantas-camisas-polo-debe-tener-un-hombre» prometia «probartelo en
   casa y pagar solo cuando confirmes que te queda», que viola la regla dura del
   negocio, y decia «coleccion de 6 te cuesta $575.000» (resto del pack de 6, y
   con la cuenta mal: 575.000 son 5 unidades, no 6).

C) 168 testimonios inventados con nombre y barrio en 21 paginas de ciudad. El
   sitio tiene 4 resenas reales. Se quita el bloque entero de las 21 paginas, del
   generador build_cities.py y del template, para que no vuelva en un rebuild.

🚨 Los HTML del repo tienen CRLF: se lee y escribe con newline='' para no
   convertir todo el fichero y dejar el diff irrevisable.
"""
import glob, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RAIZ = os.path.dirname(os.path.abspath(__file__))
SECO = "--dry" in sys.argv

WA_MALO, WA_BUENO = "573001234567", "573207544636"


def leer(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def escribir(p, s):
    if SECO:
        return
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def quitar_bloque_testimonios(h):
    """Borra el <div class="city-block"> que contiene los testimonios, entero.

    Hay que contar la profundidad de <div>: el bloque lleva 8 divs hijos y un
    corte por la primera </div> dejaria HTML roto.
    """
    m = re.search(r'<h3[^>]*class="city-block-title"[^>]*>\s*Lo que dicen nuestros clientes', h)
    if not m:
        return h, 0
    ini = h.rfind('<div class="city-block">', 0, m.start())
    if ini < 0:
        return h, 0
    i, prof = ini, 0
    for t in re.finditer(r'<div\b|</div>', h[ini:]):
        prof += 1 if t.group(0).startswith("<div") else -1
        if prof == 0:
            i = ini + t.end()
            break
    else:
        return h, 0
    n = h[ini:i].count('class="city-testi"')
    # se lleva tambien la linea en blanco que queda detras
    resto = h[i:]
    resto = re.sub(r'^(\r?\n)\s*(\r?\n)', r'\1', resto, count=1)
    return h[:ini].rstrip(" ") + resto, n


def main():
    # ─────────────────────────── A) gracias.html ───────────────────────────
    p = os.path.join(RAIZ, "gracias.html")
    h = leer(p)
    n = h.count(WA_MALO)
    if n:
        escribir(p, h.replace(WA_MALO, WA_BUENO))
    print("A) gracias.html: %d enlaces de WhatsApp %s -> %s" % (n, WA_MALO, WA_BUENO))

    # ─────────────────────────── B) el blog ────────────────────────────────
    p = os.path.join(RAIZ, "blog", "cuantas-camisas-polo-debe-tener-un-hombre.html")
    h = leer(p)
    antes = h
    CAMBIOS_B = [
        ("probártelo en casa y pagar solo cuando confirmes que te queda como esperabas",
         "pagar al recibirlo, cuando el pedido llegue a tu casa"),
        ("armar una colección de 6 te cuesta $575.000",
         "armar una colección de 5 te cuesta $575.000"),
        ("te ahorras casi $200.000", "te ahorras $145.000"),
    ]
    for viejo, nuevo in CAMBIOS_B:
        if viejo in h:
            h = h.replace(viejo, nuevo)
            print("B) blog: «%s…» -> «%s…»" % (viejo[:48], nuevo[:48]))
        else:
            print("B) blog: NO encontrado «%s…»" % viejo[:48])
    if h != antes:
        escribir(p, h)

    # ─────────────────── C) testimonios inventados ─────────────────────────
    tot_p = tot_t = 0
    for f in sorted(glob.glob(os.path.join(RAIZ, "camisas-polo-*.html"))):
        h = leer(f)
        if 'class="city-testi"' not in h:
            continue
        nuevo, n = quitar_bloque_testimonios(h)
        if n:
            escribir(f, nuevo)
            tot_p += 1
            tot_t += n
    print("C) testimonios: %d quitados de %d paginas de ciudad" % (tot_t, tot_p))

    # el generador, para que no vuelvan
    p = os.path.join(RAIZ, "build_cities.py")
    h = leer(p)
    bloque = """    <div class="city-block">
          <h3 class="city-block-title">Lo que dicen nuestros clientes en {name}</h3>
          <div class="city-testimonials">
    {testi_html}      </div>
        </div>
    """
    if bloque in h:
        escribir(p, h.replace(bloque, ""))
        print("D) build_cities.py: bloque de testimonios eliminado del generador")
    else:
        print("D) build_cities.py: NO se encontro el bloque (revisar a mano)")

    print("\n%s" % ("DRY RUN — no se escribio nada" if SECO else "escrito"))


if __name__ == "__main__":
    main()
