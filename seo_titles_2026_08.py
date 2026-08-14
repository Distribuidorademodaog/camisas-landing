# -*- coding: utf-8 -*-
"""
Reescritura de <title> y <meta description> — 2026-08-14.

Motivo (datos GSC 13 may – 12 ago 2026):
  * 1.859 impresiones en top-10 (pos 5-9) produjeron 3 clics. El blog completo:
    1.427 impresiones, 8 clics, CTR 0,56% en posicion media 6,5.
  * El commit de auditoria 642d939 (13 ago) dejo 16 titulos cortados a mitad de
    frase ("...5 looks elegantes para cada"). Se reparan aqui.

Criterio de la reescritura:
  1. Ningun titulo cortado: toda frase termina.
  2. <= 62 chars visibles (el limite real de Google en movil ronda 580px).
  3. La promesa del titulo tiene que ser algo que la AI Overview NO da:
     precio real, tabla en cm, foto, disponibilidad en Colombia, contraentrega.
  4. Vocabulario del comprador, no del vendedor: el corpus de 1.954 resenas de
     la auditoria dice "tela"/"gruesa"/"delgada", no "pique".

Uso:  python seo_titles_2026_08.py [--dry-run]
"""
import io
import re
import sys

# slug -> (title, description, og_title|None, og_description|None)
# og_* = None  ->  se deja el OG que ya tenia la pagina.
PAGES = {
    # ---- 1. HUB DE COLOR: 348 impresiones, pos 5,69, CERO clics -------------
    "camisas-polo-colores-hombre.html": (
        "+20 Colores de Camisa Polo para Hombre | Foto Real y Precio",
        "Los +20 colores de camisa polo disponibles en Colombia, con foto real "
        "y precio: cuál favorece tu tono de piel y con qué combinar cada uno. "
        "Tallas S a 5XL.",
        None, None,
    ),
    # ---- 2. VERDES: 248 impresiones, pos 9,44, 1 clic ----------------------
    # Consultas reales: "polos verdes", "polo verde esmeralda", "camisa polo
    # verde oliva" -> el tono concreto es lo que buscan, va en el titulo.
    "camisas-polo-verdes-hombre.html": (
        "Camisas Polo Verdes para Hombre | Oliva, Esmeralda y Menta",
        "Camisas polo verdes para hombre en Colombia: verde oliva, esmeralda, "
        "menta y militar. Tallas S a 5XL, desde $82.500 en pack, pago "
        "contraentrega y envío gratis.",
        None, None,
    ),
    # ---- 3. BEIGE: 197 impresiones, pos 7,84, CERO clics -------------------
    # Las consultas que la traen son "outfit polo beige hombre" y "combinar
    # polo beige hombre": la intencion es COMBINAR, no comprar. El titulo tiene
    # que prometer las combinaciones o el clic no llega.
    "camisas-polo-beige-hombre.html": (
        "Camisas Polo Beige para Hombre: Cómo Combinarlas + Precio",
        "Con qué combinar una camisa polo beige: 6 outfits para oficina, fin de "
        "semana y noche. Beige, arena y camel en tallas S a 5XL desde $82.500, "
        "pago contraentrega.",
        None, None,
    ),
    # ---- 4. BLOG: 173 impresiones, pos 7,46, CERO clics --------------------
    "blog/como-combinar-camisa-polo.html": (
        "Cómo Combinar la Camisa Polo: 5 Looks con Pantalón y Zapatos",
        "5 formas de combinar tu camisa polo, con el pantalón y los zapatos "
        "exactos de cada look: oficina, fin de semana, smart casual, deportivo "
        "y noche.",
        None, None,
    ),
    # ---- 5. BLOG: 161 impresiones, pos 5,77, 1 clic ------------------------
    # "pique" tiene 0 menciones en 1.954 resenas reales; el comprador dice
    # "tela", "gruesa", "delgada". Se mantiene "pique" (es la consulta) pero la
    # promesa se escribe en el idioma del comprador.
    "blog/algodon-pique-vs-liso.html": (
        "Algodón Piqué vs Liso: Cuál Tela Escoger y Cuál Da Calor",
        "Piqué o liso: cuál tela es más gruesa, cuál da menos calor y cuál "
        "aguanta más lavadas sin deformarse. Comparativa para el clima "
        "colombiano.",
        None, None,
    ),
    # ---- 6. BLOG: 140 impresiones, pos 6,61, CERO clics --------------------
    # 48,5% de las resenas de 1-2 estrellas del sector son por talla, y el
    # sector talla pequeno. La tabla en cm es el gancho.
    "blog/como-elegir-talla-camisa-polo.html": (
        "Talla de Camisa Polo: Tabla en cm de S a 5XL (Colombia)",
        "Tabla de tallas de camisa polo con medidas exactas en cm de pecho y "
        "largo, de S a 5XL. Cómo medirte en casa y por qué la mayoría de "
        "marcas talla pequeño.",
        None, None,
    ),
    # ---- 7. BLOG: 120 impresiones, pos 6,58, 1 clic ------------------------
    # Consultas: "5xl", "talla 5xl", "que talla es 3xl en colombia" ->
    # equivalencia, no catalogo.
    "blog/tallas-grandes-3xl-4xl-5xl.html": (
        "Tallas 3XL, 4XL y 5XL en Colombia: Equivalencias en cm",
        "Qué talla es 3XL, 4XL y 5XL en Colombia: equivalencias exactas en cm y "
        "en tallaje numérico. Camisas polo hasta 5XL con pago contraentrega y "
        "envío gratis.",
        None, None,
    ),
    # ---- 8. BLOG: 91 impresiones, pos 5,99, CERO clics ---------------------
    "blog/manga-larga-vs-corta.html": (
        "Polo Manga Larga o Corta: Cuál Según tu Ciudad y Clima",
        "Manga larga o corta según los grados de tu ciudad: Bogotá, Medellín, "
        "Cali, Barranquilla y costa. Tabla por temperatura y cuál sirve para "
        "oficina.",
        None, None,
    ),
    # ---- 9. BLOG: 86 impresiones, pos 5,95, CERO clics ---------------------
    "blog/cuidados-camisa-polo.html": (
        "Cuidar la Camisa Polo: Lavarla sin que se Deforme el Cuello",
        "Cómo lavar, secar y planchar tu camisa polo para que el cuello no se "
        "deforme ni destiña. Los 7 errores que la arruinan y cómo hacerla durar "
        "años.",
        None, None,
    ),
    # ---- 10. BLOG: 76 impresiones, pos 7,00, CERO clics --------------------
    "blog/como-lavar-camisa-blanca-sin-amarillear.html": (
        "Camisa Blanca Amarillenta: 6 Trucos Caseros para Blanquearla",
        "6 trucos caseros para quitar el amarillo de las camisas blancas "
        "(bicarbonato, vinagre, sol) y evitar que vuelva. Y qué NO debes usar "
        "nunca en algodón.",
        None, None,
    ),
    # ---- 11. BLOG: 58 impresiones, pos 7,50, CERO clics --------------------
    "blog/historia-origen-camisa-polo.html": (
        "Historia de la Camisa Polo: del Tenis al Armario Moderno",
        "Cómo nació la camisa polo: del polo a caballo al tenis de los años 20 "
        "y su llegada a Colombia. Origen, evolución del cuello y por qué sigue "
        "vigente.",
        None, None,
    ),
    # ---- 12. BLOG: 56 impresiones, pos 6,64, CERO clics --------------------
    "blog/estilos-camisa-polo.html": (
        "4 Estilos de Camisa Polo: Oxford, Lino, Cuadros y Rayas",
        "Los 4 estilos de camisa polo y cuándo usar cada uno: Oxford para "
        "oficina, lino para clima cálido, cuadros y rayas para casual. Con "
        "precios en Colombia.",
        None, None,
    ),
    # ---- 13. BLOG: 45 impresiones, pos 5,80, CERO clics --------------------
    # Consulta real capturada: "vale la pena por el precio?" (pos 5).
    "blog/camisas-premium-vs-marca-costosa.html": (
        "¿Vale la Pena una Camisa de $500.000? 7 Diferencias Reales",
        "Comparamos una camisa de marca costosa ($300.000-$700.000) con una "
        "alternativa premium colombiana ($115.000): tela, costuras, cuello y "
        "durabilidad real.",
        None, None,
    ),
    # ---- 14. BLOG: 33 impresiones, pos 6,64, CERO clics --------------------
    "blog/mejores-tiendas-online-camisas-hombre-colombia.html": (
        "Las 7 Mejores Tiendas de Camisas Online en Colombia (2026)",
        "Comparamos 7 tiendas online de camisas para hombre en Colombia: "
        "precios reales, tallas hasta 5XL, tiempos de envío y cuáles tienen "
        "pago contraentrega.",
        None, None,
    ),
    # ---- 15. BLOG: 27 impresiones, pos 7,41, CERO clics --------------------
    # Consulta real capturada: "puedo abrir un paquete contra entrega antes de
    # pagar" (pos 10). Se convierte en el titulo.
    "blog/pago-contraentrega-seguro.html": (
        "Contraentrega: ¿Puedes Abrir el Paquete Antes de Pagar?",
        "Cómo funciona el pago contraentrega en Colombia: si puedes abrir el "
        "paquete antes de pagar, qué pasa si no te queda la talla y qué "
        "exigirle al mensajero.",
        None, None,
    ),

    # ======= REPARACION DE TRUNCADOS (mismo bug, fuera del top-15) ==========
    "blog/colores-camisa-polo-segun-tono-de-piel.html": (
        "Qué Color de Camisa Polo te Queda Mejor Según tu Piel",
        None, None, None,
    ),
    "blog/cuantas-camisas-polo-debe-tener-un-hombre.html": (
        "¿Cuántas Camisas Polo Debería Tener un Hombre?",
        None, None, None,
    ),
    "blog/polo-vs-camisa-cuello-botones.html": (
        "Camisa Polo vs Cuello con Botones: Cuál Usar y Cuándo",
        None, None, None,
    ),
    "blog/slim-fit-vs-regular-fit-camisa-polo.html": (
        "Slim Fit vs Regular Fit en Polos: Cuál Según tu Cuerpo",
        None, None, None,
    ),
    "blog/tendencias-2026-camisas-polo-colombia.html": (
        "Tendencias 2026 en Camisas Polo Colombia: Colores y Cortes",
        None, None, None,
    ),
    "blog/index.html": (
        "Blog Camisas Colombia | Guías de Estilo, Tallas y Cuidado",
        None, None, None,
    ),
    "polos-hombre-colombia.html": (
        "Polos Hombre Colombia | Camisas Polo de Moda desde $82.500",
        None, None, None,
    ),

    # ======= RESTO DE LA AUDITORIA: quitar "4.9*" de la meta ================
    # La auditoria dejo AggregateRating en 5.0/4 (4 resenas reales). Estas dos
    # descripciones seguian declarando 4.9 estrellas -> se elimina la mencion.
    "camisas-polo-armenia.html": (
        None,
        "Camisas polo para hombre en Armenia, Quindío: tallas S-5XL, algodón "
        "premium. Paga al recibir. Envío gratis a todo el Eje Cafetero.",
        None, None,
    ),
    "camisas-polo-santa-marta.html": (
        None,
        "Camisas polo para hombre en Santa Marta: tallas S-5XL, tela fresca para "
        "el calor. Paga al recibir, envío 1-3 días a El Rodadero y Centro.",
        None, None,
    ),
}

