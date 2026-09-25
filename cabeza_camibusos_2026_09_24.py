# -*- coding: utf-8 -*-
"""
Termino cabeza al home + rescate de camibusos — 2026-09-24.

Medido en la auditoria 360 de hoy (GSC 26-ago/22-sep):

1. EL TERMINO CABEZA NO LO TIENE EL HOME NI LA PILAR: lo captura
   `/camisas-hombre-colombia` en posicion 59-69 con 471 impresiones y CERO
   clics. La pilar, tras reescribirse el 10-sep y recibir 71 enlaces internos,
   tuvo **1 sola impresion en 28 dias**. Y home y pilar llevaban titles casi
   identicos («Camisas Polo para Hombre … en Colombia»), asi que competian
   entre ellos.

   Se reparte el terreno:
     home    -> el termino cabeza («camisas polo para hombre», «polos para
                hombre»). Ya rankea 8,7 para «camisas polo colombia» y rinde
                74,5 clics/1.000, el mejor del sitio.
     pilar   -> hub de CATALOGO (color, talla, ocasion). Deja de pelear con el
                home; es lo que de verdad hace desde el 10-sep.
     /camisas-hombre-colombia -> su propio termino, «camisas para hombre». Se
                le quita «polo» del title, description y H1 (el CUERPO no se
                toca: 206 menciones son del catalogo y el checkout compartidos).

2. CAMIBUSO SE ENFRIA: 652 impresiones en pos 9,6 -> 303 en pos 13,2. Es el
   unico termino que la competencia no trabaja y el punto 1 del plan del 10-sep
   que nunca se ejecuto. Le falta:
     - La grafia «camibuzo»: 0 menciones en todo el sitio, cuando «como se
       escribe camibuso» es una consulta real con impresiones propias.
     - Enlaces desde las ciudades: de 29, solo 4 lo enlazan.

Uso:  python cabeza_camibusos_2026_09_24.py [--dry-run]
"""
import glob
import io
import json
import os
import re
import sys

DRY = "--dry-run" in sys.argv
MARCA = 'data-link="cabeza-2026-09"'

# ── 1. termino cabeza ───────────────────────────────────────────────────────
META = {
    "index.html": dict(
        title="Camisas Polo para Hombre en Colombia | Tallas S a 5XL",
        desc="Camisas polo para hombre en Colombia: +20 colores en algodón piqué, tallas S a 5XL y polos desde $86.000 en pack. Pago contraentrega y envío gratis.",
        h1="Camisas polo para hombre en Colombia: más de 20 colores en algodón piqué, tallas S a 5XL, pago contraentrega y envío gratis.",
    ),
    "camisas-polo-premium-colombia.html": dict(
        title="Catálogo de Camisas Polo: Color, Talla y Ocasión",
        desc="Todo el catálogo de camisas polo para hombre: elige por color (+20), por talla de la S a la 5XL o por ocasión. Pago contraentrega y envío gratis a Colombia.",
        h1="Catálogo de camisas polo para hombre: elige por color, por talla de la S a la 5XL o por ocasión, con pago contraentrega y envío gratis.",
    ),
    "camisas-hombre-colombia.html": dict(
        title="Camisas para Hombre en Colombia | Contraentrega",
        desc="Camisas para hombre en Colombia: manga corta y larga, tipo lino, Oxford, cuadros y rayas. +20 colores, tallas S a 5XL, pago contraentrega y envío gratis.",
        h1="Camisas para hombre en Colombia: manga corta y larga, tipo lino, Oxford, cuadros y rayas, en tallas S a 5XL con pago contraentrega y envío gratis.",
    ),
}

# ── 2. camibuso ─────────────────────────────────────────────────────────────
# La frase va en el parrafo compartido de las 72 paginas con checkout, justo
# detras de la de tallas. Es el mismo mecanismo que saco al cluster de tallas
# del limbo en 7 dias.
ANCLA_TALLAS = "tabla de tallas en centímetros</a>."  # cierre de la frase de tallas del 17-sep
FRASE_CAMIBUSO = (
    ' En Colombia a la camisa polo también le decimos <a href="/camibusos-hombre" %s>camibusos</a>'
    " —se escribe con <em>s</em>, no «camibuzo»— y es exactamente la misma prenda." % MARCA
)

