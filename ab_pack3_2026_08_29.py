# -*- coding: utf-8 -*-
"""
A/B de la preseleccion del Pack 3 + reparar el AddToCart — 2026-08-29.

POR QUE
-------
Descomposicion medida de la caida de mayo a agosto (pedidos reales, no pixel):

    812 pedidos (mayo)
    x 0,920  gasto        ->  747
    x 0,539  CPC (+86%)   ->  403   <- 2/3 del problema, son los creativos
    x 0,773  conversion   ->  311   <- esto es lo que se prueba aqui

La conversion cae en la semana del 6-jul, justo tras el CRO del 3-jul
(commit ebc0313), y los tres numeros se mueven a la vez en la direccion que
predice la preseleccion del Pack 3:

    conversion   2,27% -> 1,75%   (-23%)
    ticket     199.107 -> 220.979 (+11%)
    % packs        38% -> 55%
    INGRESO/CLIC  4.521 -> 3.878  (-14%)   <- neto NEGATIVO

Subio el ticket pero costo mas conversion de la que gano. Aun asi NO se
revierte a ciegas: el alza de AOV es real y puede compensar con otros
creativos. Se mide.

Descartado con datos, para no perseguir fantasmas:
  - el de-branding del 21-jul: la conversion ya habia caido antes y no se
    movio despues;
  - los botones de WhatsApp del mismo CRO: 1 clic de 15.901 en trafico de
    venta web;
  - el checkout: chk->compra lleva todo el año entre 34% y 39%.

QUE HACE
--------
1. A/B 50/50 persistente por navegador:
     A = Pack 3 preseleccionado (comportamiento actual)
     B = sin preseleccion (comportamiento anterior al 3-jul)
2. Registra la EXPOSICION al entrar al paso de pack (sid aleatorio + variante),
   para poder calcular conversion por variante y no suponer que el reparto
   quedo parejo.
3. Manda la variante junto al pedido, reusando el beacon de fbc/fbp.
4. Repara el AddToCart: hoy solo se dispara si el usuario elige un pack
   ACTIVAMENTE, asi que desde el 3-jul la mitad del embudo es invisible (y
   Meta optimiza con menos señal). Pasa a dispararse cuando el usuario AVANZA
   del paso de pack, que es una accion real y ademas hace la serie comparable
   entre las dos variantes.

Uso:  python ab_pack3_2026_08_29.py [--dry-run]
"""
import io
import re
import sys

DRY = "--dry-run" in sys.argv
ARCHIVO = "index.html"
MARCA = "AB_PACK3_2026_08"
ENDPOINT = "https://pedidos.paquetecompleto.com.co/webhook/fb-attrib"

# ── 1. asignacion del experimento, junto al resto del estado ────────────────
ANCLA_ESTADO = "// ─── STATE ───"

BLOQUE_AB = """
// ── %(marca)s: experimento de la preseleccion del Pack 3 ──
// A = Pack 3 preseleccionado (actual) · B = sin preseleccion (previo al 3-jul).
// Persistente por navegador para que un mismo usuario no vea las dos.
var AB_PACK = (function () {
  try {
    var v = localStorage.getItem('ab_pack_v1');
    if (v !== 'A' && v !== 'B') { v = Math.random() < 0.5 ? 'A' : 'B'; localStorage.setItem('ab_pack_v1', v); }
    return v;
  } catch (e) { return 'A'; }   // sin localStorage se queda en el control
})();
var AB_SID = (function () {
  try {
    var s = localStorage.getItem('ab_sid_v1');
    if (!s) { s = Date.now().toString(36) + Math.random().toString(36).slice(2, 10); localStorage.setItem('ab_sid_v1', s); }
    return s;
  } catch (e) { return ''; }
})();
function abYmd() {
  return new Date(Date.now() - 5 * 3600 * 1000).toISOString().slice(0, 10).replace(/-/g, '');
}
var _abExpoEnviada = false;
function abRegistrarExposicion() {
  if (_abExpoEnviada || !AB_SID) return;
  _abExpoEnviada = true;
  try {
    if (navigator.sendBeacon) {
      navigator.sendBeacon('%(endpoint)s', new Blob([JSON.stringify({
        sid: AB_SID, variante: AB_PACK, ymd: abYmd()
      })], { type: 'text/plain' }));
    }
  } catch (e) { /* la medicion nunca puede romper el checkout */ }
}

""" % {"marca": MARCA, "endpoint": ENDPOINT}

# ── 2. preseleccion condicional + registro de exposicion ───────────────────
PRESEL_VIEJO = """    if (!S.pack) preselectPack3();"""
PRESEL_NUEVO = """    abRegistrarExposicion();
    if (!S.pack && AB_PACK === 'A') preselectPack3();"""

# ── 3. AddToCart al AVANZAR del paso de pack ───────────────────────────────
AVANZA_VIEJO = """  } else if (currentStep === STEP_PACK) {
    if (!S.pack) return;
    S.shirtIdx = 0;"""
AVANZA_NUEVO = """  } else if (currentStep === STEP_PACK) {
    if (!S.pack) return;
    // AddToCart al CONFIRMAR el pack, no solo al elegirlo a mano: desde el
    // 3-jul la preseleccion no disparaba el evento y la mitad del embudo
    // quedo invisible. Comparte la clave de dedup con pickPack().
    try {
      var _k = 'fb_atc_' + S.packQty + '_' + S.packPrice;
      if (typeof fbq !== 'undefined' && !sessionStorage.getItem(_k)) {
        sessionStorage.setItem(_k, '1');
        fbq('track', 'AddToCart', {
          value: S.packPrice, currency: 'COP',
          content_name: S.pack, num_items: S.packQty,
        });
      }
    } catch (e) {}
    S.shirtIdx = 0;"""

# ── 4. variante junto al pedido, en el beacon que ya existe ────────────────
BEACON_VIEJO = """        telefono: celSoloNum, ymd: _capiDate, fbc: _fbc, fbp: _fbp
      })], { type: 'text/plain' }));"""
BEACON_NUEVO = """        telefono: celSoloNum, ymd: _capiDate, fbc: _fbc, fbp: _fbp,
        variante: (typeof AB_PACK !== 'undefined' ? AB_PACK : null)
      })], { type: 'text/plain' }));"""

CAMBIOS = [
    ("bloque del experimento", ANCLA_ESTADO, BLOQUE_AB + ANCLA_ESTADO),
    ("preseleccion condicional", PRESEL_VIEJO, PRESEL_NUEVO),
    ("AddToCart al avanzar", AVANZA_VIEJO, AVANZA_NUEVO),
    ("variante en el beacon", BEACON_VIEJO, BEACON_NUEVO),
]


def main():
    s = io.open(ARCHIVO, encoding="utf-8").read()
    if MARCA in s:
        print("ya estaba aplicado")
        return 0

    faltan = [n for n, v, _ in CAMBIOS if v not in s]
    if faltan:
        for n in faltan:
            print("ABORTADO: no se encontro '%s'" % n)
        return 1

    for nombre, viejo, nuevo in CAMBIOS:
        s = s.replace(viejo, nuevo, 1)
        print("  OK  %s" % nombre)

    if not DRY:
        io.open(ARCHIVO, "w", encoding="utf-8", newline="").write(s)
    print("\n%s%s" % ("index.html actualizado", "  (simulacion)" if DRY else ""))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