TITLE_MAX = 62
DESC_MAX = 160
# Un titulo valido termina en palabra completa, nunca en preposicion/articulo.
COLGANTES = {"de", "del", "la", "el", "los", "las", "para", "por", "con", "sin",
             "y", "o", "u", "a", "en", "al", "que", "un", "una", "segun", "mas",
             "cada", "tu", "su", "es", "vs"}


def check(slug, title, desc):
    errs = []
    if title is not None:
        if len(title) > TITLE_MAX:
            errs.append(f"title {len(title)} chars > {TITLE_MAX}")
        last = re.sub(r"[^\wáéíóúñ]", "", title.split()[-1].lower())
        if last in COLGANTES:
            errs.append(f'title termina en palabra colgante: "...{title[-25:]}"')
        if '"' in title:
            errs.append("title tiene comillas dobles")
    if desc is not None:
        if len(desc) > DESC_MAX:
            errs.append(f"desc {len(desc)} chars > {DESC_MAX}")
        if not desc.rstrip().endswith((".", "!", "?")):
            errs.append("desc no termina en signo de puntuacion")
        if '"' in desc:
            errs.append("desc tiene comillas dobles")
    return errs


def apply_to(path, title, desc, og_title, og_desc, dry):
    s = io.open(path, encoding="utf-8").read()
    orig = s
    if title is not None:
        s, n = re.subn(r"<title>.*?</title>", lambda m: "<title>%s</title>" % title,
                       s, count=1, flags=re.S)
        assert n == 1, "no se encontro <title> en %s" % path
    if desc is not None:
        s, n = re.subn(r'(<meta\s+name="description"\s+content=")(.*?)(">)',
                       lambda m: m.group(1) + desc + m.group(3),
                       s, count=1, flags=re.S)
        assert n == 1, "no se encontro meta description en %s" % path
    if og_title is not None:
        s = re.sub(r'(<meta\s+property="og:title"\s+content=")(.*?)(">)',
                   lambda m: m.group(1) + og_title + m.group(3), s, count=1, flags=re.S)
    if og_desc is not None:
        s = re.sub(r'(<meta\s+property="og:description"\s+content=")(.*?)(">)',
                   lambda m: m.group(1) + og_desc + m.group(3), s, count=1, flags=re.S)
    if s != orig and not dry:
        io.open(path, "w", encoding="utf-8", newline="").write(s)
    return s != orig


def main():
    dry = "--dry-run" in sys.argv
    fallos = []
    for slug, (t, d, ot, od) in PAGES.items():
        fallos += [(slug, e) for e in check(slug, t, d)]
    if fallos:
        print("VALIDACION FALLIDA:")
        for slug, e in fallos:
            print("  %-52s %s" % (slug, e))
        sys.exit(1)

    tocados = 0
    for slug, (t, d, ot, od) in PAGES.items():
        if apply_to(slug, t, d, ot, od, dry):
            tocados += 1
            print("%-54s title=%-3s desc=%-3s" % (
                slug, len(t) if t else "--", len(d) if d else "--"))
    print("\n%s %d paginas (%d definidas)" % (
        "DRY-RUN: cambiarian" if dry else "Actualizadas", tocados, len(PAGES)))


if __name__ == "__main__":
    main()