# Doble grafia dentro de la propia pagina de camibusos: la consulta «como se
# escribe camibuso» ya trae impresiones y la pagina no lo decia en ninguna parte.
FAQ_GRAFIA = {
    "@type": "Question",
    "name": "¿Se escribe camibuso o camibuzo?",
    "acceptedAnswer": {
        "@type": "Answer",
        "text": "Se escribe camibuso, con s. Viene de unir camisa y buso, y buso va con s. "
                "«Camibuzo» con z es un error de escritura frecuente, pero la prenda es la misma: "
                "la camisa tipo polo de cuello tejido y botones.",
    },
}


def set_meta(h, title, desc):
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, h, count=1, flags=re.S)
    for pat in (r'(<meta\s+property="og:title"\s+content=")[^"]*(")',
                r'(<meta\s+name="twitter:title"\s+content=")[^"]*(")'):
        h = re.sub(pat, lambda m: m.group(1) + title + m.group(2), h, count=1)
    for pat in (r'(<meta\s+name="description"\s+content=")[^"]*(")',
                r'(<meta\s+property="og:description"\s+content=")[^"]*(")',
                r'(<meta\s+name="twitter:description"\s+content=")[^"]*(")'):
        h = re.sub(pat, lambda m: m.group(1) + desc + m.group(2), h, count=1)
    return h


def set_h1(h, nuevo):
    """El H1 lleva un <span> oculto con el texto SEO y despues la marca visible."""
    m = re.search(r"(<h1[^>]*>)(.*?)(</h1>)", h, re.S)
    assert m, "sin H1"
    interior = m.group(2)
    sm = re.search(r'(<span style="position:absolute;width:1px[^>]*>)(.*?)(</span>)', interior, re.S)
    assert sm, "el H1 no tiene el span oculto"
    nuevo_int = interior[:sm.start(2)] + nuevo + interior[sm.end(2):]
    return h[:m.start(2)] + nuevo_int + h[m.end(2):]


def faq_grafia(h):
    """Anade la pregunta de la grafia al FAQPage si no esta."""
    def repl(m):
        try:
            d = json.loads(m.group(1))
        except Exception:
            return m.group(0)
        if d.get("@type") != "FAQPage":
            return m.group(0)
        if any("camibuzo" in (q.get("name") or "").lower() for q in d.get("mainEntity", [])):
            return m.group(0)
        d["mainEntity"].append(FAQ_GRAFIA)
        return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + "</script>"
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', repl, h, flags=re.S)


def main():
    # 1. termino cabeza
    print("== 1. termino cabeza ==")
    for f, m in META.items():
        h = io.open(f, encoding="utf-8").read()
        antes = re.search(r"<title>(.*?)</title>", h, re.S).group(1)
        assert len(m["title"]) <= 60, (f, len(m["title"]))
        assert len(m["desc"]) <= 160, (f, len(m["desc"]))
        nuevo = set_h1(set_meta(h, m["title"], m["desc"]), m["h1"])
        print("   %-36s" % f)
        print("      antes (%2d): %s" % (len(antes), antes))
        print("      ahora (%2d): %s" % (len(m["title"]), m["title"]))
        if not DRY and nuevo != h:
            io.open(f, "w", encoding="utf-8", newline="").write(nuevo)

    # 2. camibuso: frase en el parrafo compartido
    print("\n== 2. camibuso ==")
    pgs = sorted(p for p in glob.glob("*.html") if p not in ("404.html", "gracias.html"))
    n = ya = 0
    for f in pgs:
        h = io.open(f, encoding="utf-8").read()
        if MARCA in h:
            ya += 1
            continue
        if h.count(ANCLA_TALLAS) != 1:
            continue
        # en la propia pagina de camibusos el enlace seria un autoenlace
        frase = FRASE_CAMIBUSO
        if f == "camibusos-hombre.html":
            frase = frase.replace('<a href="/camibusos-hombre" %s>camibusos</a>' % MARCA,
                                  "<strong>camibusos</strong>")
        fin = h.index(ANCLA_TALLAS) + len(ANCLA_TALLAS)
        h = h[:fin] + frase + h[fin:]
        n += 1
        if not DRY:
            io.open(f, "w", encoding="utf-8", newline="").write(h)
    print("   frase de camibuso en %d paginas (%d ya la tenian)" % (n, ya))

    # 3. la grafia dentro de la propia pagina
    f = "camibusos-hombre.html"
    h = io.open(f, encoding="utf-8").read()
    nuevo = faq_grafia(h)
    if nuevo != h:
        if not DRY:
            io.open(f, "w", encoding="utf-8", newline="").write(nuevo)
        print("   FAQ «¿camibuso o camibuzo?» anadida")
    else:
        print("   FAQ de grafia: ya estaba")
    print("\n%s" % ("(DRY-RUN)" if DRY else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
