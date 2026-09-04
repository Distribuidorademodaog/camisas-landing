# -*- coding: utf-8 -*-
"""
Saca de la pagina 2 a las landings de color — 2026-09-04.

Diagnostico (GSC, 6 ago - 2 sep 2026): dos landings de color acumulan 544
impresiones con CERO clics, ambas varadas en posicion 11,7. El motivo es
literal: la consulta que mas las trae NO APARECE NI UNA VEZ en la pagina.

    /camisas-polo-azules-hombre   "polos azules"  30 impr  pos 31,2
                                  "polo azul"     25 impr  pos 45,9
        -> "polos azules" aparece 0 veces en el HTML

    /camisas-polo-verdes-hombre   "polos verdes"  31 impr  pos 20,6
                                  "polo verde"     9 impr  pos 38,1
        -> "polos verdes" aparece 0 veces en el HTML

El plural corto es como busca la gente; el sitio solo dice "camisas polo
azules". Las variantes largas ya rankean 9-11 ("camisa polo azul claro" 10,1,
"camisa polo verde claro" 9,0), asi que el title conserva "Camisa Polo <color>"
y suma el plural corto delante.

Las descriptions se rehacen con lo que SI funciona en este sitio: las paginas
de ciudad, que con el mismo tipo de posicion (8-9) sacan 2,6-4,7% de CTR
poniendo precio, contraentrega y envio gratis por delante.

Toca el HTML desplegado Y la fuente en _landings/ (gitignored), para que no se
pierda si algun dia se vuelve a correr build_landings.py.

Uso:  python seo_color_plural_2026_09_04.py [--dry-run]
"""
import io
import json
import re
import sys

PAGS = {
    "camisas-polo-azules-hombre": {
        "title_viejo": "Camisas Polo Azules para Hombre | El Color que Nunca Falla",
        "title": "Polos Azules para Hombre | Camisa Polo Azul Marino y Celeste",
        "tw_title_viejo": "Camisas Polo Azules para Hombre en Colombia",
        "tw_title": "Polos Azules para Hombre en Colombia | Camisa Polo Azul",
        "bc_viejo": '"name": "Camisas Polo Azules para Hombre"',
        "bc": '"name": "Polos Azules para Hombre"',
        "desc": ("Polos azules para hombre en Colombia: azul marino, rey, celeste "
                 "y petróleo en algodón piqué. Tallas S a 5XL desde $82.500 en "
                 "pack, contraentrega y envío gratis."),
        "og_desc": ("Polos azules para hombre: marino, rey, celeste y petróleo en "
                    "algodón piqué. El color más versátil del clóset. Tallas S a "
                    "5XL, contraentrega y envío gratis a toda Colombia."),
        "tw_desc": ("El azul es el color más seguro que existe. Polos azules "
                    "marino, rey, celeste y petróleo en algodón piqué. S-5XL "
                    "desde $82.500. Paga al recibir."),
        "keywords": ("polos azules, polos azules para hombre, polo azul, camisas "
                     "polo azules hombre, camisa polo azul marino, camisa polo "
                     "azul rey, polo celeste hombre, camisa polo azul petroleo, "
                     "con que combinar polo azul, pago contraentrega"),
        "h1sr": ("Polos azules para hombre en Colombia: azul marino, rey, celeste "
                 "y petroleo en algodon pique premium, tallas S a 5XL, desde "
                 "82.500 pesos en pack, pago contraentrega y envio gratis."),
        "h2_viejo": "Camisas polo azules<br><em>el color que nunca falla</em>",
        "h2": "Polos azules para hombre<br><em>el color que nunca falla</em>",
        "p_viejo": ("Si tuvieras que elegir un solo color de polo para toda la "
                    "vida, la respuesta es azul."),
        "p": ("Si tuvieras que elegir un solo color de polo para toda la vida, "
              "la respuesta es azul. Nuestros polos azules van del marino al "
              "celeste."),
    },
    "camisas-polo-verdes-hombre": {
        "title_viejo": "Camisas Polo Verdes para Hombre | Oliva, Esmeralda y Menta",
        "title": "Polos Verdes para Hombre | Camisa Polo Verde Oliva y Militar",
        "tw_title_viejo": None,   # se resuelve leyendo el HTML
        "tw_title": "Polos Verdes para Hombre en Colombia | Camisa Polo Verde",
        "bc_viejo": '"name": "Camisas Polo Verdes para Hombre"',
        "bc": '"name": "Polos Verdes para Hombre"',
        "desc": ("Polos verdes para hombre en Colombia: verde oliva, esmeralda, "
                 "menta y militar en algodón piqué. Tallas S a 5XL desde $82.500 "
                 "en pack, contraentrega y envío gratis."),
        "og_desc": ("Polos verdes para hombre: oliva, esmeralda, menta y militar "
                    "en algodón piqué. El color de tendencia del año. Tallas S a "
                    "5XL, contraentrega y envío gratis a toda Colombia."),
        "tw_desc": ("El verde es el color que manda en 2026. Polos verdes oliva, "
                    "esmeralda, menta y militar en algodón piqué. S-5XL desde "
                    "$82.500. Paga al recibir."),
        "keywords": ("polos verdes, polos verdes para hombre, polo verde, camisas "
                     "polo verdes hombre, camisa polo verde oliva, polo verde "
                     "esmeralda, camisa polo verde militar, polo verde menta, "
                     "con que combinar polo verde, pago contraentrega"),
        "h1sr": ("Polos verdes para hombre en Colombia: verde oliva, esmeralda, "
                 "menta y militar en algodon pique premium, tallas S a 5XL, desde "
                 "82.500 pesos en pack, pago contraentrega y envio gratis."),
        "h2_viejo": "Camisas polo verdes<br><em>el color que manda en 2026</em>",
        "h2": "Polos verdes para hombre<br><em>el color que manda en 2026</em>",
        "p_viejo": ("El verde dejo de ser un color de nicho para convertirse en "
                    "el tono de moda del ano."),
        "p": ("El verde dejo de ser un color de nicho para convertirse en el tono "
              "de moda del ano. Nuestros polos verdes van del oliva al esmeralda."),
    },
}


