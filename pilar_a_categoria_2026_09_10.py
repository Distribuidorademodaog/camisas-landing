# -*- coding: utf-8 -*-
"""
Convierte la pilar de COMPARATIVA a pagina de CATEGORIA — 2026-09-10.

Hallazgo de la auditoria 360 del 09-10: la familia de terminos cabeza («camisas
polo», «polos para hombre»…, 711 impresiones) la capturan /camisas-hombre-colombia
(577 impr, pos 51) y /camisas-polo-juveniles-hombre (384, pos 46). La pilar NO
aparece, pese a tener 64 enlaces entrantes —mas que ninguna pagina del sitio— y
pese a decir «camisas polo» 31 veces, mas que sus rivales.

La causa no es enlazado ni densidad: son sus ENCABEZADOS. Cuatro de sus doce H2
son comparativos («Que es una camisa polo estilo premium», «Original vs
alternativa: las diferencias reales», «Por que elegir la alternativa colombiana»).
Es la vieja pagina «alternativa a la marca cara» renombrada en el de-branding de
julio, con la estructura intacta. Google la clasifica por lo que es y la rankea
13,6 para «camisa premium» / «polo premium», no para «camisas polo».

Que hace: sustituye los tres bloques comparativos por tres bloques de CATALOGO
—por color, por talla, por ocasion— y reescribe el hero y las dos FAQ defensivas.
Efecto secundario buscado: el clusters de tallas (3XL/4XL/5XL/XXL/tabla, las 5 sin
indexar segun la misma auditoria) pasa a estar enlazado en prosa desde una pagina
que Google si rastrea, no solo desde una lista al pie.

Se conservan intactos los bloques que ya eran de categoria (calidad, colores y
estilos, tallas, contraentrega, ciudad, historia, combinar) y todos sus enlaces.
La seccion editada es la unica de la pilar (`id="camisas-polo-premium"`), que
build_landings.py reemplaza en cada landing: NO se propaga a las otras 26.

Uso:  python pilar_a_categoria_2026_09_10.py [--dry-run]
"""
import io
import re
import sys

RUTA = "camisas-polo-premium-colombia.html"
CARR = "  <!-- ═══════ CARRUSEL ═══════ -->"

# ── hero ────────────────────────────────────────────────────────────────────
HERO_VIEJO = (
    '<h2 class="sec-title sec-title-light">Camisas polo estilo<br><em>Premium en Colombia</em></h2>\n'
    '      <p class="sec-subtitle sec-subtitle-light">La alternativa colombiana premium: el mismo corte clasico y calidad de tela del polo que todos conocen, a precio justo, con tallaje real y pago contraentrega.</p>')
HERO_NUEVO = (
    '<h2 class="sec-title sec-title-light">Camisas polo<br><em>para hombre en Colombia</em></h2>\n'
    '      <p class="sec-subtitle sec-subtitle-light">Mas de 20 colores, tallas de la S a la 5XL con tallaje colombiano real, envio gratis a todo el pais y pago contraentrega.</p>')

INTRO_VIEJA = re.compile(
    r'<p>Si buscas <strong>camisas polo estilo premium en Colombia</strong>.*?llega a tu puerta\.</p>', re.S)
INTRO_NUEVA = (
    '<p>Este es el catalogo completo de <strong>camisas polo para hombre</strong> de '
    'Camisas Colombia: todos los colores, todas las tallas y todos los estilos, en el '
    'mismo <strong>algodon pique premium</strong> y al mismo precio por unidad. Puedes '
    'entrar directo a lo que buscas —por color, por talla o por ocasion— o armar un '
    'pack de varias y bajar el precio por camisa hasta <strong>$82.500</strong>. Todo '
    'con envio gratis a los 32 departamentos y pago contraentrega.</p>')

# ── los tres bloques de catalogo que sustituyen a los comparativos ──────────
COLOR = """<h2>Camisas polo por color</h2>
      <p>Manejamos <strong>mas de 20 colores</strong>, todos en la misma tela y el mismo tallaje, asi que puedes mezclar sin sorpresas. Cada color tiene su propia pagina con foto real del tono, porque en pantalla los colores enganan:</p>
      <ul>
        <li><strong>Los cuatro basicos</strong> que resuelven el 80% del guardarropa: <a href="/camisas-polo-blancas-hombre">blancas</a>, <a href="/camisas-polo-negras-hombre">negras</a>, <a href="/camisas-polo-azul-marino-hombre">azul marino</a> y <a href="/camisas-polo-grises-hombre">grises</a>.</li>
        <li><strong>Los frescos</strong>, para tierra caliente y uso diario: <a href="/camisas-polo-celestes-hombre">celestes</a>, <a href="/camisas-polo-azules-hombre">azules</a> y <a href="/camisas-polo-beige-hombre">beige</a>.</li>
        <li><strong>Los de caracter</strong>, cuando quieres que te noten: <a href="/camisas-polo-verdes-hombre">verdes</a>, <a href="/camisas-polo-rojas-hombre">rojas</a> y <a href="/camisas-polo-vinotinto-hombre">vinotinto</a>.</li>
      </ul>
      <p>Si prefieres verlos todos juntos antes de decidir, esta la <a href="/camisas-polo-colores-hombre">paleta completa con foto real de cada tono</a> y una guia de <a href="/blog/colores-camisa-polo-segun-tono-de-piel">que color favorece segun tu tono de piel</a>.</p>"""

