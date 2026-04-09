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

## Modelo A · Anomalía de voltaje

| Parámetro | Valor |
|:----------|:------|
| **Tipo** | Clasificador de 6 clases |
| **Bloque DSP** | Custom `tecovolt_block` (5 features físicas) |
| **Frecuencia** | 1000 Hz |
| **Ventana** | 200 ms, stride 200 ms (sin overlap) |
| **Clases** | `normal`, `sag_leve`, `sag_severo`, `swell`, `outage`, `flicker` |

### Features extraídas

- **RMS (mV):** Voltaje eficaz de la ventana
- **Peak-to-peak (mV):** Rango máximo de la señal
- **Crest factor:** Relación pico/RMS — indicador de distorsión
- **RMS ripple (mV):** Variabilidad del RMS — detecta flicker
- **Frecuencia dominante (Hz):** Componente frecuencial principal

### Dataset

Datos sintéticos generados con `tecovolt_synth.py`, calibrados con **PicoScope 2208B** usando señales reales de la red eléctrica de Puebla, MX. El AWG del PicoScope permite crear condiciones controladas de cada clase.

### Resultados de entrenamiento

| Iteración | Accuracy (float32) | Notas |
|:----------|:-------------------|:------|
| 1er entrenamiento | 92.6% | Confusión: `sag_leve` ↔ `normal` en bordes de RMS |
| **2do entrenamiento** | **94.5%** | +100 ciclos, Flatten layer, dataset ampliado en clases con traslape |

{: .warning }
> **Pendiente:** Reentrenamiento con datos reales capturados del ACS712 y ZMPT101B en el Arduino Uno Q.

---

## Modelo B · Riesgo térmico

| Parámetro | Valor |
|:----------|:------|
| **Tipo** | Clasificador de 3 clases |
| **Bloque DSP** | Flatten (temperatura cambia lento — sin análisis frecuencial) |
| **Frecuencia** | 1 Hz (BMP280) |
| **Ventana** | 10 muestras = 10 s |
| **Clases** | `bajo` (20–45 °C), `medio` (45–65 °C), `alto` (65–90 °C + baja humedad) |

**Features:** `avg_temperature` y `avg_humidity` por ventana de 10 muestras.

**Dataset:** Datos sintéticos (`tecovolt_temp_synth.py`). 150 ventanas × 3 clases = 450 total, split 80/20.

---

## Modelo C · Predicción de demanda

| Parámetro | Valor |
|:----------|:------|
| **Tipo** | Clasificador de 3 clases |
| **Bloque DSP** | Flatten |
| **Frecuencia** | ~1.67 Hz (thread Zephyr: 1000 muestras ADC a 10 kHz + 500 ms sleep) |
| **Ventana** | 10 lecturas de rawRMS |
| **Clases** | `baja` (rawRMS < 3.0), `media` (3.0–120), `alta` (rawRMS ≥ 120) |

### Dataset base

| Clase | Fuente | rawRMS |
|:------|:-------|:-------|
| Baja | Datos reales PicoScope | ≈ 0.0 (sin carga) |
| Alta | Datos reales PicoScope | ≈ 169.5 (dos calentadores ~1900 W) |
| Media | Estimado (pendiente) | Captura real pendiente con ~950 W |

**1er entrenamiento:** Accuracy = 87.5%. Confusión: `media` vs. `alta` (clase media usa rawRMS estimado, no real).

{: .note }
> **En curso:** Captura real de clase 'media' con ACS712 y carga de ~950 W para mejorar el modelo.

---

## Custom DSP Blocks

A diferencia del flujo estándar de Edge Impulse, Tecovolt implementa **bloques DSP custom** desplegados vía Docker:

**`tecovolt_block` (Voltaje)** — Extrae las 5 features físicas relevantes para clasificación de anomalías de voltaje. Implementado en Python, empaquetado en Docker y registrado en Edge Impulse Studio como bloque personalizado.

**`tecotemp_block` (Temperatura)** — Procesa las ventanas de temperatura y humedad del BMP280 con un Flatten block optimizado para señales de baja frecuencia.

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
