# -*- coding: utf-8 -*-
"""
Reescribe blog/pago-contraentrega-seguro.html sin la promesa de abrir el
paquete antes de pagar — 2026-09-05.

El post estaba construido sobre esa promesa: el <title> la preguntaba, un H2 la
vendia como "Ventaja 1", otro H2 daba la lista de que revisar "antes de soltar
el dinero" y una FAQ la confirmaba. Como la transportadora no la permite, se
reenfoca a lo que si se cumple: como funciona el contraentrega, que medios de
pago acepta el transportador, cuanto tarda y que pasa si la talla no queda
(cambio sin costo en 30 dias).

Se mantiene la URL (346 impresiones/mes, posicion 8,5), el H1 y las otras 11
secciones. Cada cambio va tanto en el HTML visible como en el JSON-LD.

Uso:  python reescribir_post_contraentrega_2026_09_05.py [--dry-run]
"""
import io
import re
import sys

RUTA = "blog/pago-contraentrega-seguro.html"

CAMBIOS = [
    # ── title / meta / OG / Twitter ──
    ("Contraentrega: ¿Puedes Abrir el Paquete Antes de Pagar?",
     "Pago Contraentrega en Colombia: Cómo Funciona Paso a Paso"),
    ("Cómo funciona el pago contraentrega en Colombia: si puedes abrir el paquete antes de pagar, qué pasa si no te queda la talla y qué exigirle al mensajero.",
     "Cómo funciona el pago contraentrega en Colombia: qué medios de pago acepta el transportador, cuánto tarda la entrega y qué pasa si la talla no te queda."),

    # ── H2 "Ventaja 1" + su cuerpo ──
    ("<h2>Ventaja 1: ves el producto físico antes de pagar</h2>"
     "<p>Esta es la ventaja más obvia pero más importante. En pago anticipado, ves fotos editadas. En pago contraentrega, sostienes el producto en las manos antes de soltar el dinero.</p>"
     "<p>Tocas la tela, revisas el corte, te pruebas la talla, miras las costuras. Si algo no cuadra con lo que prometieron, no compras. Esa decisión la tomas con información completa.</p>",
     "<h2>Ventaja 1: no arriesgas tu plata por adelantado</h2>"
     "<p>Esta es la ventaja más obvia pero más importante. En pago anticipado le entregas el dinero a una tienda que no conoces y esperas. En pago contraentrega no sale un peso de tu bolsillo hasta que el pedido está físicamente en tu puerta.</p>"
     "<p>Si el pedido no llega, no pagaste nada. No hay reembolso que perseguir, ni chat de soporte, ni disputa con el banco. El riesgo de la operación lo asume la tienda, que es donde debe estar.</p>"),

    # ── H2 "Qué revisar antes de soltar el dinero" -> antes de PEDIR ──
    ("<h2>Qué revisar antes de soltar el dinero</h2>"
     "<p>El poder del contraentrega está en el minuto que tienes el paquete en las manos y aún no has pagado. Aprovéchalo: abre el paquete frente al transportador y revisa con calma. Es tu derecho como comprador y ningún repartidor serio te lo va a negar. En el caso de una <a href=\"/camisas-polo-premium-colombia\" data-link=\"pilar-2026-09\">camisa polo</a>, esta es la lista rápida que recomendamos:</p>"
     "<ul><li><strong>Talla correcta:</strong> confirma que la etiqueta coincida con lo que pediste, desde la S hasta la 5XL. Si tienes dudas, pruébatela ahí mismo.</li>"
     "<li><strong>Color y modelo:</strong> que sea el que ordenaste y se parezca a la foto de la web.</li>"
     "<li><strong>Estado físico:</strong> revisa costuras, botones, cuello y que no haya manchas ni hilos sueltos.</li>"
     "<li><strong>Cantidad:</strong> si pediste un pack de varias camisas, cuéntalas antes de firmar.</li></ul>",
     "<h2>Qué confirmar antes de hacer el pedido</h2>"
     "<p>El transportador entrega el paquete cerrado y cobra en ese momento: no es él quien resuelve dudas de talla ni de color. Por eso lo que decide que aciertes pasa <em>antes</em> de que salga el envío. En el caso de una <a href=\"/camisas-polo-premium-colombia\" data-link=\"pilar-2026-09\">camisa polo</a>, esta es la lista rápida que recomendamos:</p>"
     "<ul><li><strong>Talla:</strong> mídete el pecho con una cinta y compáralo con la tabla en centímetros, de la S a la 5XL. No te guíes por la letra que usas en otra marca.</li>"
     "<li><strong>Color y modelo:</strong> mira la foto real del tono, no solo el nombre. Si dudas entre dos, pregúntanos por WhatsApp antes de pedir.</li>"
     "<li><strong>Dirección y teléfono:</strong> que estén completos y que haya alguien para recibir. Es la causa número uno de entregas fallidas.</li>"
     "<li><strong>Cantidad:</strong> si vas por un pack, confirma los colores y las tallas de cada camisa en el pedido.</li></ul>"),

    ("<p>Si algo no cuadra, devuelves el paquete en el momento y no pagas un peso. No estás obligado a recibir un producto que llegó mal, y no tienes que iniciar ningún trámite de reembolso después.",
     "<p>Y si aun así la talla no queda, la cambias sin costo dentro de los 30 días siguientes: nos escribes por WhatsApp y coordinamos el cambio. Esa es la red de seguridad real, y no depende de lo que el mensajero te permita hacer en la puerta."),

    # ── FAQ (visible + JSON-LD comparten el texto) ──
    ("¿Puedo abrir el paquete antes de pagar?", "¿Qué pasa si la talla no me queda?"),
    ("Sí. De hecho, te recomendamos abrirlo y revisar el producto frente al transportador. Si no estás satisfecho, lo devuelves ahí mismo y no pagas.",
     "La cambias sin costo dentro de los 30 días siguientes. Nos escribes por WhatsApp, coordinamos la recogida y te enviamos la talla correcta. Antes de pedir, mídete el pecho y compáralo con la tabla en centímetros para acertar de una."),
]


def main():
    dry = "--dry-run" in sys.argv
    h = io.open(RUTA, encoding="utf-8").read()
    orig = h
    for viejo, nuevo in CAMBIOS:
        n = h.count(viejo)
        if n == 0:
            raise SystemExit("!! no encontrado: %s" % viejo[:90])
        h = h.replace(viejo, nuevo)
        print("  x%d  %s" % (n, viejo[:78].replace("\n", " ")))

    # el JSON-LD tiene que seguir siendo valido
    import json
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        json.loads(m.group(1))
    resto = re.findall(r'abrir el paquete antes de pagar|antes de soltar el dinero|te pruebas la talla',
                       h, re.I)
    print("\nrestos de la promesa en el post: %s" % (resto or "ninguno"))
    if not dry and h != orig:
        io.open(RUTA, "w", encoding="utf-8", newline="").write(h)
    print("%s" % ("(DRY-RUN)" if dry else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
