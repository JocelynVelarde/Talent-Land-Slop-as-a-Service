---
title: Edge AI & Modelos
nav_order: 5
---

# Edge AI & Modelos

{: .fs-8 }

Pipeline de datos, entrenamiento de modelos, custom DSP blocks y cuantización INT8 para inferencia on-device.
{: .fs-5 .fw-300 }

---

## Inteligencia artificial que opera sin conexión

Cuando la red eléctrica falla, el internet del hogar suele irse con ella. Por eso entrenamos en **Edge Impulse Studio** con datos reales de voltaje residencial y luego llevamos esos modelos al **Qualcomm AI Hub** para cuantizarlos a INT8 y perfilarlos energéticamente.

El resultado es un modelo que vive dentro del Arduino, aprende el comportamiento específico de cada red eléctrica y toma decisiones autónomas sin depender de una sola petición a internet.

---

## Modelo A · Anomalía de voltaje (TecovoltClassifier)

| Parámetro           | Valor                                                            |
| :------------------ | :--------------------------------------------------------------- |
| **Proyecto EI**     | tecovolt-voltage                                                 |
| **Tipo**            | Clasificador de 6 clases                                         |
| **Bloque DSP**      | Custom `tecovolt_block` — 6 features físicas vía Python/ngrok    |
| **Frecuencia**      | 1000 Hz                                                          |
| **Ventana**         | 200 ms (200 samples), stride 200 ms                              |
| **Arquitectura NN** | Dense 16 → Dense 8 → Softmax 6 clases                            |
| **Training cycles** | 100, lr=0.001                                                    |
| **Accuracy final**  | **99.3% validation, AUC=1.00**                                   |
| **Clases**          | `normal`, `sag_leve`, `sag_severo`, `swell`, `outage`, `flicker` |

### Features extraídas (6)

| Feature              | Descripción                                                                  |
| :------------------- | :--------------------------------------------------------------------------- |
| **rms_v**            | Voltaje RMS de la ventana — feature más discriminante para outage vs normal  |
| **peak_to_peak_v**   | Diferencia máximo–mínimo de la ventana                                       |
| **crest_factor**     | Peak / RMS — detecta distorsión de forma de onda                             |
| **rms_ripple_v**     | Desviación estándar del RMS por ciclo — detecta inestabilidad                |
| **dominant_freq_hz** | Frecuencia dominante vía FFT — detecta deriva de frecuencia                  |
| **thd**              | Total Harmonic Distortion — feature clave para separar `flicker` de `normal` |

{: .note }

> **¿Por qué THD?** `flicker` y `normal` tienen RMS casi idéntico (~0.1175V). El flicker genera modulación de amplitud que produce armónicos de 2° y 3° grado. En el dataset final: normal THD=0.005–0.015, flicker THD=0.15–0.30 — una diferencia de 10–20x. Sin esta feature el modelo confunde las dos clases.

{: .warning }

> **Crítico — no normalizar.** El RMS absoluto es la feature más discriminante. Normalizado, outage (0.0018 V) y normal (0.1175 V) se acercan y el modelo pierde su clase más fácil. outage vs normal es una diferencia de 164x — el modelo aprende física, no ruido.

### Historia de iteraciones

| Versión | Accuracy  | Notas                                                                       |
| :------ | :-------- | :-------------------------------------------------------------------------- |
| v1      | 94.5%     | Dataset sintético puro, 5 features                                          |
| v2      | 63.7%     | Dataset mixto (real + sintético). Confusión: `normal` ↔ `sag_leve`          |
| v3      | 63%       | THD como 6ta feature, arquitectura 20→10, auto-weight. Collapse a `flicker` |
| **v4**  | **99.3%** | Fix bug `fs` hardcodeado + separación agresiva en synth                     |

<img src="../assets/images/features/not_overfitted.png" alt="Descripción" width="600">

{: .warning }

> **Bug crítico resuelto (v2→v4):** el DSP block tenía `fs=6279.8` hardcodeado (sample rate del PicoScope) pero el dataset v2/v3 fue generado a 1000 Hz. Esto rompía el cálculo de RMS ripple y THD completamente. Fix: `fs = 1000.0` hardcodeado, alineado con el parámetro de Edge Impulse.

<img src="../assets/images/features/class_initial.png" alt="Descripción" width="500">

<img src="../assets/images/features/class_prefinal.png" alt="Descripción" width="600">

<img src="../assets/images/features/class_final.png" alt="Descripción" width="600">

### Dataset

Dataset mixto real + sintético. Datos reales capturados con PicoScope 2208B MSO del ZMPT101B a 6279.8 Hz (submuestreado a 1000 Hz para el modelo). Augmentation ×50 por captura real usando el perfil de ruido real medido (std diff-to-diff). Dataset final: **1440 train / 360 test, 6 clases balanceadas.**

