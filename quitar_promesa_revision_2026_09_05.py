# -*- coding: utf-8 -*-
"""
Quita la promesa de "revisar/probar/abrir la prenda ANTES de pagar" — 2026-09-05.

Motivo (decision del negocio): la transportadora no permite abrir el paquete
antes de pagar, asi que el sitio prometia algo que el mensajero no deja cumplir
y eso termina en disputas en la puerta.

QUE SE QUEDA: el pago contraentrega en si ("pagas cuando el domiciliario llega
a tu puerta", "pago contraentrega", "paga al recibir", "sin anticipos"), el
envio gratis y los 30 dias de cambio. Es el modelo de negocio y esta hasta en
el H1.
QUE SE VA: toda promesa de inspeccionar, probarse o abrir la prenda como
condicion previa al pago.
CON QUE SE REEMPLAZA: lo que si se puede cumplir — pagas al recibir, y si la
talla no queda, cambio sin costo dentro de los 30 dias.

Alcance medido antes de tocar nada: 124 frases distintas, 241 ocurrencias,
73 archivos.

NO se toca (falsos positivos verificados a mano):
  - "Descuentos exclusivos, solo si los agregas ahora antes de pagar" (order
    bumps del checkout).
  - consejos de compra y cuidado: "revisa el gramaje", "revisa tus polos un par
    de veces al año", "revisa nuestra guia de tallas", "probarse la camisa bajo
    luz artificial de tienda" (habla de tiendas fisicas, no de nuestra entrega).

Uso:  python quitar_promesa_revision_2026_09_05.py [--dry-run]
"""
import glob
import io
import os
import re
import sys

