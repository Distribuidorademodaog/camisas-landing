# -*- coding: utf-8 -*-
"""
Enlaces en prosa hacia las paginas que Google NO indexa — 2026-09-24.

La auditoria 360 de hoy inspecciono las 95 URLs del sitemap: 82 indexadas (86%)
y 13 fuera. Las 13 NO son huerfanas — reciben entre 14 y 26 enlaces internos
cada una. El problema es de donde salen: de paginas que Google rastrea poco.

Lo que funciono el 17-sep con el cluster de tallas (de «Google no reconoce esta
URL» a indexadas y rankeando 5-8 en SIETE dias) fue enlazarlas desde paginas
calientes. Aqui se repite con las que Google mas rastrea de este sitio: los
articulos de blog que rankean en posicion 5-7 y acumulan miles de impresiones.

Emparejamiento por TEMA, no por hueco libre: un enlace impertinente en un
articulo que rankea puede costar mas que el enlace que gana.

    como-combinar-camisa-polo (803 impr @7,3)     -> los 3 colores sin indexar
    colores-...-tono-de-piel (280 impr @5,0)      -> los 3 colores sin indexar
    polo-vs-camisa-cuello-botones (490 @6,1)      -> formales + matrimonio + grado
    algodon-pique-vs-liso (2.244 @6,0)            -> la guia definitiva + /guias
    como-elegir-talla-camisa-polo (892 @6,1)      -> senores (corte comodo)

⚠️ Los blogs NO se regeneran con build_landings.py (solo las 25 landings), asi
que el parrafo sobrevive. Si algun dia se corre build_blog.py desde posts.json,
esto se pierde — igual que paso con los `cc-relacionados` en agosto.

Uso:  python enlazar_sin_indexar_2026_09_24.py [--dry-run]
"""
import io
import re
import sys

DRY = "--dry-run" in sys.argv
MARCA = 'data-link="rescate-2026-09"'
A = lambda u, t: '<a href="%s" %s>%s</a>' % (u, MARCA, t)

BLOQUES = {
    "blog/como-combinar-camisa-polo": (
        "<p>Si quieres ir sobre seguro con el color, estas tres son las que mejor combinan con "
        "todo lo que tengas en el armario: " + A("/camisas-polo-azul-marino-hombre", "camisas polo azul marino")
        + ", " + A("/camisas-polo-grises-hombre", "polos grises") + " y "
        + A("/camisas-polo-celestes-hombre", "polos celestes") + ".</p>"),

    "blog/colores-camisa-polo-segun-tono-de-piel": (
        "<p>De los colores universales que funcionan con cualquier subtono, tres los tenemos en "
        "página propia con todas las tallas: " + A("/camisas-polo-azul-marino-hombre", "azul marino")
        + ", " + A("/camisas-polo-grises-hombre", "gris") + " y "
        + A("/camisas-polo-celestes-hombre", "celeste") + ".</p>"),

    "blog/polo-vs-camisa-cuello-botones": (
        "<p>Para el 20-30% de ocasiones en las que la polo no alcanza, tenemos el catálogo aparte: "
        + A("/camisas-formales-hombre", "camisas formales para hombre") + ", y por evento, "
        + A("/camisas-para-matrimonio-hombre", "camisas para matrimonio") + " y "
        + A("/camisas-para-grado-hombre", "camisas para grado") + ".</p>"),

    "blog/algodon-pique-vs-liso": (
        "<p>Si quieres el tema completo —telas, cortes, tallas y cuidados en un solo sitio—, está en "
        "la " + A("/guias/guia-definitiva-camisas-polo-hombre-colombia", "guía definitiva de la camisa polo")
        + ", dentro de nuestras " + A("/guias", "guías") + ".</p>"),

    "blog/como-elegir-talla-camisa-polo": (
        "<p>Si buscas un corte más holgado y clásico, sin el ajuste juvenil, mira las "
        + A("/camisas-polo-para-senores-hombre", "camisas polo para señores") + ".</p>"),
}

ANCLA = '<div class="post-conclusion">'


def main():
    total = 0
    for slug, bloque in BLOQUES.items():
        f = slug + ".html"
        h = io.open(f, encoding="utf-8").read()
        if MARCA in h:
            print("  = %-46s ya aplicado" % slug)
            continue
        assert h.count(ANCLA) == 1, "%s: %d anclas" % (slug, h.count(ANCLA))
        h = h.replace(ANCLA, bloque + "\n" + ANCLA)
        destinos = re.findall(r'href="(/[^"]+)"', bloque)
        print("  + %-46s -> %s" % (slug, ", ".join(d.split("/")[-1][:26] for d in destinos)))
        total += len(destinos)
        if not DRY:
            io.open(f, "w", encoding="utf-8", newline="").write(h)
    print("\n%d enlaces nuevos desde 5 articulos %s" % (total, "(DRY-RUN)" if DRY else "aplicados"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
