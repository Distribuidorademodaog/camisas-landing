# -*- coding: utf-8 -*-
"""
Reoptimizacion de las 13 paginas de ciudad indexadas — 2026-08-18.

Por que las ciudades: con la dimension `page` sola (la fiable — ver la nota de
metodologia al final), en 3 meses las paginas de ciudad dan **63 clics sobre
1.560 impresiones = 4,04% de CTR**, el 38% de los clics de todo el sitio con el
16% de las impresiones. Ningun otro formato se acerca: el blog informativo esta
en 0,24%. Medellin, recien indexada, entra en posicion 4,9 con 9,09% de CTR.

Tres problemas medidos en esas 13 paginas:

  1. Los 13 titles eran la MISMA plantilla: "Camisas Polo en {Ciudad} | Pago
     Contraentrega Colombia". 24 caracteres de relleno identico repetidos 13
     veces, sin nada que distinga una ciudad de otra en el SERP.
  2. Nueve descriptions declaraban "4.9★ +998 clientes" — la afirmacion que la
     auditoria retiro del schema por tener solo 4 resenas reales. Seguia viva
     en la meta description Y en la description del schema WebPage.
  3. Artefacto del de-branding: "Cundinamarca. estilo clasico, +20 colores"
     (minuscula despues de punto) en 10 paginas. Viene del reemplazo
     "Ralph Lauren" -> "estilo clasico" hecho a mitad de frase.

Criterio del copy nuevo: cada ciudad usa datos REALES de su propia pagina
(temperatura y barrios que ya estan en el contenido local), no plantilla. El
clima es ademas el criterio de compra que importa: el corpus de 1.954 resenas
de la auditoria dice que el comprador juzga la camisa por "tela gruesa vs
delgada", no por composicion.

NOTA DE METODOLOGIA (importante, cost dos analisis equivocados):
    En este sitio NO se puede cruzar `page` con `country` en la API de GSC.
    Misma pagina, misma ventana:
        dimensions=[page]           -> /camisas-polo-cali  20 clics, 352 impr
        dimensions=[page, country]  -> /camisas-polo-cali   0 clics,  18 impr
    Al cruzar dimensiones GSC descarta las filas que no puede atribuir y el
    volumen se desploma ~95%. Los totales por pais (dimension `country` sola)
    y por pagina (dimension `page` sola) SI reconcilian con el export de la UI.
    Usar siempre dimensiones sueltas para este sitio.

Uso:  python seo_ciudades_2026_08.py [--dry-run]
"""
import io
import re
import sys

# slug -> (title, description)
CIUDADES = {
    # ---------- clima frio: el angulo es manga larga ----------
    "bogota": (
        "Camisas Polo en Bogotá: Manga Larga o Corta, Paga al Recibir",
        "Camisas polo para hombre en Bogotá: manga larga o corta para los 13°C, "
        "tallas S a 5XL y +20 colores. Pagas al recibir, envío 1-3 días a "
        "Chapinero y Usaquén."),
    "manizales": (
        "Camisas Polo en Manizales | Manga Larga para el Frío",
        "Camisas polo para hombre en Manizales: manga larga para los 17°C, "
        "tallas S a 5XL y +20 colores. Pagas al recibir, envío 1-3 días a "
        "Palermo y Fundadores."),
    "soacha": (
        "Camisas Polo en Soacha | Envío Gratis desde Bogotá",
        "Camisas polo para hombre en Soacha: tallas S a 5XL y +20 colores, tela "
        "para el frío de la sabana. Pagas al recibir, envío 1-3 días a "
        "Compartir y todo Soacha."),
    "pereira": (
        "Camisas Polo en Pereira | Envío Gratis al Eje Cafetero",
        "Camisas polo para hombre en Pereira: tallas S a 5XL, +20 colores y tela "
        "cómoda para los 21°C. Pagas al recibir, envío gratis a Circunvalar y "
        "Dosquebradas."),
    # ---------- clima templado: versatilidad todo el ano ----------
    "medellin": (
        "Camisas Polo en Medellín | Envío a Todo el Valle de Aburrá",
        "Camisas polo para hombre en Medellín: tela cómoda para los 22°C todo el "
        "año, tallas S a 5XL y +20 colores. Pagas al recibir, envío a Provenza "
        "y Astorga."),
    "bucaramanga": (
        "Camisas Polo en Bucaramanga | Tallas S a 5XL, Paga al Recibir",
        "Camisas polo para hombre en Bucaramanga: tallas S a 5XL y +20 colores "
        "para los 23°C de la ciudad. Pagas al recibir, envío 1-3 días al Cacique "
        "y todo Santander."),
    "ibague": (
        "Camisas Polo en Ibagué | Envío Gratis y Pagas al Recibir",
        "Camisas polo para hombre en Ibagué, Tolima: tallas S a 5XL, +20 colores "
        "y tela cómoda para los 22°C. Pagas al recibir, envío gratis en 1-3 "
        "días."),
    # ---------- clima calido: el angulo es tela fresca ----------
    "cali": (
        "Camisas Polo en Cali: Tela Fresca para el Calor del Valle",
        "Camisas polo para hombre en Cali: tela fresca para los 30°C del Valle, "
        "tallas S a 5XL y +20 colores. Pagas al recibir, envío gratis en 1-3 "
        "días."),
    "barranquilla": (
        "Camisas Polo en Barranquilla | Tela Fresca para el Calor",
        "Camisas polo para hombre en Barranquilla: tela fresca para los 30°C, "
        "tallas S a 5XL y +20 colores. Pagas al recibir, envío 1-3 días a Alto "
        "Prado y Riomar."),
    "cartagena": (
        "Camisas Polo en Cartagena | Frescas para Bocagrande y Centro",
        "Camisas polo para hombre en Cartagena: tela fresca para los 30°C, "
        "tallas S a 5XL y +20 colores. Pagas al recibir, envío 1-3 días a "
        "Bocagrande y Getsemaní."),
    "cucuta": (
        "Camisas Polo en Cúcuta | Tela Fresca y Pagas al Recibir",
        "Camisas polo para hombre en Cúcuta: tela fresca para los 28°C, tallas S "
        "a 5XL y +20 colores. Pagas al recibir, envío 1-3 días a Caobos y el "
        "centro."),
    "santa-marta": (
        "Camisas Polo en Santa Marta | Frescas para El Rodadero",
        "Camisas polo para hombre en Santa Marta: tela fresca para los 32°C, "
        "tallas S a 5XL y +20 colores. Pagas al recibir, envío 1-3 días a El "
        "Rodadero y el Centro."),
    "villavicencio": (
        "Camisas Polo en Villavicencio | Tela Fresca para el Llano",
        "Camisas polo para hombre en Villavicencio, Meta: tela fresca para los "
        "33°C del Llano, tallas S a 5XL y +20 colores. Pagas al recibir, envío "
        "1-3 días."),
}