# (patron, reemplazo). Orden: de mas especifico a mas general.
REGLAS = [
    # ── plantilla de las paginas de ciudad (la mas repetida) ──
    (r"Cuando el domiciliario llegue a tu puerta, revisas la camisa y pagas en efectivo o con datafono\.",
     "Cuando el domiciliario llegue a tu puerta, pagas en efectivo o con datafono."),

    # ── "Pagas solo cuando ... llega a tu puerta, revisas X, y confirmas ..." ──
    (r"Pagas solo cuando el domiciliario llega a tu puerta, revisas [^.]*?y confirmas que (?:te gusta|te queda|todo esta bien|te convence)\.",
     "Pagas solo cuando el domiciliario llega a tu puerta, sin anticipos."),
    (r"Pagas el pack completo solo cuando el domiciliario llega a tu puerta, revisas [^.]*?y confirmas que todo esta bien\.",
     "Pagas el pack completo solo cuando el domiciliario llega a tu puerta, sin anticipos."),
    (r"pagas contraentrega, solo cuando el domiciliario llega a tu puerta, revisas [^.]*?y confirmas que te gusta\.",
     "pagas contraentrega, solo cuando el domiciliario llega a tu puerta."),
    (r"solo entregas el dinero cuando el domiciliario llega, revisas la camisa y confirmas que te gusta\.",
     "solo entregas el dinero cuando el domiciliario llega."),
    (r"solo sueltas el dinero cuando el domiciliario llega, revisas [^.]*?y confirmas que te convence\.",
     "solo sueltas el dinero cuando el domiciliario llega."),
    (r", o sea que sueltas el dinero solo cuando el domiciliario llega a tu puerta y ya revisaste la prenda\.",
     ", o sea que sueltas el dinero solo cuando el domiciliario llega a tu puerta."),

    # ── "Recibes el paquete, revisas X, y pagas ..." ──
    (r"Recibes el paquete, revisas [^.]*?, y pagas en efectivo, Nequi, Daviplata o transferencia solo si te convence\.",
     "Recibes el paquete y pagas en efectivo, Nequi, Daviplata o transferencia."),
    (r"Recibes el paquete, ves el tono real del celeste a la luz del dia, revisas la tela y la talla, y pagas en efectivo, Nequi, Daviplata o transferencia solo si te convence\.",
     "Recibes el paquete y pagas en efectivo, Nequi, Daviplata o transferencia."),
    (r"Recibes la camisa, revisas [^.]*?, y pagas en efectivo, Nequi, Daviplata o transferencia solo si te convence\.",
     "Recibes la camisa y pagas en efectivo, Nequi, Daviplata o transferencia."),
    (r"Recibes, revisas [^.]*?, y pagas en efectivo, Nequi, Daviplata o transferencia solo si te convence\.",
     "Recibes y pagas en efectivo, Nequi, Daviplata o transferencia."),
    (r"recibes el paquete, revisas [^.]*?, y pagas solo si te convence, en efectivo, Nequi, Daviplata o transferencia\.",
     "recibes el paquete y pagas en efectivo, Nequi, Daviplata o transferencia."),
    (r"recibes el paquete, ves el color real bajo tu propia luz, revisas la tela y la talla, y pagas en efectivo, Nequi, Daviplata o transferencia solo si te convence\.",
     "recibes el paquete y pagas en efectivo, Nequi, Daviplata o transferencia."),
    (r"recibes el paquete, revisas que el tono de rojo sea el que esperabas, confirmas la talla y solo entonces pagas\.",
     "recibes el paquete y pagas en ese momento."),
    (r"recibes el pack, revisas colores y tallas, y pagas al momento\.",
     "recibes el pack y pagas al momento."),
    (r"Recibes tu polo, revisas la tela, confirmas que la talla te queda bien para la oficina y luego pagas\.",
     "Recibes tu polo y pagas en ese momento."),

    # ── "revisas X y pagas solo si ..." ──
    (r"revisas la camisa en la puerta de tu casa y pagas solo si te convence\.",
     "pagas en la puerta de tu casa, sin adelantar nada."),
    (r"revisas la tela, la manga y la talla, y pagas en efectivo, Nequi, Daviplata o transferencia solo si te convence\.",
     "pagas en efectivo, Nequi, Daviplata o transferencia."),
    (r"revisas tu camisa de algod&oacute;n en la puerta de tu casa, confirmas que te gusta la tela y que te queda, y solo entonces pagas",
     "pagas en la puerta de tu casa"),
    (r"revisas tu camisa Oxford, confirmas que te gusta y que te queda, y recien ahi pagas\.",
     "pagas en la puerta de tu casa, sin adelantar nada."),
    (r"Revisas tu camisa de rayas, confirmas que te gusta el patron y que te queda bien, y luego pagas\.",
     "Pagas en la puerta de tu casa, sin adelantar nada."),
    (r"Revisas tu polo blanca con calma, confirmas la calidad y el ajuste, y luego pagas\.",
     "Pagas en la puerta de tu casa, sin adelantar nada."),
    (r"revisas la camisa cuando llega y pagas solo si te queda\.",
     "pagas cuando la camisa llega a tu puerta."),
    (r"revisas la camisa en tu puerta y solo pagas si te convence",
     "pagas en tu puerta, sin adelantar nada"),
    (r"revisas el tono exacto del beige, la tela y la talla en tu puerta, y solo pagas si te convence\.",
     "pagas en tu puerta, sin adelantar nada."),
    (r"revisas tu camisa y pagas solo cuando la recibes\.",
     "pagas solo cuando recibes la camisa."),
    (r"revisas tu polo blanca en la puerta y pagas solo cuando la recibes\.",
     "pagas en la puerta, solo cuando recibes."),
    (r"cuando llega el paquete revisas la camisa y pagas contraentrega\.",
     "pagas contraentrega cuando llega el paquete."),
    (r"pagas solo cuando recibes y revisas la camisa\.", "pagas solo cuando recibes."),
    (r"pagas solo cuando recibes y confirmas que te queda\.", "pagas solo cuando recibes."),
    (r"Pagas directo al transportador cuando recibes y revisas tu camisa, sin (adelantar nada|anticipos)\.",
     "Pagas directo al transportador cuando recibes, sin anticipos."),
    (r"revisas el producto físicamente, te lo pruebas, y solo pagas si te queda\.",
     "pagas al recibir, sin adelantar nada."),
    (r"el domiciliario llega a tu puerta, te pruebas o revisas la camisa, confirmas que la talla te queda, y",
     "el domiciliario llega a tu puerta y"),
    (r"El domiciliario llega, revisas la prenda, confirmas que te gusta y que te queda, y solo entonces pagas",
     "El domiciliario llega y pagas"),
    (r"Abres el paquete, revisas la tela, el color y la talla, y", "Recibes el paquete y"),
    (r", confirmas que te gusta el color, que la textura es la que esperabas y que te queda bien, y solo entonces pagas\.",
     " y pagas en ese momento."),

    # ── "puedes revisar la camisa antes de pagarla" y variantes ──
    (r"(?:Y todo respaldado por |Esa red de seguridad es la que le da tranquilidad a )?Puedes revisar la camisa antes de pagarla, muchos [^.]*\.",
     "Puedes cambiar la talla sin costo dentro de los 30 dias."),
    (r"Por eso puedes revisar la camisa antes de pagarla, muchos [^.]*\.",
     "Y si la talla no queda, la cambias sin costo dentro de los 30 dias."),
    (r"Con la opcion de revisar la camisa antes de pagarla, muchos de ellos senores y familias que compran para papa o el abuelo, sabemos",
     "Como muchos de nuestros clientes son senores y familias que compran para papa o el abuelo, sabemos"),
    (r"Por eso m&aacute;s de puedes revisarla antes de pagar y repiten pedido\.",
     "Por eso nuestros clientes repiten pedido."),
    (r"Esa red de seguridad es la que le da tranquilidad a puedes revisar la camisa antes de pagarla\.",
     "Esa red de seguridad es la que da tranquilidad al comprar en linea."),
    (r"Y todo respaldado por puedes revisar la camisa antes de pagarla\.",
     "Y todo respaldado por 30 dias de cambio sin costo."),
    (r"Es la forma mas segura de comprar camisas a cuadros para hombre por internet, y la razon por la que puedes revisar la camisa antes de pagarla\.",
     "Es la forma mas segura de comprar camisas a cuadros para hombre por internet."),
    (r"Es la razon por la que puedes revisar la camisa antes de pagarla comprando packs\.",
     "Es la razon por la que tantos clientes compran packs."),
    (r"Es la razon por la que puedes revisar la camisa antes de pagarla\.",
     "Es la razon por la que comprar en linea deja de ser un riesgo."),
    (r"Puedes revisar la camisa antes de pagarla justamente por esa consistencia en la calidad\.",
     "Esa consistencia en la calidad es la que se nota al primer uso."),
    (r"Puedes revisar la camisa antes de pagarla, justamente por eso: prendas",
     "Y justamente por eso: prendas"),
    (r"Puedes revisar la camisa antes de pagarla comprando asi, sin riesgo\.",
     "Comprar asi no tiene riesgo."),
    (r"Puedes revisar la camisa antes de pagarla comprando asi\.",
     "Comprar asi no tiene riesgo."),
    (r"Por eso puedes revisar la camisa antes de pagarla: pueden ver y tocar antes de soltar el dinero\.",
     "Y si el tono no es el que esperabas, cambias sin costo dentro de los 30 dias."),
    (r"Por eso puedes revisar la camisa antes de pagarla\.", "Sin anticipos ni riesgo."),
    (r"Puedes revisar la camisa antes de pagarla\.", "No adelantas un solo peso."),
    (r"Puedes revisar tu camisa antes de pagar un solo peso\.", "No adelantas un solo peso."),
    (r"Puedes revisarla antes de pagarla, que es la mejor garantia de que la prenda que vas a revender o entregar cumple\.",
     "Los 30 dias de cambio son la mejor garantia de que la prenda que vas a revender o entregar cumple."),
    (r"Por eso puedes revisarla antes de pagar: si no te convence, no la recibes\.",
     "Y si el tono no es el que esperabas, cambias sin costo dentro de los 30 dias."),
    (r"Como adem&aacute;s el pago es contraentrega, revisas la camisa antes de pagarla\.",
     "Ademas el pago es contraentrega."),
    (r"Como además el pago es contraentrega, revisas la camisa antes de pagarla\.",
     "Además el pago es contraentrega."),
    (r"(&mdash;|, )y puedes revisar la camisa antes de pagarla\.", r"\1con 30 dias de cambio sin costo."),
    (r"puedes revisarla antes de pagar</strong>", "pagas al recibir</strong>"),

    # ── "te la pruebas / probarte antes de pagar" ──
    (r"Y como compras contraentrega, el riesgo es minimo: te pruebas la camisa antes de pagar\.",
     "Y como compras contraentrega, el riesgo es minimo: no adelantas un solo peso."),
    (r"Y como compras contraentrega, te pruebas la camisa antes de pagar\.",
     "Y como compras contraentrega, no adelantas un solo peso."),
    (r"Prefieres probarte la camisa en casa y pagar solo si te queda, sin arriesgar tu plata por adelantado\.",
     "Prefieres pagar al recibir, sin arriesgar tu plata por adelantado."),
    (r"Con nuestro pago contraentrega puedes probarte la prenda en casa y quedártela solo si te queda perfecta, sin ningún riesgo\.",
     "Con nuestro pago contraentrega no adelantas nada, y si la talla no queda, la cambias sin costo dentro de los 30 días."),
    (r"Puedes abrir el paquete, tocar la tela, revisar el cuello y confirmar la talla\.",
     "Y si la talla no queda, la cambias sin costo dentro de los 30 dias."),
    (r"Tocas la tela, revisas el corte, te pruebas la talla, miras las costuras\.",
     "Y si algo no queda como esperabas, cambias sin costo dentro de los 30 dias."),
    (r"pueden ver y tocar antes de soltar el dinero\.", "no adelantan un solo peso."),
    (r", si la camisa no te convence al abrir el paquete, no la aceptas y no pagas &mdash;asi de simple&mdash;\.",
     ", y si la talla no queda, la cambias sin costo dentro de los 30 dias."),
    (r"Sin filas en el mall, sin buscar parqueadero bajo el sol samario, sin pagar antes de probarte la camisa\.",
     "Sin filas en el mall, sin buscar parqueadero bajo el sol samario y sin adelantar un peso."),
    (r"abre el paquete frente al transportador y revisa con calma\.",
     "revisa la guia y los datos del pedido antes de recibir."),

    # ── consejos de compra: "antes de pagar" -> "antes de comprar" ──
    (r"Para comprar barato sin arrepentirte, aprende a leer la prenda antes de pagar\.",
     "Para comprar barato sin arrepentirte, aprende a leer la prenda antes de comprar."),
    (r"Para elegir bien, aprende a revisar tres cosas antes de pagar cualquier polo:",
     "Para elegir bien, aprende a revisar tres cosas antes de comprar cualquier polo:"),
    (r"Nuestras camisas pasan las cuatro pruebas, y puedes comprobarlo tu mismo antes de pagar, comprando al precio mas bajo\.",
     "Nuestras camisas pasan las cuatro pruebas, y las llevas al precio mas bajo."),
    (r"Como el beige tiene muchos matices, poder verlo en persona antes de pagar es una gran ventaja, y el envio es gratis a todo Colombia\.",
     "Como el beige tiene muchos matices, publicamos foto real de cada tono, y el envio es gratis a todo Colombia."),
    (r"Pide con unos dias de anticipacion a tu evento y, si dudas de la talla, el pack te da margen para escoger, y solo pagas cuando la recibes\.",
     "Pide con unos dias de anticipacion a tu evento y, si dudas de la talla, el pack te da margen para escoger."),
    (r"—pagas cuando la recibes, no antes— y entrega en 3 a 6 días hábiles\.",
     "—pagas al recibir— y entrega en 3 a 6 días hábiles."),
    (r": revisas la camisa antes de pagar\.", ": pagas al recibir."),

    # ── blogs (texto con tildes) ──
    (r"Trabajamos con pago contraentrega y envío gratis, así que la camisa llega a tu casa, te la pruebas y confirmas que el color, el ajuste y el largo son los correctos para tu cuerpo antes de pagar\.",
     "Trabajamos con pago contraentrega y envío gratis, así que no adelantas nada: pagas cuando la camisa llega a tu casa."),
    (r"Con más de 20 colores disponibles de la talla S a la 5XL, envío gratis y pago contraentrega, puedes probarte la polo en casa y confirmar que el color, el ajuste y el largo son los correctos para tu cuerpo antes de pagar\.",
     "Con más de 20 colores disponibles de la talla S a la 5XL, envío gratis y pago contraentrega, compras sin adelantar nada y con 30 días para cambiar la talla si no queda."),
    (r"¿Puedo probarme la camisa polo antes de pagar\?", "¿Qué pasa si la talla no me queda?"),
    (r"quienes prefieren probar antes de pagar \(contraentrega\)\.",
     "quienes prefieren pagar al recibir (contraentrega)."),
    (r"Comprar alternativa con pago contraentrega: el producto llega a tu casa, te lo pruebas antes de pagar y solo pagas si te queda\.",
     "Comprar alternativa con pago contraentrega: el producto llega a tu casa y pagas ahí mismo, sin adelantar nada."),
    (r"Y como pagas contraentrega y te la pruebas antes de pagar, puedes ver el color junto a tu cara sin ningún riesgo antes de decidir\.",
     "Y como pagas contraentrega, no arriesgas plata por adelantado; si el tono no convence, cambias sin costo dentro de los 30 días."),
    (r"Con pago contraentrega puedes probarte la camisa antes de pagar, así que aprovéchalo para verificar el fit frente al espejo\.",
     "Y si al probártela el fit no es el que buscabas, cambias la talla sin costo dentro de los 30 días."),
    (r"con tallaje real de S a 5XL y pago contraentrega, puedes probarte tu camisa antes de pagar y asegurarte de que quede perfecta desde el primer uso\.",
     "con tallaje real de S a 5XL, pago contraentrega y 30 días para cambiar la talla, aciertas desde el primer pedido."),
    (r"En Camisas Colombia manejamos polos estilo premium en tallas de la S a la 5XL con pago contraentrega y envío a todo el país, así que puedes probar la talla en casa antes de pagar y ajustar sin riesgo\.",
     "En Camisas Colombia manejamos polos estilo premium en tallas de la S a la 5XL con pago contraentrega y envío a todo el país, y 30 días para cambiar la talla si no queda."),
    (r"Todas las polos van con pago contraentrega, así que te la pruebas en casa antes de pagar, y si el corte o la talla no queda perfecto, cambiamos por otra talla sin costo dentro de los 30 días\.",
     "Todas las polos van con pago contraentrega, y si el corte o la talla no queda perfecto, cambiamos por otra talla sin costo dentro de los 30 días."),
    (r"Además compras con pago contraentrega, así que te la pruebas en casa y si no queda, cambiamos la talla sin costo dentro de 30 días\.",
     "Además compras con pago contraentrega, y si la talla no queda, la cambiamos sin costo dentro de 30 días."),
    (r"Te la pruebas antes de pagar; si no ajusta, la devuelves sin costo\.",
     "Pagas al recibir; si la talla no ajusta, la cambias sin costo dentro de los 30 días."),
    (r"pides 3XL, te llega, te la pruebas\.", "pides 3XL y te llega."),

    # ── 2a pasada: variantes que no encajaban en las reglas de arriba ──
    (r"pagas solo cuando la camisa llega a tu puerta, revisas la tela y la talla, y confirmas que te gusta\.",
     "pagas solo cuando la camisa llega a tu puerta, sin anticipos."),
    (r"Revisas tu camisa a cuadros, confirmas que el patron te gusta y que la talla te queda, y recien ahi pagas\.",
     "Pagas en la puerta de tu casa, sin adelantar nada."),
    (r"Pagas solo cuando el domiciliario llega a tu puerta, revisas la tela, la talla y el color, y confirmas que sirve para tu evento\.",
     "Pagas solo cuando el domiciliario llega a tu puerta, sin anticipos."),
    (r"Pagas solo cuando el domiciliario llega a tu puerta, revisas la camisa y confirmas la talla y el color\.",
     "Pagas solo cuando el domiciliario llega a tu puerta, sin anticipos."),
    (r"pagas solo cuando el domiciliario llega a tu puerta, revisas la tela, el cuello y la talla, y confirmas que te gusta\.",
     "pagas solo cuando el domiciliario llega a tu puerta, sin anticipos."),
    (r"Pagas solo cuando el domiciliario llega a tu puerta y revisas la prenda, ideal si eres estudiante y cuidas el bolsillo\.",
     "Pagas solo cuando el domiciliario llega a tu puerta, ideal si eres estudiante y cuidas el bolsillo."),
    (r"&mdash;pagas solo cuando la camisa llega a tu puerta&mdash; y puedes revisar la camisa antes de pagarla\.",
     "&mdash;pagas solo cuando la camisa llega a tu puerta&mdash; con 30 dias de cambio sin costo."),
    (r"Revisas tu camisa polo, confirmas que te gusta y que te queda, y luego pagas\.",
     "Pagas en la puerta de tu casa, sin adelantar nada."),
    (r"Recibes, revisas la tela y la talla, y pagas en efectivo, Nequi, Daviplata o transferencia\.",
     "Recibes y pagas en efectivo, Nequi, Daviplata o transferencia."),
    (r"Con nosotros no pagas por adelantado: el domiciliario llega, revisas la camisa y pagas solo si te convence\.",
     "Con nosotros no pagas por adelantado: el domiciliario llega y pagas en ese momento."),
    (r"No transfieres nada por adelantado: el domiciliario llega con tu pack completo, abres el paquete, revisas cada camisa [^.]*?\.",
     "No transfieres nada por adelantado: el domiciliario llega con tu pack completo y pagas en ese momento."),

    # ── 3a pasada. Dos puntos ciegos del barrido inicial:
    #    (a) etiquetas HTML dentro de la frase ("Revisas tu <strong>camisa
    #        tipo lino</strong>") rompian el patron;
    #    (b) la tercera persona ("revisan", "pagan"), que solo aparece en la
    #        pagina de senores.
    (r"y como es pago contraentrega puedes revisar cada talla al recibir\.",
     "y como es pago contraentrega, no adelantas nada."),
    (r"Revisas tu <strong>camisa tipo lino</strong> y pagas en ese momento\.",
     "Pagas en ese momento, sin adelantar nada."),
    (r"el senor o su familia reciben el paquete en la puerta, revisan la tela, el cuello y la talla, y pagan solo si estan conformes, en efectivo, Nequi, Daviplata o transferencia\.",
     "el senor o su familia pagan en la puerta, en efectivo, Nequi, Daviplata o transferencia."),
    (r"pago contraentrega \(pagas cuando recibes y te pruebas la prenda\)",
     "pago contraentrega (pagas cuando recibes)"),
    (r"recibes la camisa, revisas la calidad y el cuello, y pagas solo si te convence\.",
     "recibes la camisa y pagas en ese momento."),

    # ── limpieza de la redundancia que introdujeron mis propios reemplazos ──
    (r"pagas solo cuando la camisa llega a tu puerta, sin anticipos\. Sin anticipos ni riesgo\. Sin anticipos ni riesgo\.",
     "pagas solo cuando la camisa llega a tu puerta, sin anticipos ni riesgo."),
    (r"pagas solo cuando la camisa llega a tu puerta, sin anticipos\. Sin anticipos ni riesgo\.",
     "pagas solo cuando la camisa llega a tu puerta, sin anticipos ni riesgo."),
    (r"(<strong>Pagas solo cuando el domiciliario llega a tu puerta</strong>, en efectivo, Nequi, Daviplata o transferencia\.) Pagas en la puerta de tu casa, sin adelantar nada\.",
     r"\1"),
    (r"(pagas solo cuando el domiciliario llega a tu puerta</strong>, en efectivo, Nequi, Daviplata o transferencia\.) Pagas en la puerta de tu casa, sin adelantar nada\.",
     r"\1"),
    (r"(en efectivo, Nequi, Daviplata o transferencia\.) (?:Pagas|Recibes) (?:en la puerta de tu casa, sin adelantar nada|y pagas en efectivo, Nequi, Daviplata o transferencia)\.",
     r"\1"),
    (r"Sin anticipos\. Sin anticipos ni riesgo\.", "Sin anticipos ni riesgo."),
    (r"Sin anticipos ni riesgo\. Sin anticipos ni riesgo\.", "Sin anticipos ni riesgo."),
    (r"sin anticipos\. Nada de anticipos ni sorpresas\.", "sin anticipos ni sorpresas."),
    (r"No adelantas un solo peso\. No adelantas un solo peso\.", "No adelantas un solo peso."),
]


