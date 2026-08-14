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

**Día 2 — si las 4 anteriores entran al índice**

| # | URL |
|---|---|
| 5 | /camisas-polo-itagui |
| 6 | /camisas-polo-envigado |
| 7 | /camisas-polo-valledupar |
| 8 | /camisas-polo-monteria |

**No pedir todavía**: neiva, pasto, armenia, popayán. Son los mercados más
pequeños y gastan cuota de una señal que conviene concentrar.

## La decisión de fondo

Pedir indexación es un empujón, no una solución: si Google ya evaluó Medellín
y decidió no indexarla, volver a pedirlo sin cambiar nada suele repetir el
resultado. Las dos palancas que sí mueven la aguja:

1. **Dejar de crear páginas.** Cada página nueva que Google rechaza empeora la
   señal de calidad del dominio. Ya está decidido en el proyecto desde el
   7 de agosto ("atacar posición, no cobertura") — esto lo confirma con datos.
2. **Backlinks a la pilar y a Medellín.** Es el único frente donde la
   competencia gana por autoridad y no por producto.

Opción a evaluar: poner en `noindex` las 8 ciudades de mercado pequeño que
Google rechaza (neiva, pasto, armenia, popayán, valledupar, montería, itagüí,
envigado) hasta que el dominio tenga más autoridad. Concentra la señal en las
páginas que sí pueden rankear. Es reversible, pero es una decisión de negocio.
