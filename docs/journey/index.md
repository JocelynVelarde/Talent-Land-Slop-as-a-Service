---
title: Nuestro Journey
nav_order: 10
---

# Nuestro Journey

{: .fs-8 }

De la idea a 99.3% accuracy en 72 horas — hitos, bugs, decisiones y lo que aprendimos en el camino.
{: .fs-5 .fw-300 }

---

## ✅ Completado

### Arquitectura y diseño

- Definición de arquitectura MCU/MPU y separación deliberada de responsabilidades
- Diseño CAD del enclosure con todos los componentes posicionados — listo para impresión 3D

### Calibración de sensores — Día 2

- Diagnóstico y fix DC vs AC coupling en ACS712-30A
- Factor empírico medido: 10.52 mV/A (divisor de voltaje a 3.3V)
- Sustitución de cable de bajo calibre que generaba caídas de voltaje internas
- Validación ZMPT101B: 60.02 Hz, crest factor 1.4445

### Captura de datos reales — Día 2

- Dataset de voltaje: CSVs desde PicoScope 7, 6279.8 Hz, ventana 200 ms
- Dataset de corriente: 48 ventanas reales vía Monitor de Arduino App Lab
- Valores medidos: rawRMS 0.00 / 42.81 / 87.60 (sin carga / 950 W / 1900 W)

### Pipeline de datos e IA

- `tecovolt_synth.py`, `tecovolt_pipeline_v2.py`, `tecovolt_temp_synth.py`, `tecovolt_demand_synth.py`
- Custom DSP blocks: `tecovolt_block` (6 features + THD) y `tecotemp_block`
- Fix bug crítico: `fs=6279.8` → `fs=1000.0` en `dsp.py`

### Iteraciones del modelo A (voltaje)

- v1: 94.5% — sintético puro
- v2: 63.7% — dataset mixto, bug fs detectado
- v3: 63% — THD agregado, bug aún presente
- **v4: 99.3%, AUC=1.00 — bug corregido + separación agresiva en synth**

### Software e integración

- Lógica de predicción compuesta en MPU: `deque(maxlen=10)`, umbrales por patrón acumulado
- Script AWG `tecovolt_demo_awg.py`: secuencia automatizada de ~60 s para el demo
- Twilio WhatsApp API configurada en el MPU
- GitHub Actions para gestión automática de labels

### Firmware

- `tecovolt_voltage_daq.ino`: 200 samples @ 1 kHz, formato `label,s0..s199`
- `tecovolt_daq.ino`: ACS712 con `delay(600)` y output CSV limpio
- Fix `Monitor.readStringUntil`: carácter a carácter para `\r\n` o `\r`
- Fix `dsp-server.py`: guiones en parámetros JSON → underscores

---

## 🔄 En curso

- Deployment de modelos cuantizados INT8 en el STM32U585
- Integración MCU ↔ MPU vía RouterBridge
- Pitch final para el jurado Qualcomm

---

## ⬜ Pendiente

- Dashboard Flask funcional en el MPU
- Logger SQLite de eventos históricos
- Pruebas end-to-end: sensor → modelo → relay → WhatsApp
- Optimización final vía Qualcomm AI Hub con datos reales
- Impresión 3D del enclosure

---

## Archivos generados

| Archivo                    | Descripción                                                           |
| :------------------------- | :-------------------------------------------------------------------- |
| `tecovolt_pipeline_v2.py`  | Pipeline PicoScope 2208B → Edge Impulse. 6 features, augmentation ×50 |
| `dsp.py`                   | DSP block custom — 6 features + THD, `fs=1000 Hz`                     |
| `dsp-server.py`            | Servidor HTTP para EI con fix `scale-axes` → underscore               |
| `tecovolt_demand_synth.py` | Generador sintético de demanda anclado a valores reales               |
| `tecovolt_capture.py`      | Captura Serial → CSV para modelo de demanda                           |
| `tecovolt_daq.ino`         | Sketch ACS712 con `delay(600)` y output CSV limpio                    |
| `tecovolt_voltage_daq.ino` | Sketch ZMPT101B, formato `label,s0..s199`                             |
| `ei_voltage_train_v3.csv`  | Dataset voltaje: 1440 train, 6 clases                                 |
| `ei_voltage_test_v3.csv`   | Test set voltaje: 360 muestras reales                                 |
| `demand_train_final.csv`   | Dataset demanda: 638 train (600 sintéticos + 38 reales)               |
| `tecovolt_demo_awg.py`     | Automatización AWG PicoScope para demo (~60 s)                        |

---

## Gestión del proyecto

| Label         | Área                                       |
| :------------ | :----------------------------------------- |
| `hardware`    | Ensamblaje físico, circuitos, enclosure    |
| `firmware`    | Código MCU (C/C++), Zephyr RTOS            |
| `software`    | Código MPU (Python), Flask, SQLite         |
| `edge-ai`     | Modelos, Edge Impulse, Qualcomm AI Hub     |
| `integración` | Pruebas end-to-end, comunicación MCU ↔ MPU |

---

[Ver el repositorio completo en GitHub →](https://github.com/JocelynVelarde/Talent-Land-Slop-as-a-Service){: .btn .btn-primary }