TALLA = """<h2>Camisas polo por talla, de la S a la 5XL</h2>
      <p>Usamos <strong>tallaje colombiano real</strong>, con medidas pensadas para la contextura local y no el tallaje importado que suele quedar una talla mas pequeno. Cada talla grande tiene su propia pagina con las medidas exactas en centimetros:</p>
      <ul>
        <li><a href="/camisas-xxl-hombre">Camisas polo XXL</a> — de 114 a 122 cm de pecho.</li>
        <li><a href="/camisas-3xl-hombre">Camisas polo 3XL</a> — de 122 a 130 cm.</li>
        <li><a href="/camisas-4xl-hombre">Camisas polo 4XL</a> — de 130 a 138 cm.</li>
        <li><a href="/camisas-5xl-hombre">Camisas polo 5XL</a> — de 138 a 146 cm, la talla mas grande que manejamos.</li>
      </ul>
      <p>De la S a la XL el precio es el mismo, y en tallas grandes tambien: no cobramos mas por mas tela. Antes de pedir, midete el pecho con una cinta y comparalo con la <a href="/tallas-de-camisas-hombre-colombia">tabla de tallas en centimetros</a>; si prefieres verlas todas en un solo sitio, ahi esta el catalogo de <a href="/camisas-hombre-tallas-grandes">camisas en tallas grandes</a>. Si la talla no queda, la cambias sin costo dentro de los 30 dias.</p>"""

OCASION = """<h2>Camisas polo por ocasion y estilo</h2>
      <p>La misma prenda cambia de registro segun el color, el estampado y con que la combines. Estas son las paginas por uso, para que llegues directo a la que necesitas:</p>
      <ul>
        <li><strong>Oficina y trabajo:</strong> <a href="/camisas-para-oficina-hombre-colombia">camisas para oficina</a>, <a href="/camisas-oxford-hombre-colombia">Oxford</a> y <a href="/camisas-formales-hombre">formales</a>.</li>
        <li><strong>Eventos:</strong> <a href="/camisas-para-matrimonio-hombre">matrimonio</a>, <a href="/camisas-para-grado-hombre">grado</a>, <a href="/camisas-para-eventos-hombre">eventos en general</a> y <a href="/camisas-semiformales-hombre">semiformales</a>.</li>
        <li><strong>Dia a dia:</strong> <a href="/camisas-casuales-hombre-colombia">casuales</a>, <a href="/camisas-manga-corta-hombre">manga corta</a> y <a href="/camisas-manga-larga-contraentrega">manga larga</a>.</li>
        <li><strong>Por tela y estampado:</strong> <a href="/camisas-tipo-lino-hombre">tipo lino</a>, <a href="/camisas-100-algodon-hombre">100% algodon</a>, <a href="/camisas-cuadros-hombre">a cuadros</a> y <a href="/camisas-de-rayas-hombre">de rayas</a>.</li>
        <li><strong>Por edad:</strong> <a href="/camisas-polo-juveniles-hombre">juveniles</a> y <a href="/camisas-polo-para-senores-hombre">para senores</a>.</li>
      </ul>
      <p>Si vas a llevar varias, el <a href="/pack-camisas-polo-hombre">pack de camisas polo</a> deja cada una desde $82.500; para volumen esta <a href="/camisas-polo-por-mayor-colombia">venta por mayor</a> y si lo que buscas es el precio mas bajo, <a href="/camisas-polo-baratas-colombia">camisas polo baratas</a>. Tambien puedes <a href="/camibusos-hombre">buscarlas como camibusos</a>, que es como les decimos en buena parte del pais.</p>"""

# ── FAQ: las dos defensivas pasan a ser de catalogo ─────────────────────────
FAQ_VIEJA_1 = re.compile(
    r'<h3>¿Son camisas de marca costosaes\?</h3>\s*<p>.*?</p>', re.S)
FAQ_NUEVA_1 = (
    '<h3>¿Cuantos colores tienen y estan todos en todas las tallas?</h3>\n'
    '        <p>Manejamos <strong>mas de 20 colores</strong> y todos comparten la misma tela y el mismo tallaje. '
    'La disponibilidad por talla cambia con el inventario: los basicos (blanco, negro, azul marino, gris) suelen estar '
    'completos de la S a la 5XL, y los tonos de temporada rotan. En la <a href="/camisas-polo-colores-hombre">paleta '
    'completa</a> ves cada tono con foto real.</p>')

FAQ_VIEJA_2 = re.compile(
    r'<h3>¿En que se diferencia del polo original\?</h3>\s*<p>.*?</p>', re.S)
