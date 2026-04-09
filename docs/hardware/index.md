---
title: Hardware
nav_order: 6
---

# Hardware
{: .fs-8 }

Bill of materials, sensores, actuadores y diseño físico del nodo Tecovolt.
{: .fs-5 .fw-300 }

---

## Bill of Materials

### Hardware

| Componente | Modelo | Rol en el sistema | Precio MXN |
|:-----------|:-------|:------------------|:-----------|
| **Arduino Uno Q 4GB** | Qualcomm | Plataforma principal. MCU STM32U585 + MPU QRB2210 Linux | ~$1,200 |
| **Sensor voltaje AC** | ZMPT101B | Mide voltaje RMS. Detecta sags, swells, micro-cortes | ~$80 |
| **Sensor corriente** | ACS712-30A | Mide demanda de carga en tiempo real vía ADC | ~$90 |
| **Sensor temp/humedad** | BMP280 / BME280 | Alimenta modelo de riesgo térmico en Edge Impulse | ~$60 |
| **Módulo relay doble** | 5V optoacoplado | Desconecta cargas no críticas. Respuesta < 1ms | ~$70 |
| **Batería LiPo** | 5000 mAh + MT3608 | Resiliencia durante el apagón | ~$180 |
| **Osciloscopio** | PicoScope 2208B MSO | Validación y captura de datos. AWG integrado | — |
| **Prototipado** | Caja, protoboard, cables | Materiales para el demo | ~$200 |

### Software (todo gratuito)

| Herramienta | Rol |
|:------------|:----|
| **Edge Impulse Studio** | Entrenamiento de los 3 modelos |
| **Qualcomm AI Hub** | Cuantización INT8 |
| **Arduino App Lab + Foundries.io** | Desarrollo + OTA updates |
| **Twilio** | Alertas WhatsApp |

**Total estimado del prototipo: ~$1,920 MXN**
{: .fs-5 .fw-700 }

---

## Arduino Uno Q — La plataforma

El Arduino Uno Q de Qualcomm es el corazón del sistema. Su arquitectura de doble procesador permite la separación deliberada de responsabilidades:

| Procesador | Specs | Rol |
|:-----------|:------|:----|
| **MCU (STM32U585)** | 786 KB RAM, 2 MB ROM, Zephyr RTOS | Ejecuta 3 modelos Edge AI en C/C++, latencia sub-milisegundo |
| **MPU (QRB2210)** | 4 GB RAM, Linux | Python, Flask, SQLite, WiFi/Twilio |

---

## Sensores

### ZMPT101B — Voltaje AC

Transformador de voltaje miniatura. Señal analógica proporcional al voltaje de la red (0–250V AC). Se lee vía ADC del MCU a 1 kHz para alimentar el Modelo A de anomalías de voltaje. Ajuste de ganancia via potenciómetro.

### ACS712-30A — Corriente

Sensor de efecto Hall para corriente AC/DC hasta 30A. Proporciona el rawRMS que alimenta el Modelo C de predicción de demanda. Frecuencia de muestreo efectiva: ~1.67 Hz.

### BMP280 — Temperatura y humedad

Sensor ambiental para las condiciones del tablero eléctrico. Frecuencia: 1 Hz. Alimenta el Modelo B de riesgo térmico con clasificación simple (Flatten block).

---

## Actuador — Relay doble 5V

El relay optoacoplado cierra el loop de protección. Cuando cualquiera de los 3 modelos detecta riesgo alto, el MCU activa el relay en **menos de 1ms** para desconectar cargas no críticas.

---

## Diseño físico

| Especificación | Detalle |
|:--------------|:--------|
| **Grado IP55** | Caja sellada apta para instalación exterior |
| **Aislamiento 127V** | Transformadores + optoacopladores = aislamiento galvánico completo |
| **Enclosure CAD** | Todos los componentes posicionados, listo para impresión 3D |

La separación física entre la zona de alto voltaje (red eléctrica) y la zona de bajo voltaje (procesador) es crítica para la seguridad del usuario.