def main():
    dry = "--dry-run" in sys.argv
    paginas = sorted(set(p.replace(os.sep, "/") for p in
                     glob.glob("*.html") + glob.glob("blog/*.html")
                     + glob.glob("guias/*.html")))
    # el post de contraentrega se reescribe aparte, entero
    paginas = [p for p in paginas if p != "blog/pago-contraentrega-seguro.html"]
    total = 0
    sin_uso = []
    por_regla = {}
    tocados = set()
    for pat, rep in REGLAS:
        por_regla[pat] = 0
    for f in paginas:
        h = io.open(f, encoding="utf-8").read()
        orig = h
        for pat, rep in REGLAS:
            h, n = re.subn(pat, rep, h)
            por_regla[pat] += n
            total += n
        if h != orig:
            tocados.add(f)
            if not dry:
                io.open(f, "w", encoding="utf-8", newline="").write(h)
    for pat, n in por_regla.items():
        if n == 0:
            sin_uso.append(pat)
    print("%d reemplazos en %d archivos" % (total, len(tocados)))
    if sin_uso:
        print("\n%d reglas SIN USO (revisar, puede que el texto sea distinto):" % len(sin_uso))
        for p in sin_uso[:15]:
            print("   %s" % p[:110])
    print("\n%s" % ("(DRY-RUN, no se escribio)" if dry else "aplicado"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