def sub1(pat, repl, s, label, flags=0):
    nuevo, n = re.subn(pat, lambda m: repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit("!! [%s] patron no encontrado (%d)" % (label, n))
    return nuevo


def exacto(viejo, nuevo, s, label, veces):
    if s.count(viejo) != veces:
        raise SystemExit("!! [%s] esperaba %d ocurrencias, hay %d"
                         % (label, veces, s.count(viejo)))
    return s.replace(viejo, nuevo)


def aplicar(slug, c, dry):
    html_p = "%s.html" % slug
    sec_p = "_landings/%s.section.html" % slug
    meta_p = "_landings/%s.meta.json" % slug

    h = io.open(html_p, encoding="utf-8").read()
    if c["title"] in h:
        print("%-30s ya aplicado" % slug)
        return

    # Campo por campo, no por cadena compartida: en verdes el <title> se
    # reescribio en agosto pero og:title y el name del WebPage se quedaron con
    # el viejo, asi que las tres NO coinciden entre si.
    h = sub1(r"<title>.*?</title>", "<title>%s</title>" % c["title"], h, "title", re.S)
    h = sub1(r'<meta property="og:title" content="[^"]*">',
             '<meta property="og:title" content="%s">' % c["title"], h, "og:title")
    h, n = re.subn(r'("@type": "WebPage".*?"name": ")[^"]*(")',
                   lambda m: m.group(1) + c["title"] + m.group(2),
                   h, count=1, flags=re.S)
    if n != 1:
        raise SystemExit("!! [webpage:name] no encontrado en %s" % slug)
    h = sub1(r'<meta name="twitter:title" content="[^"]*">',
             '<meta name="twitter:title" content="%s">' % c["tw_title"], h, "twitter:title")
    h = exacto(c["bc_viejo"], c["bc"], h, "breadcrumb", 1)
    h = sub1(r'<meta name="description" content="[^"]*">',
             '<meta name="description" content="%s">' % c["desc"], h, "desc")
    h = sub1(r'<meta property="og:description" content="[^"]*">',
             '<meta property="og:description" content="%s">' % c["og_desc"], h, "og:desc")
    h = sub1(r'<meta name="twitter:description" content="[^"]*">',
             '<meta name="twitter:description" content="%s">' % c["tw_desc"], h, "tw:desc")
    h = sub1(r'<meta name="keywords" content="[^"]*">',
             '<meta name="keywords" content="%s">' % c["keywords"], h, "keywords")
    m = re.search(r'(<h1 class="hero-title"><span style="[^"]*">)(.*?)(</span>)', h, re.S)
    if not m:
        raise SystemExit("!! [%s] sin span oculto en el H1" % slug)
    h = h[:m.start(2)] + c["h1sr"] + h[m.end(2):]
    # cuerpo: el H2 principal y la entradilla, en el HTML y en la fuente
    h = exacto(c["h2_viejo"], c["h2"], h, "h2", 1)
    h = exacto(c["p_viejo"], c["p"], h, "parrafo", 1)

    s = io.open(sec_p, encoding="utf-8").read()
    s = exacto(c["h2_viejo"], c["h2"], s, "h2 (section)", 1)
    s = exacto(c["p_viejo"], c["p"], s, "parrafo (section)", 1)

    j = json.load(io.open(meta_p, encoding="utf-8"))
    j.update({"title": c["title"], "meta_description": c["desc"],
              "keywords": c["keywords"], "hero_h1_sr": c["h1sr"],
              "og_title": c["title"], "og_description": c["og_desc"],
              "twitter_title": c["tw_title"], "twitter_description": c["tw_desc"],
              "webpage_name": c["title"], "breadcrumb_name": c["bc"][9:-1]})

    if not dry:
        io.open(html_p, "w", encoding="utf-8", newline="").write(h)
        io.open(sec_p, "w", encoding="utf-8", newline="").write(s)
        io.open(meta_p, "w", encoding="utf-8", newline="").write(
            json.dumps(j, ensure_ascii=False, indent=2) + "\n")
    print("%-30s title -> %s" % (slug, c["title"]))


def main():
    dry = "--dry-run" in sys.argv
    for slug, c in PAGS.items():
        aplicar(slug, c, dry)
    print("\n%s" % ("(DRY-RUN, no se escribio nada)" if dry else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
