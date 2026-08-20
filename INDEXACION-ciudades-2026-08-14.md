# Indexación de las páginas de ciudad — 14 ago 2026

Estado medido con la URL Inspection API de Search Console sobre las 21 páginas
de ciudad. **9 indexadas, 12 no.** Las 9 indexadas son exactamente las 9 con
tráfico en GSC: la correlación es total.

## Qué NO lo explica (medido, descartado)

| Hipótesis | Medición | Veredicto |
|---|---|---|
| Contenido duplicado | Medellín 40,4% de solapamiento vs Cali 44,9% (indexada) | descartado |
| Contenido delgado | No indexadas 1.154 palabras únicas de media vs 653 las indexadas | descartado |
| Enlaces internos | Medellín tiene 79 enlaces entrantes, Cali 76 | descartado |
| Problema técnico | 200, canonical propio, `index, follow`, en sitemap | descartado |

## Lo que sí encaja: la edad del lote

| Lote | Fecha | Páginas | Indexadas |
|---|---|---|---|
| Originales | anterior | 10 | 8 de 10 (faltan medellín y cartagena) |
| Lote 5 | 22 jul | 8 ciudades | 0 de 8 |
| Lote 6 | 6 ago | 3 ciudades | 1 de 3 (soacha) |

El sitio pasó de 31 a 86 páginas en cinco semanas y Google indexó ~1 de cada 6
de las nuevas. Esto es saturación de índice en un dominio con poca autoridad:
Google decide cuántas páginas de este sitio le merecen espacio, y ya llegó a su
tope. Coincide con lo que ya estaba diagnosticado en el proyecto: el cuello de
botella es **autoridad/backlinks**, no cobertura.

## Orden para "Solicitar indexación" en GSC

Inspección de URLs → pegar la URL → *Solicitar indexación*. Hay un límite
aproximado de 10-12 al día. Pedirlas todas de golpe no ayuda: conviene ir por
las de mercado real y dejar reposar.

Todas van precedidas de `https://www.camisascolombia.com`.

**Día 1 — las que valen dinero**

| # | URL | Por qué primero |
|---|---|---|
| 1 | /camisas-polo-medellin | 2º mercado del país. Cali indexada da 20 clics; Medellín debería dar más |
| 2 | /camisas-polo-cartagena | Ciudad grande, original, mismo estado que Medellín |
| 3 | /camisas-polo-santa-marta | Google ni la conoce pese a llevar 3 semanas en el sitemap |
| 4 | /camisas-polo-villavicencio | Ídem, y es capital de departamento sin competencia local fuerte |

Y no hay día 2: las otras 8 ciudades quedaron en `noindex` (ver abajo). La
cuota diaria de solicitudes se concentra entera en estas 4.

## La decisión de fondo

Pedir indexación es un empujón, no una solución: si Google ya evaluó Medellín
y decidió no indexarla, volver a pedirlo sin cambiar nada suele repetir el
resultado. Las dos palancas que sí mueven la aguja:

1. **Dejar de crear páginas.** Cada página nueva que Google rechaza empeora la
   señal de calidad del dominio. Ya está decidido en el proyecto desde el
   7 de agosto ("atacar posición, no cobertura") — esto lo confirma con datos.
2. **Backlinks a la pilar y a Medellín.** Es el único frente donde la
   competencia gana por autoridad y no por producto.

## ✅ EJECUTADO 2026-08-14: noindex a las 8 ciudades de mercado pequeño

`noindex_ciudades_pequenas.py` puso `<meta name="robots" content="noindex,
follow">` y sacó del sitemap a: **neiva, pasto, armenia, popayán, valledupar,
montería, itagüí, envigado**. Sitemap 84 → 76 URLs.

Decisiones de la implementación:

- **`follow`, no `noindex, nofollow`.** El link equity sigue fluyendo hacia las
  páginas que sí queremos indexar.
- **Los enlaces internos se mantienen** (47-56 páginas siguen enlazando cada
  una). Son útiles para el usuario que busca su ciudad y para el rastreo; lo
  que se retira es la petición de indexarlas.
- **Fuera del sitemap.** Dejar una URL con `noindex` dentro del sitemap manda
  dos señales opuestas. `verificar_cambios.py` ahora tiene un control que
  falla si vuelven a desalinearse.

Para revertir cuando el dominio tenga más autoridad:

```
python noindex_ciudades_pequenas.py --revertir
```

