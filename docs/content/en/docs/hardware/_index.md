---
title: "Hardware"
linkTitle: "Hardware"
weight: 5
description: >
  Bill of materials, sensores, actuadores y diseño físico del nodo Tecovolt.
---

## Stack de hardware

| Componente | Modelo | Rol en el sistema | Precio MXN |
|-----------|--------|-------------------|------------|
| **Arduino Uno Q 4GB** | Qualcomm | Plataforma principal. MCU STM32U585 ejecuta inferencia a < 1ms; MPU QRB2210 con Linux gestiona comunicación y logs | ~$1,200 |
| **Sensor voltaje AC** | ZMPT101B | Mide voltaje RMS. Detecta sags, swells, micro-cortes y variaciones de frecuencia. Ajuste via potenciómetro | ~$80 |
| **Sensor corriente** | ACS712-30A | Mide la demanda de carga en tiempo real. Captura rawRMS via ADC del MCU a ~1.67 Hz efectivos | ~$90 |
| **Sensor temp/humedad** | BMP280 / BME280 | Captura temperatura y humedad del tablero. Alimenta el modelo de riesgo térmico en Edge Impulse | ~$60 |
| **Módulo relay doble** | 5V optoacoplado | Actuador físico. Desconecta cargas no críticas cuando el modelo detecta riesgo alto. Respuesta < 1ms | ~$70 |
| **Batería LiPo** | 5000 mAh + MT3608 | Resiliencia durante el apagón. Módulo MT3608 boost para regulación de voltaje | ~$180 |
| **Osciloscopio** | PicoScope 2208B MSO | Instrumento de validación y captura de datos. AWG integrado para señales de prueba controladas | — |
| **Prototipado** | Caja, protoboard, cables | Materiales de prototipado para el demo | ~$200 |

**Total estimado del prototipo: ~$1,920 MXN**

## Arduino Uno Q — La plataforma

El Arduino Uno Q de Qualcomm es el corazón del sistema. Su arquitectura de doble procesador es lo que permite la separación deliberada de responsabilidades:

- **MCU (STM32U585):** 786 KB RAM, 2 MB ROM. Corre Zephyr RTOS. Ejecuta los 3 modelos de Edge AI en C/C++ con latencia sub-milisegundo.
- **MPU (QRB2210):** 4 GB RAM, Linux. Corre Python, Flask, SQLite, y gestiona WiFi/Twilio.

{{% alert title="Nota sobre el datasheet" color="info" %}}
El datasheet completo del Arduino Uno Q (ABX00162) está disponible en la documentación oficial de Arduino. Consultar las especificaciones de pines y voltajes para replicar el circuito.
{{% /alert %}}

## Sensores

### ZMPT101B — Voltaje AC

Transformador de voltaje miniatura que proporciona una señal analógica proporcional al voltaje de la red. Rango de medición: 0-250V AC. La señal se lee vía ADC del MCU a 1 kHz para alimentar el Modelo A de anomalías de voltaje.

### ACS712-30A — Corriente

Sensor de efecto Hall que mide corriente AC/DC hasta 30A. Proporciona el rawRMS que alimenta el Modelo C de predicción de demanda. Frecuencia de muestreo efectiva: ~1.67 Hz.

### BMP280 — Temperatura y humedad

Sensor ambiental que captura las condiciones del tablero eléctrico. Frecuencia: 1 Hz. Sus lecturas alimentan el Modelo B de riesgo térmico con un enfoque de clasificación simple (Flatten block).

## Actuador — Relay doble 5V

El relay optoacoplado cierra el loop de protección. Cuando cualquiera de los 3 modelos detecta una condición de riesgo alto, el MCU activa el relay en menos de 1ms para desconectar cargas no críticas del circuito.

## Diseño físico

### Enclosure

- **Grado IP55:** Apto para instalación exterior junto al tablero eléctrico
- **Aislamiento 127V:** Zona de alto voltaje separada del procesador mediante transformadores y optoacopladores
- **Diseño CAD completo:** Todos los componentes posicionados (Arduino Uno Q, ZMPT101B, ACS712, BMP280, relay, LiPo), listo para impresión 3D

### Consideraciones de seguridad

La separación física entre la zona de alto voltaje (red eléctrica) y la zona de bajo voltaje (procesador) es crítica. Los transformadores del ZMPT101B y los optoacopladores del relay proporcionan aislamiento galvánico completo.

## Software stack del hardware

| Herramienta | Rol |
|------------|-----|
| **Edge Impulse Studio** | Entrenamiento de modelos de anomalía, riesgo térmico y predicción de demanda |
| **Qualcomm AI Hub** | Cuantización INT8 para maximizar velocidad de inferencia |
| **Arduino App Lab + Foundries.io** | Entorno oficial de desarrollo para Uno Q. OTA updates |
| **Twilio** | Integración por WhatsApp para alertas y mensajes autónomos |

Todas las herramientas de software tienen costo **$0** — son gratuitas o parte del ecosistema Qualcomm.