TITLE_MAX = 62
DESC_MAX = 160
# Afirmaciones de resena sin respaldo: solo hay 4 resenas reales (ver auditoria).
PROHIBIDO = ["4.9", "998", "estrellas", "★"]


def validar():
    errs = []
    for slug, (t, d) in CIUDADES.items():
        if len(t) > TITLE_MAX:
            errs.append("%s: title %d chars > %d" % (slug, len(t), TITLE_MAX))
        if len(d) > DESC_MAX:
            errs.append("%s: desc %d chars > %d" % (slug, len(d), DESC_MAX))
        if not d.rstrip().endswith("."):
            errs.append("%s: desc no termina en punto" % slug)
        for p in PROHIBIDO:
            if p in t or p in d:
                errs.append("%s: afirmacion sin respaldo %r" % (slug, p))
        if '"' in t or '"' in d:
            errs.append("%s: comillas dobles rompen el atributo" % slug)
    ts = [t for t, _ in CIUDADES.values()]
    if len(set(ts)) != len(ts):
        errs.append("hay titles duplicados entre ciudades")
    return errs


def aplicar(slug, title, desc, dry):
    p = "camisas-polo-%s.html" % slug
    s = io.open(p, encoding="utf-8").read()
    orig = s

    # La description vieja vive en DOS sitios: la meta y el schema WebPage.
    # Se reemplaza la cadena literal completa para cubrir ambos de una vez.
    m = re.search(r'<meta name="description" content="(.*?)">', s, re.S)
    if not m:
        raise SystemExit("!! sin meta description: %s" % p)
    vieja = m.group(1)
    n_desc = s.count(vieja)
    s = s.replace(vieja, desc)

    s, n_t = re.subn(r"<title>.*?</title>", "<title>%s</title>" % title, s,
                     count=1, flags=re.S)
    if n_t != 1:
        raise SystemExit("!! sin <title>: %s" % p)

    s = re.sub(r'(<meta property="og:title" content=")(.*?)(">)',
               lambda mm: mm.group(1) + title + mm.group(3), s, count=1,
               flags=re.S)

    if s != orig and not dry:
        io.open(p, "w", encoding="utf-8", newline="").write(s)
    return n_desc


def main():
    dry = "--dry-run" in sys.argv
    errs = validar()
    if errs:
        print("VALIDACION FALLIDA:")
        for e in errs:
            print("   " + e)
        sys.exit(1)

    print("%-15s %-6s %-5s %s" % ("CIUDAD", "TITLE", "DESC", "veces que estaba la desc vieja"))
    for slug, (t, d) in CIUDADES.items():
        n = aplicar(slug, t, d, dry)
        print("%-15s %-6d %-5d %d  (meta + schema WebPage)" % (slug, len(t), len(d), n))
    print("\n%s %d ciudades" % ("DRY-RUN:" if dry else "Actualizadas", len(CIUDADES)))


if __name__ == "__main__":
    main()
