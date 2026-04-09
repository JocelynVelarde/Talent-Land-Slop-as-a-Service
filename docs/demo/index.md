---
title: Estrategia de Demo
nav_order: 8
has_children: false
---

# Estrategia de Demo

{: .fs-8 }

PicoScope como validador independiente, script AWG automatizado y argumentos técnicos para el jurado.
{: .fs-5 .fw-300 }

---

## Filosofía del demo

El PicoScope 2208B MSO **no es un display redundante** — actúa como **validador independiente.** Muestra la waveform física en tiempo real mientras Tecovolt clasifica y actúa el relay. Dos sistemas independientes mostrando el mismo fenómeno fortalece la credibilidad de las detecciones ante el jurado.

---

## Secuencia AWG automatizada (~60 segundos)

El script `tecovolt_demo_awg.py` automatiza el AWG del PicoScope para reproducir la secuencia de fenómenos que activa el relay:

| Fase               | Config AWG       | Duración                            |
| :----------------- | :--------------- | :---------------------------------- |
| **normal**         | 1500 mV, 60.0 Hz | 8 s — baseline                      |
| **sag_leve × 3**   | 1000 mV, 59.8 Hz | 3 s cada uno — patrón acumulándose  |
| **sag_severo × 2** | 600 mV, 59.5 Hz  | 4 s cada uno — **RELAY ACTÚA aquí** |
| **outage**         | 0 mV             | 6 s — relay ya protegió el circuito |
| **normal**         | 1500 mV, 60.0 Hz | 5 s — recuperación                  |

{: .note }

> La escala del AWG (1500 mV) corresponde a la señal de referencia que el ZMPT procesa para generar ~0.115 V RMS en el ADC del Arduino — equivalente a la red normal de 127V en México.

El relay actúa en `sag_severo` porque el MPU acumula ≥2 detecciones de esa clase en su historial de 10 ventanas — no en la primera detección aislada.

---

## Argumento contra overfitting

El modelo final tiene **99.3% accuracy en validation set con AUC=1.00.**

Puntos de defensa ante el jurado:

**1. La curva de entrenamiento no diverge.** Train y validation convergen juntas — evidencia de generalización correcta, no de memorización.

**2. Los fenómenos físicos tienen diferencias matemáticas reales y medibles:**

| Clase      | RMS medido | Diferencia vs normal                |
| :--------- | :--------- | :---------------------------------- |
| normal     | 0.1175 V   | —                                   |
| outage     | 0.0007 V   | **164x menor**                      |
| sag_severo | ~0.04 V    | ~3x menor                           |
| flicker    | ~0.1175 V  | ~idéntico en RMS — separado por THD |

**3. El modelo aprendió física, no ruido.** Una diferencia de 164x entre outage y normal no es un artefacto del dataset — es voltaje presente vs voltaje ausente.

**4. THD separa lo que RMS no puede.** `flicker` y `normal` tienen el mismo RMS. El modelo los distingue por distorsión armónica (THD 10–20x mayor en flicker) — una propiedad física real de la modulación de amplitud.

---

## Diferenciadores técnicos para el pitch

| #   | Diferenciador                           | Argumento                                                                                               |
| :-- | :-------------------------------------- | :------------------------------------------------------------------------------------------------------ |
| 1   | Tres modelos simultáneos en un solo MCU | Gestión de memoria embebida en 786 KB RAM con inferencia en paralelo                                    |
| 2   | INT8 via Qualcomm AI Hub                | ~200 KB → ~50 KB por modelo. Diferencia entre 12h y 72h de batería                                      |
| 3   | Separación MCU/MPU deliberada           | Inferencia < 1ms en MCU, lógica compuesta y comunicación en MPU                                         |
| 4   | Relay físico                            | Cierra el loop de protección — no es un dashboard, es una respuesta autónoma                            |
| 5   | OTA via Foundries.io                    | Modelos actualizables en campo sin tocar el hardware                                                    |
| 6   | DSP block custom con THD                | Feature que detecta flicker por distorsión armónica, no amplitud — imposible con bloques estándar de EI |