O para rescatar solo alguna: quitarla de la lista `FUERA` del script y correr
`--revertir`.

**Lo que esto NO arregla:** el problema de fondo sigue siendo autoridad. El
noindex concentra la señal, pero quien mete a Medellín en el índice son los
backlinks. Ese frente sigue pendiente.

---

# Medición de seguimiento — 20 ago 2026

Inspección con la URL Inspection API sobre las 76 URLs del sitemap **más** las 8
puestas en `noindex`, para confirmar ambos frentes.

## El noindex y los títulos por clima funcionaron

| Fecha | URLs evaluadas | Indexadas | % |
|---|---|---|---|
| 5 ago | 72 | 34 | 47% |
| **20 ago** | **76** | **59** | **78%** |

**Las 13 ciudades que siguen en el índice están indexadas al 100%**, incluidas
las 4 que este documento marcaba como prioridad manual:

| Ciudad | Estado | Último rastreo |
|---|---|---|
| Medellín | Enviada e indexada | 2026-08-14 |
| Cartagena | Enviada e indexada | 2026-08-14 |
| Santa Marta | Enviada e indexada | 2026-08-14 |
| Villavicencio | Enviada e indexada | 2026-08-14 |

Se indexaron el mismo día en que se desplegaron los títulos diferenciados por
clima y geografía. **Ya no hay que pedirles indexación en GSC**: la lista de
"Día 1" de arriba queda cumplida.

Corrige también la hipótesis de este documento: no era solo saturación de
índice. Medellín y Cartagena llevaban desde el 13 de mayo rastreadas y
rechazadas; entraron cuando el contenido dejó de ser intercambiable. La
diferenciación sí movió la aguja.

## Las 8 en noindex: objetivo cumplido, sin residuo

Ninguna está en el índice, así que no hay nada que des-indexar. Seis nunca
fueron rastreadas y dos (Montería, Valledupar) quedaron en "rastreada, sin
indexar" desde el 13 de mayo.

## Lo que falta: 17 URLs

| Estado | URLs | Lectura |
|---|---|---|
| Descubierta: actualmente sin indexar | 12 | Google la conoce y no ha gastado rastreo |
| Google no reconoce esta URL | 5 | Ni siquiera la ha descubierto |

**Ninguna ha sido rastreada nunca.** No hay rechazo de calidad: hay falta de
presupuesto de rastreo. Las 17:

`/camisas-formales-hombre` · `/camisas-para-grado-hombre` ·
`/camisas-para-matrimonio-hombre` · `/camisas-polo-azul-marino-hombre` ·
`/camisas-polo-celestes-hombre` · `/camisas-polo-grises-hombre` ·
`/camisas-polo-vinotinto-hombre` · `/camisas-polo-para-senores-hombre` ·
`/camisetas-polo-hombre` · `/polos-hombre-colombia` · `/guias` ·
`/guias/guia-definitiva-camisas-polo-hombre-colombia` ·
`/blog/cuantas-camisas-polo-debe-tener-un-hombre` ·
`/blog/errores-comunes-al-usar-camisa-polo` ·
`/blog/slim-fit-vs-regular-fit-camisa-polo` ·
`/blog/camisas-polo-para-cada-tipo-de-cuerpo` · `/blog/ocasiones-camisa-polo`

Ojo con dos: `/camisetas-polo-hombre` y `/polos-hombre-colombia` son sinónimos
entre sí y de `/camisas-polo-premium-colombia`, que sí está indexada. Que Google
ignore las dos primeras es coherente — probablemente sean candidatas a fusión
antes que a insistir en indexarlas.

## Ejecutado 2026-08-20

1. **Corregida la lista de la Indexing API.** `~/indexing/sites/camisascolombia.txt`
   en el Hostinger tenía 84 URLs, **incluidas las 8 en `noindex`** — se le estaba
   pidiendo a Google indexar lo que se le pide no indexar. Ahora son las 76 del
   sitemap. Regenerarla siempre desde el sitemap tras cambios de cobertura.
2. **Enviadas las 76 a la Indexing API:** OK=76, fallos=0. Justificado porque el
   contenido cambió de verdad (títulos, schema, marcado) desde el último rastreo.

## El frente que sigue abierto

Sin cambios respecto al diagnóstico original: **autoridad**. El sistema de
backlinks tiene 64 oportunidades y el T1 (redes sociales) sigue sin ejecutar,
que además es lo que desbloquea el `sameAs` vacío del schema.
