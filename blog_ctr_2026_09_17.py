# -*- coding: utf-8 -*-
"""
CTR del blog: metas con precio + contraentrega y callout de catalogo — 2026-09-17.

Motivo (GSC 19 ago - 15 sep 2026): el blog acumula 11.947 impresiones (57% del
sitio) en posicion 5-7 y da 74 clics: 6 por cada 1.000 impresiones, contra 28
de las ciudades. La respuesta informativa se la come la IA de Google; lo unico
que le queda al fragmento es parecer tienda: precio, tallas y contraentrega.

Criterio:
  * El TITLE conserva la intencion informativa (si pasa a comercial, Google lo
    saca de la consulta informativa y se pierden las impresiones). Solo se toca
    donde cabe un gancho concreto sin cambiar de tema, y siempre <= 61 chars.
  * La META lleva el gancho comercial: «+20 colores, S a 5XL, desde $86.000 en
    pack, pago contraentrega». <= 160 chars.
  * Callout de catalogo arriba del texto en los 3 articulos grandes que no lo
    tenian (elegir talla, polo vs botones, historia). Los otros 5 ya lo llevan.

Uso:  python blog_ctr_2026_09_17.py [--dry-run]
"""
import io
import re
import sys

DRY = "--dry-run" in sys.argv
TALLAS = 'data-link="tallas-2026-09"'

POSTS = {
    # 2.324 impr / pos 6,0 / CTR 0,8%
    "algodon-pique-vs-liso": (
        "Algodón Piqué vs Liso: Cuál Es Mejor y Cuál Da Menos Calor",
        "Piqué o liso: cuál es más gruesa, cuál da menos calor y cuál aguanta más lavadas. "
        "Polos en piqué: +20 colores, S a 5XL, desde $86.000 en pack, contraentrega.",
        None),
    # 1.371 impr / pos 7,3 / CTR 0,3%
    "como-combinar-camisa-polo": (
        None,
        "5 looks de camisa polo con el pantalón y los zapatos exactos: oficina, fin de semana, "
        "smart casual y noche. Polos +20 colores desde $86.000, contraentrega.",
        None),
    # 1.245 impr / pos 6,2 / CTR 0,6% — sin callout
    "como-elegir-talla-camisa-polo": (
        None,
        "Tabla de tallas de camisa polo en cm (pecho y largo) de S a 5XL y cómo medirte en casa. "
        "Tallaje colombiano real, pago contraentrega y 30 días de cambio.",
        "📏 ¿Ya sabes tu talla? Mira las <a href=\"/camisas-polo-premium-colombia\"><strong>camisas polo de S a 5XL</strong></a> "
        "o la <a href=\"/tallas-de-camisas-hombre-colombia\" %s><strong>tabla de tallas en centímetros</strong></a>: "
        "+20 colores, pago contraentrega y envío gratis a toda Colombia." % TALLAS),
    # 1.024 impr / pos 7,0 / CTR 0,5%
    "manga-larga-vs-corta": (
        None,
        "Manga larga o corta según los grados de tu ciudad (Bogotá, Medellín, Cali, costa), con tabla "
        "por temperatura. Las dos en +20 colores desde $86.000.",
        None),
    # 775 impr / pos 5,8 / 0 clics — rankea 1º para «qué es una camisa polo»; sin callout
    "polo-vs-camisa-cuello-botones": (
        "Camisa Polo vs Camisa de Botones: Diferencias y Cuál Usar",
        "Qué es una camisa polo, en qué se diferencia de la camisa de cuello con botones y cuál usar "
        "según ocasión y clima. Polos desde $86.000, contraentrega.",
        "👔 ¿Buscas la polo? Mira las <a href=\"/camisas-polo-premium-colombia\"><strong>camisas polo para hombre</strong></a>: "
        "+20 colores, tallas S a 5XL, desde $86.000 en pack, pago contraentrega y envío gratis a toda Colombia."),
    # 794 impr / pos 7,2 / CTR 0,4%
    "cuidados-camisa-polo": (
        "Cómo Cuidar la Camisa Polo: 7 Errores que Deforman el Cuello",
        "Cómo lavar, secar y planchar la camisa polo para que el cuello no se deforme ni destiña, "
        "y los 7 errores que la arruinan. Polos nuevos desde $86.000.",
        None),
    # 659 impr / pos 7,2 / CTR 0,2% — sin callout
    "historia-origen-camisa-polo": (
        None,
        "Cómo nació la camisa polo: del polo a caballo al tenis de los años 20 y su llegada a Colombia. "
        "La de hoy: +20 colores, S a 5XL, desde $86.000, contraentrega.",
        "👔 La camisa polo de hoy: <a href=\"/camisas-polo-premium-colombia\"><strong>camisas polo para hombre</strong></a> "
        "en +20 colores y tallas S a 5XL, desde $86.000 en pack, con pago contraentrega y envío gratis a toda Colombia."),
}

CALLOUT = ('<p style="background:#f0f2f5;border-left:4px solid #c9a96e;padding:14px 18px;'
           'border-radius:8px;font-size:1.02rem;margin-bottom:18px" data-callout="catalogo-2026-09">%s</p>\n')


def set_meta(h, title, desc):
    if title:
        h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, h, count=1, flags=re.S)
        for pat in (r'(<meta\s+property="og:title"\s+content=")[^"]*(")',
                    r'(<meta\s+name="twitter:title"\s+content=")[^"]*(")'):
            h = re.sub(pat, lambda m: m.group(1) + title + m.group(2), h, count=1)
    if desc:
        for pat in (r'(<meta\s+name="description"\s+content=")[^"]*(")',
                    r'(<meta\s+property="og:description"\s+content=")[^"]*(")',
                    r'(<meta\s+name="twitter:description"\s+content=")[^"]*(")'):
            h = re.sub(pat, lambda m: m.group(1) + desc + m.group(2), h, count=1)
    return h


def main():
    for slug, (title, desc, callout) in POSTS.items():
        f = "blog/%s.html" % slug
        h = io.open(f, encoding="utf-8").read()
        antes = " ".join(re.search(r"<title>(.*?)</title>", h, re.S).group(1).split())
        if title:
            assert len(title) <= 61, (slug, len(title))
        assert len(desc) <= 160, (slug, len(desc))
        nuevo = set_meta(h, title, desc)
        if callout and 'data-callout="catalogo-2026-09"' not in nuevo:
            marca = '<div class="post-body">\n'
            assert nuevo.count(marca) == 1, slug
            nuevo = nuevo.replace(marca, marca + CALLOUT % callout)
        print("%s" % slug)
        print("   title %s (%d): %s" % ("=" if not title else ">", len(title or antes), title or antes))
        print("   meta  (%d): %s" % (len(desc), desc))
        if callout:
            print("   + callout")
        if not DRY and nuevo != h:
            io.open(f, "w", encoding="utf-8", newline="").write(nuevo)
    print("\n%s" % ("(DRY-RUN)" if DRY else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
