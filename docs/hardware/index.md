---
title: Hardware
nav_order: 6
---

# Hardware

{: .fs-8 }

Un nodo de $1,920 MXN que hace lo que dispositivos de $6,000 MXN no pueden — actuar antes del colapso.
{: .fs-5 .fw-300 }

---

## Bill of Materials

### Hardware

| Componente              | Modelo                   | Rol en el sistema                                       | Precio MXN |
| :---------------------- | :----------------------- | :------------------------------------------------------ | :--------- |
| **Arduino Uno Q 4GB**   | Qualcomm                 | Plataforma principal. MCU STM32U585 + MPU QRB2210 Linux | ~$1,200    |
| **Sensor voltaje AC**   | ZMPT101B                 | Mide voltaje RMS. Detecta sags, swells, micro-cortes    | ~$80       |
| **Sensor corriente**    | ACS712-30A               | Mide demanda de carga en tiempo real vía ADC            | ~$90       |
| **Sensor temp/humedad** | BMP280 / BME280          | Alimenta modelo de riesgo térmico                       | ~$60       |
| **Módulo relay doble**  | 5V optoacoplado          | Desconecta cargas no críticas. Respuesta < 1ms          | ~$70       |
| **Batería LiPo**        | 5000 mAh + MT3608        | Resiliencia durante el apagón                           | ~$180      |
| **Osciloscopio**        | PicoScope 2208B MSO      | Validación y captura de datos. AWG integrado            | —          |
| **Prototipado**         | Caja, protoboard, cables | Materiales para el demo                                 | ~$200      |

**Total estimado del prototipo: ~$1,920 MXN**
{: .fs-5 .fw-700 }

---

## Arduino Uno Q — Dos cerebros, un propósito

| Procesador          | Specs                             | Rol                                                                        |
| :------------------ | :-------------------------------- | :------------------------------------------------------------------------- |
| **MCU (STM32U585)** | 786 KB RAM, 2 MB ROM, Zephyr RTOS | 3 modelos Edge AI en C/C++, latencia sub-ms. ADC 12-bit (`ADC_MAX = 4095`) |
| **MPU (QRB2210)**   | 4 GB RAM, Linux                   | Python, Flask, SQLite, WiFi, Twilio                                        |

---

## Circuito de prototipo

_Setup físico del nodo con sensores, relay y Arduino Uno Q._

<img src="../assets/images/demo/dummy_circuit.png" alt="Circuito de prototipo Tecovolt" style="width:100%; border-radius:6px; margin: 1rem 0;">

---

## Sensores

### ZMPT101B — Voltaje AC

Transformador de voltaje miniatura. Señal analógica proporcional al voltaje de la red (0–250V AC). Se lee vía ADC del MCU a 1 kHz para alimentar el Modelo A.

**Configuración validada:** AC coupling centrado en 0V, ±2V.

| Medición     | Valor                       |
| :----------- | :-------------------------- |
| RMS          | 831.4 mV                    |
| Frecuencia   | 60.02 Hz (nominal mexicana) |
| Crest factor | 1.4445 (teórico: 1.414)     |

### Señales capturadas con el PicoScope

_Señal normal de 60 Hz — baseline de referencia._

<img src="../assets/images/signals/signal_normal.png" alt="Señal normal ZMPT101B" style="width:100%; border-radius:6px; margin: 1rem 0;">

_Señal de outage — RMS cae a ~0.0007 V, diferencia de 164x vs normal._

<img src="../assets/images/signals/signal_outage.png" alt="Señal de outage" style="width:100%; border-radius:6px; margin: 1rem 0;">

_Señal con ruido — perfil de ruido usado para augmentation ×50 del dataset._

<img src="../assets/images/signals/signal_w_noise.png" alt="Señal con ruido" style="width:100%; border-radius:6px; margin: 1rem 0;">

{: .note }

> **Para capturar outage real:** desconectar el ZMPT del tomacorriente durante la captura. Desconectar un calentador solo captura un transitorio de reconexión — el ZMPT sigue viendo la red.

---

### ACS712-30A — Corriente

Sensor de efecto Hall hasta 30A. Sensibilidad nominal: 66 mV/A a 5V. **Factor real medido: 10.52 mV/A** (con divisor de voltaje a 3.3V del STM32).

**Configuración validada: DC coupling a ±5V.**

{: .warning }

> **Lección de calibración:** en AC coupling a ±50mV el offset de 2.5V del ACS712 desaparece y solo queda ruido. El ACS712 **requiere DC coupling** para ver la señal útil. El multímetro promediaba el RMS y filtraba transitorios de < 200ms — exactamente los fenómenos que Tecovolt detecta. El PicoScope fue el único instrumento capaz de revelarlos.

| Carga            | rawRMS       | Potencia |
| :--------------- | :----------- | :------- |
| Sin carga        | 0.00         | 0 W      |
| Un calentador    | 42.81 ± 0.21 | ~950 W   |
| Dos calentadores | 87.60 ± 0.23 | ~1900 W  |

---

### BMP280 — Temperatura y humedad

Sensor ambiental para el tablero eléctrico. 1 Hz. Alimenta el Modelo C de riesgo térmico.

---

## PicoScope 2208B MSO — El validador independiente

_Waveform capturada en vivo durante las pruebas de calibración._

<img src="../assets/images/demo/osciloscope_fir.png" alt="PicoScope capturando señal del ZMPT101B" style="width:100%; border-radius:6px; margin: 1rem 0;">

---

## Actuador — Relay doble 5V

Cierra el loop de protección. Cuando el MPU detecta ≥2 clasificaciones `sag_severo` en historial de 10 ventanas, el MCU activa el relay en **< 1ms** para desconectar cargas no críticas.

---

## Parámetros críticos del firmware

| Parámetro     | Valor            | Razón                                               |
| :------------ | :--------------- | :-------------------------------------------------- |
| `ADC_MAX`     | 4095             | STM32U585 es 12-bit — **no** 1023 del Arduino UNO   |
| `SAMPLE_US`   | 1000             | 1ms = 1 kHz                                         |
| `N_SAMPLES`   | 200              | 200ms de ventana                                    |
| Thread ACS712 | `k_usleep(1000)` | 1 kHz. `k_usleep(100)` daría 10 kHz accidentalmente |

---

## Enclosure — Diseño físico

_Primera iteración del enclosure CAD con todos los componentes posicionados._

<div style="display:flex; gap:1rem; margin: 1rem 0;">
  <img src="../assets/images/demo/cad_it1.jpeg" alt="Enclosure CAD — vista frontal" style="width:49%; border-radius:6px;">
  <img src="../assets/images/demo/cad_it1_2.jpeg" alt="Enclosure CAD — vista lateral" style="width:49%; border-radius:6px;">
</div>

| Especificación       | Detalle                                                            |
| :------------------- | :----------------------------------------------------------------- |
| **Grado IP55**       | Caja sellada apta para instalación exterior                        |
| **Aislamiento 127V** | Transformadores + optoacopladores = aislamiento galvánico completo |
| **Enclosure CAD**    | Listo para impresión 3D                                            |
