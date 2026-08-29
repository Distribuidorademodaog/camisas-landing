# -*- coding: utf-8 -*-
"""
Atribucion de Meta: fbc/fbp al CAPI + deduplicacion en las 64 landings — 2026-08-29.

DIAGNOSTICO (datos reales, agosto 2026)
---------------------------------------
Meta reportaba 221 compras contra 266 reales en los 26 dias ya asentados: un
subconteo del 17%. Dos causas distintas, las dos en el mismo sitio:

1. El evento de RESPALDO del servidor no puede atribuirse.
   capi-sender manda Purchase con user_data = {telefono, external_id, pais}.
   Sin `fbc` (el click id del anuncio) ni `fbp` (la cookie del navegador),
   Meta recibe la compra pero NO puede amarrarla al clic que la origino.
   El pixel del navegador si los manda solo; el problema es solo el respaldo,
   que es justo el que cubre los casos de JS bloqueado, iOS o pestaña cerrada.

2. La deduplicacion solo funcionaba en index.html.
   El commit 59afe90 puso un event_id determinista, pero SOLO en el home. Las
   otras 64 paginas siguen con:
       const pedidoId = `ORD-${Date.now()}-${Math.floor(Math.random()*1000)}`;
   El servidor calcula 'pur_<telefono>_<YYYYMMDD Bogota>'. Nunca coinciden, asi
   que en esas 64 paginas el navegador y el servidor mandan el MISMO Purchase
   con dos ids distintos y Meta no puede unirlos.

QUE HACE
--------
En las 65 paginas con checkout:
  a) Calcula el event_id determinista (misma formula que capi-sender) y lo usa
     en el `eventID` del pixel. NO toca `pedidoId`, que sigue siendo la
     referencia del pedido para el correo y para n8n.
  b) Captura las cookies _fbc/_fbp (y reconstruye _fbc desde ?fbclid= si la
     cookie aun no existe) y las manda al servidor con navigator.sendBeacon.

Por que sendBeacon y no fetch:
  - Es "simple request": no dispara preflight, no necesita configurar CORS.
  - Es fire-and-forget y sobrevive al unload: NO puede bloquear el checkout.
    (Ver la leccion ya documentada: un fetch bloqueante congelo los CTAs.)
  - Va envuelto en try/catch: si algo falla, el pedido sigue su curso igual.

Uso:  python capi_fbc_fbp_2026_08_29.py [--dry-run]
"""
import io
import os
import re
import sys

DRY = "--dry-run" in sys.argv
SKIP = {"_blog", "_cities", "_landings", "output", "src", ".git", "node_modules"}
ENDPOINT = "https://pedidos.paquetecompleto.com.co/webhook/fb-attrib"
MARCA = "CAPI_FBC_FBP_2026_08"

# Bloque que se inserta justo antes del `if (typeof fbq !== 'undefined' ...`.
# Se apoya en celSoloNum, que ya existe en las 65 paginas.
BLOQUE = """
  // ── %(marca)s: atribucion del evento de respaldo del servidor ──
  // El pixel de abajo ya manda _fbc/_fbp solo. Esto es para el Purchase que
  // capi-sender manda desde el servidor: sin fbc/fbp Meta no puede amarrar la
  // compra al clic del anuncio (subconteo medido del 17%% en agosto 2026).
  // La clave telefono+fecha es la MISMA del event_id, asi el servidor cruza.
  const _capiDate = new Date(Date.now() - 5 * 3600 * 1000).toISOString().slice(0, 10).replace(/-/g, '');
  const capiEventId = 'pur_' + celSoloNum + '_' + _capiDate;
  try {
    const _ck = n => (document.cookie.match('(^|;)\\\\s*' + n + '\\\\s*=\\\\s*([^;]+)') || [])[2] || '';
    let _fbc = _ck('_fbc');
    if (!_fbc) {
      // Si el usuario acaba de llegar del anuncio, la cookie puede no existir
      // todavia: se reconstruye con el formato oficial fb.1.<ts>.<fbclid>.
      const _cid = new URLSearchParams(location.search).get('fbclid');
      if (_cid) _fbc = 'fb.1.' + Date.now() + '.' + _cid;
    }
    const _fbp = _ck('_fbp');
    if ((_fbc || _fbp) && navigator.sendBeacon) {
      navigator.sendBeacon('%(endpoint)s', new Blob([JSON.stringify({
        telefono: celSoloNum, ymd: _capiDate, fbc: _fbc, fbp: _fbp
      })], { type: 'text/plain' }));
    }
  } catch (e) { /* la atribucion nunca puede romper el checkout */ }

""" % {"marca": MARCA, "endpoint": ENDPOINT}

# Ancla: la linea que abre el disparo del pixel. Identica en las 65 paginas.
ANCLA = "  if (typeof fbq !== 'undefined' && (Date.now() - trackTs) > TWENTY_FOUR_H) {"


def html_files():
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in sorted(files):
            if f.endswith(".html"):
                yield os.path.join(root, f).replace("\\", "/").lstrip("./")


def main():
    ok = dedup = beacon = 0
    sin_ancla = []

    for path in html_files():
        s = io.open(path, encoding="utf-8").read()
        if "trackKey" not in s or "fbq('track', 'Purchase'" not in s:
            continue  # pagina sin checkout
        if MARCA in s:
            continue  # ya procesada

        orig = s

        # (a) event_id determinista. index.html ya lo tiene: no se duplica.
        if "capiEventId" not in s:
            if ANCLA not in s:
                sin_ancla.append(path)
                continue
            s = s.replace(ANCLA, BLOQUE + ANCLA, 1)
            beacon += 1
        else:
            # index.html: ya calcula capiEventId, solo falta el beacon.
            solo_beacon = BLOQUE.split("const capiEventId")[0]
            solo_beacon = solo_beacon.replace(
                "  const _capiDate = new Date(Date.now() - 5 * 3600 * 1000)"
                ".toISOString().slice(0, 10).replace(/-/g, '');\n", "")
            resto = BLOQUE[BLOQUE.index("  try {"):]
            s = s.replace(ANCLA, solo_beacon + resto + ANCLA, 1)
            beacon += 1

        # (b) el pixel debe usar el id determinista, no el aleatorio
        if "eventID: pedidoId" in s:
            s = s.replace("}, { eventID: pedidoId });",
                          "}, { eventID: capiEventId });")
            s = s.replace("console.log('Evento Purchase enviado con ID:', pedidoId);",
                          "console.log('Evento Purchase enviado con ID:', capiEventId);")
            dedup += 1

        if s != orig:
            if not DRY:
                io.open(path, "w", encoding="utf-8", newline="").write(s)
            ok += 1

    print("Paginas con checkout modificadas: %d%s" % (ok, "  (simulacion)" if DRY else ""))
    print("   event_id determinista corregido en: %d" % dedup)
    print("   captura de fbc/fbp añadida en:      %d" % beacon)
    if sin_ancla:
        print("   !! sin el ancla esperada (%d): %s" % (len(sin_ancla), sin_ancla[:5]))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
