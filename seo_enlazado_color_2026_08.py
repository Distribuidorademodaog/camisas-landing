# -*- coding: utf-8 -*-
"""
Enlazado interno hacia el cluster de color — 2026-08-14.

Diagnostico (GSC 13 may – 12 ago 2026):
  El hub /camisas-polo-colores-hombre YA enlazaba las 10 paginas de color, y el
  pilar /camisas-hombre-colombia tambien. El hueco estaba en otro lado: los
  blogs que hablan DE COLOR no enlazaban ninguna pagina de color.

    blog/colores-camisa-polo-segun-tono-de-piel  -> 0 enlaces a color
    blog/como-combinar-camisa-polo (pos 7,5)     -> 0 enlaces a color
    blog/tendencias-2026-camisas-polo-colombia   -> 0 enlaces a color

  Resultado: verdes, beige, rojas, grises, celestes, vinotinto y azul-marino
  recibian enlaces de solo 2-3 paginas, y las dos fuentes eran del mismo tipo
  (listado de categoria). Las paginas de color rankean pos 14-27 para consultas
  comerciales ("polos verdes", "polo azul rey") mientras el hub esta en pos 5,7.

Que hace: inserta un bloque "Camisas polo por color" (misma clase .related-block
+ .cities-block que ya usa el sitio) justo antes del bloque de ciudades, con
anchor de coincidencia exacta. No toca el cuerpo del articulo ni los scripts.

Uso:  python seo_enlazado_color_2026_08.py [--dry-run]
"""
import io
import re
import sys

COLORES = {
    "blancas":     ("camisas polo blancas",     "Blancas"),
    "negras":      ("camisas polo negras",      "Negras"),
    "azules":      ("camisas polo azules",      "Azules"),
    "azul-marino": ("camisas polo azul marino", "Azul marino"),
    "celestes":    ("camisas polo celestes",    "Celestes"),
    "verdes":      ("camisas polo verdes",      "Verdes"),
    "rojas":       ("camisas polo rojas",       "Rojas"),
    "vinotinto":   ("camisas polo vinotinto",   "Vinotinto"),
    "grises":      ("camisas polo grises",      "Grises"),
    "beige":       ("camisas polo beige",       "Beige"),
}

TODOS = list(COLORES)

# blog -> (titulo del bloque, colores a enlazar)
DESTINOS = {
    # Guia de color por tono de piel: el articulo entero trata de esto.
    "blog/colores-camisa-polo-segun-tono-de-piel.html": (
        "Ver camisas polo por color", TODOS),
    # pos 7,46 con 173 impresiones y 0 clics. Ademas las consultas que traen la
    # pagina beige son "combinar polo beige hombre" -> este es el articulo que
    # deberia estar alimentandola.
    "blog/como-combinar-camisa-polo.html": (
        "Ver camisas polo por color", TODOS),
    # Los tonos que el propio articulo nombra como tendencia 2026.
    "blog/tendencias-2026-camisas-polo-colombia.html": (
        "Los colores de tendencia, en catalogo",
        ["verdes", "vinotinto", "azul-marino", "beige", "celestes"]),
    # El cuidado cambia segun el color: el blanco se amarillea, el negro destine.
    "blog/cuidados-camisa-polo.html": (
        "Cuidado segun el color", ["blancas", "negras", "azules"]),
    # Articulo de estilos: los colores mas versatiles para cada estilo.
    "blog/estilos-camisa-polo.html": (
        "Ver camisas polo por color",
        ["blancas", "azul-marino", "beige", "grises", "celestes"]),
}

ANCLA = '<div class="related-block"><h3>Compra camisas polo en tu ciudad</h3>'
MARCA = 'data-block="color-cluster"'


def bloque(titulo, colores):
    chips = "".join(
        '<a href="/camisas-polo-%s-hombre" title="%s para hombre">%s</a>'
        % (slug, COLORES[slug][0], COLORES[slug][1]) for slug in colores)
    return ('<div class="related-block" %s><h3>%s</h3>'
            '<div class="cities-block">%s</div></div> ' % (MARCA, titulo, chips))


def main():
    dry = "--dry-run" in sys.argv
    total_links = 0
    for path, (titulo, colores) in DESTINOS.items():
        s = io.open(path, encoding="utf-8").read()
        if MARCA in s:
            print("%-52s ya tenia el bloque, se omite" % path)
            continue
        if ANCLA not in s:
            print("%-52s !! no se encontro el ancla de ciudades" % path)
            continue
        nuevo = s.replace(ANCLA, bloque(titulo, colores) + ANCLA, 1)
        assert nuevo.count("<div") - s.count("<div") == 2, "divs desbalanceados"
        assert nuevo.count("</div>") - s.count("</div>") == 2, "divs desbalanceados"
        if not dry:
            io.open(path, "w", encoding="utf-8", newline="").write(nuevo)
        total_links += len(colores)
        print("%-52s +%d enlaces de color" % (path, len(colores)))
    print("\n%s %d enlaces internos nuevos hacia el cluster de color"
          % ("DRY-RUN:" if dry else "Insertados", total_links))


if __name__ == "__main__":
    main()