Para `outage` no se amplifica la señal — solo ruido mínimo, ya que la señal es ~0 V y amplificar introduciría artefactos.

---

## Modelo B · Demanda energética (DemandClassification)

| Parámetro           | Valor                                                 |
| :------------------ | :---------------------------------------------------- |
| **Proyecto EI**     | tecovolt-demand                                       |
| **Tipo**            | Clasificador de 3 clases                              |
| **Bloque DSP**      | Flatten — Average, RMS, Std deviation (normalizado)   |
| **Frecuencia**      | ~2 Hz (lecturas rawRMS del ACS712)                    |
| **Ventana**         | 10 muestras = 5 s                                     |
| **Arquitectura NN** | Dense 8 → Softmax 3 clases                            |
| **Training cycles** | 100, lr=0.0005                                        |
| **Clases**          | `baja` (rawRMS <8), `media` (~42.81), `alta` (~87.60) |

{: .note }

> A diferencia del modelo de voltaje, el modelo de demanda **sí requiere normalización.** Las 3 features (avg, rms, std) están en la misma escala y el modelo necesita aprender proporciones, no valores absolutos.

### Valores reales medidos (ACS712-30A, dos calentadores ~1900 W)

| Clase   | rawRMS       | Carga real                 |
| :------ | :----------- | :------------------------- |
| `baja`  | 0.00         | Sin carga                  |
| `media` | 42.81 ± 0.21 | Un calentador (~950 W)     |
| `alta`  | 87.60 ± 0.23 | Dos calentadores (~1900 W) |

**Dataset final:** 638 train (600 sintéticos anclados a valores reales + 38 reales). Transitorios de arranque descartados (fronteras entre clases).

{: .note }

> **Insight de diseño:** la corriente (ACS712) **no** debe mezclarse como feature en el modelo de voltaje. Un sag con calentador encendido se ve diferente a un sag sin calentador — la corriente depende de las cargas del usuario, no de la calidad de la red.

---

## Modelo C · Riesgo térmico

| Parámetro      | Valor                                                                   |
| :------------- | :---------------------------------------------------------------------- |
| **Tipo**       | Clasificador de 3 clases                                                |
| **Bloque DSP** | Flatten (temperatura cambia lento — sin análisis frecuencial)           |
| **Frecuencia** | 1 Hz (BMP280)                                                           |
| **Ventana**    | 10 muestras = 10 s                                                      |
| **Clases**     | `bajo` (20–45 °C), `medio` (45–65 °C), `alto` (65–90 °C + baja humedad) |

Desarrollado por Jocelyn Velarde. Usa datos de temperatura/humedad del BMP280. Separado correctamente en proyecto EI propio porque tiene bloque de procesamiento distinto (Flatten, no DSP custom).

---

## Custom DSP Blocks

A diferencia del flujo estándar de Edge Impulse, Tecovolt implementa **bloques DSP custom** desplegados vía Docker y expuestos al servidor de EI vía ngrok:

**`tecovolt_block` (Voltaje)** — Extrae las 6 features físicas del modelo de voltaje, incluyendo THD. Implementado en Python (`dsp.py`), servido vía HTTP (`dsp-server.py`). Fix aplicado: parámetros JSON con guiones (`scale-axes`) se convierten a underscores antes de pasar como kwargs de Python.

**`tecotemp_block` (Temperatura)** — Procesa ventanas de temperatura/humedad del BMP280 con Flatten block.

---

## Lógica de predicción compuesta (MPU)

El relay no actúa en una sola detección. El MPU acumula un historial de las últimas 10 clasificaciones del MCU y evalúa patrones:

```python
history = deque(maxlen=10)

if history.count('sag_leve') >= 3:   → alerta_amarilla (WhatsApp)
if history.count('sag_severo') >= 2: → alerta_roja → relay_off
```

Esta lógica es lo que diferencia Tecovolt de un monitor pasivo: actúa de forma **predictiva** antes del colapso total, desconectando cargas no críticas para proteger el transformador local.

---

## Pipeline de cuantización

```
Edge Impulse Studio (float32)
        │
        ▼
   Exportar modelo
        │
        ▼
Qualcomm AI Hub
   · Cuantización INT8
   · Perfilado de potencia
   · Validación en Dragonwing
        │
        ▼
Librería C++ INT8 (~50 KB por modelo)
        │
        ▼
Deploy en STM32U585 (786 KB RAM / 2 MB ROM)
```

El paso por Qualcomm AI Hub no es un detalle técnico — es la diferencia entre un nodo que dura **12 horas** de batería y uno que dura **72**.