FAQ_NUEVA_2 = (
    '<h3>¿Cual estilo elijo: pique, Oxford o lino?</h3>\n'
    '        <p>El <strong>algodon pique</strong> es el polo clasico y el mas versatil: sirve para oficina y para fin de semana. '
    'El <a href="/camisas-oxford-hombre-colombia">Oxford</a> es mas formal, ideal si trabajas en ambiente ejecutivo. '
    'El <a href="/camisas-tipo-lino-hombre">tipo lino</a> es el mas fresco y el que mejor funciona en tierra caliente. '
    'Los tres van en el mismo tallaje S a 5XL.</p>')

FAQ_CALIDAD_VIEJA = re.compile(
    r'(<h3>¿La calidad es realmente buena\?</h3>\s*<p>.*?)(</p>)', re.S)
FAQ_CALIDAD_EXTRA = (
    r'\1 Si quieres el detalle de en que se nota la calidad de una tela frente a otra, '
    r'lo desglosamos en <a href="/blog/camisas-premium-vs-marca-costosa">esta comparativa</a>.\2')


def main():
    dry = "--dry-run" in sys.argv
    h = io.open(RUTA, encoding="utf-8").read()
    if "Camisas polo por color" in h:
        print("ya aplicado")
        return

    m = re.search(r'  <section class="sec sec-light" id="camisas-polo-premium">.*?(?=\n\n'
                  + re.escape(CARR) + r')', h, re.S)
    if not m:
        raise SystemExit("!! no se encontro la seccion unica de la pilar")
    sec = m.group(0)
    enlaces_antes = len(re.findall(r'<a\b', sec))

    # 1. hero
    if HERO_VIEJO not in sec:
        raise SystemExit("!! hero no encontrado")
    sec = sec.replace(HERO_VIEJO, HERO_NUEVO, 1)
    sec, n = INTRO_NUEVA and INTRO_VIEJA.subn(lambda _: INTRO_NUEVA, sec, count=1)
    if n != 1:
        raise SystemExit("!! intro no encontrada")

    # 2. los tres bloques comparativos -> catalogo, por posicion entre <h2>
    partes = re.split(r'(?=<h2)', sec)
    titulos = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", (re.search(r'<h2[^>]*>(.*?)</h2>', p, re.S).group(1) if re.search(r'<h2', p) else "")))
               for p in partes]
    objetivo = ["Que es una camisa polo estilo premium",
                "Original vs alternativa: las diferencias reales",
                "Por que elegir la alternativa colombiana premium"]
    nuevos = [COLOR, TALLA, OCASION]
    for viejo, nuevo in zip(objetivo, nuevos):
        idx = [i for i, t in enumerate(titulos) if t.strip() == viejo]
        if len(idx) != 1:
            raise SystemExit("!! bloque '%s': %d coincidencias" % (viejo, len(idx)))
        cola = partes[idx[0]][len(partes[idx[0]].rstrip()):]  # respeta el espaciado final
        partes[idx[0]] = nuevo + "\n\n      " + cola.lstrip("\n")
    sec = "".join(partes)

    # 3. FAQ
    for pat, rep in ((FAQ_VIEJA_1, FAQ_NUEVA_1), (FAQ_VIEJA_2, FAQ_NUEVA_2)):
        sec, k = pat.subn(lambda _: rep, sec, count=1)
        if k != 1:
            raise SystemExit("!! FAQ no encontrada")
    sec, k = FAQ_CALIDAD_VIEJA.subn(FAQ_CALIDAD_EXTRA, sec, count=1)
    if k != 1:
        raise SystemExit("!! FAQ de calidad no encontrada")

    # tambien el titulo del bloque de FAQ y el kicker, que decian "estilo premium"
    sec = sec.replace("<h2>Preguntas frecuentes sobre camisas polo estilo premium</h2>",
                      "<h2>Preguntas frecuentes sobre camisas polo</h2>", 1)
    sec = sec.replace('<div class="sec-kicker kicker-gold">Camisas polo &middot; Estilo Premium</div>',
                      '<div class="sec-kicker kicker-gold">Catalogo &middot; Camisas polo para hombre</div>', 1)

    enlaces_despues = len(re.findall(r'<a\b', sec))
    nuevo_html = h[:m.start()] + sec + h[m.end():]
    assert nuevo_html.count("<section") == h.count("<section"), "secciones alteradas"
    assert nuevo_html.count("</div>") - nuevo_html.count("<div") == h.count("</div>") - h.count("<div"), "balance de div roto"

    pal = lambda x: len(re.sub(r"<[^>]+>", " ", x).split())
    print("H2 comparativos sustituidos : 3")
    print("enlaces internos            : %d -> %d" % (enlaces_antes, enlaces_despues))
    print("palabras de la seccion      : %d -> %d" % (pal(m.group(0)), pal(sec)))
    if not dry:
        io.open(RUTA, "w", encoding="utf-8", newline="").write(nuevo_html)
    print("\n%s" % ("(DRY-RUN, no se escribio)" if dry else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
