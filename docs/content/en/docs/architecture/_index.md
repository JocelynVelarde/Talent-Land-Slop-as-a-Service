---
title: "Arquitectura Técnica"
linkTitle: "Arquitectura"
weight: 3
description: >
  Diseño dual MCU + MPU, pipeline de datos, stack de software y flujo de operación del sistema Tecovolt.
---

## Visión general

Tecovolt es técnicamente complejo por una razón central: **un sistema de protección eléctrica no puede depender de la nube ni tolerar latencias de red.** Cada decisión de diseño parte de ese principio. El dispositivo se instala junto al tablero eléctrico del hogar y opera de forma completamente autónoma, incluso cuando el internet cae junto con la luz.

## Arquitectura dual MCU + MPU

La decisión de diseño más importante es la **separación deliberada de responsabilidades** entre los dos procesadores del Arduino Uno Q:

### MCU · STM32U585 (C/C++)

El microcontrolador se dedica exclusivamente a tareas de tiempo real:

- Muestreo ADC a **1 kHz**
- Inferencia de **3 modelos en paralelo**
- Activación del relay físico **< 1ms**
- Sin red, sin logs, sin OS — latencia cero

### MPU · QRB2210 (Python / Linux)

El microprocesador gestiona todo lo que requiere sistema operativo:

- Lógica de alerta compuesta (buffer MCU)
- Logger **SQLite** de eventos históricos
- Dashboard **Flask** + alertas **Twilio WhatsApp**
- OTA model updates vía **Foundries.io**

> Esta separación garantiza que, pase lo que pase en la red, **la respuesta física nunca se bloquee.**

## Stack de software e IA

| Herramienta | Propósito |
|-------------|-----------|
| **Edge Impulse Studio** | Entrenamiento de los 3 modelos. Custom DSP blocks (`tecovolt_block`, `tecotemp_block`) en Python vía Docker |
| **Qualcomm AI Hub** | Cuantización INT8 y perfilado energético. Reducción de ~200 KB a ~50 KB por modelo |
| **Arduino App Lab + Foundries.io** | Entorno oficial de desarrollo para Uno Q. OTA updates en campo |
| **Flask + SQLite** | Dashboard web histórico en el MPU. Logger de eventos a 1 Hz |
| **Twilio WhatsApp API** | Canal de alertas bidireccional. Notificaciones de riesgo + comandos de relay |

## Flujo de operación

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│ 1. Entrenamiento│    │ 2. Optimización  │    │ 3. Desarrollo y     │
│ Edge Impulse    │───▶│ Qualcomm AI Hub  │───▶│    Deploy           │
│ Studio          │    │                  │    │ Arduino App Lab     │
│                 │    │ · Cuantización   │    │                     │
│ · 3 modelos     │    │   INT8           │    │ · C/C++ en MCU      │
│ · Custom DSP    │    │ · Perfilado de   │    │ · Python en MPU     │
│ · Export C++/Py │    │   potencia       │    │ · Entorno Uno Q     │
└─────────────────┘    │ · Validación en  │    └──────────┬──────────┘
                       │   Dragonwing     │               │
                       └──────────────────┘               │
                                                          ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│ 5. Notificación │    │ 4. Actualización │    │   Nodo desplegado   │
│ Twilio WhatsApp │◀───│ Foundries.io OTA │◀───│                     │
│                 │    │                  │    │ Evento de riesgo ──▶│
│ · Alertas       │    │ · Remota         │    │ Comando usuario ◀──│
│ · Comandos      │    │ · Gestión de     │    │                     │
│ · Control relay │    │   modelos        │    └─────────────────────┘
└─────────────────┘    │ · Escalabilidad  │
                       └──────────────────┘
```

## Seguridad y robustez

| Especificación | Detalle |
|---------------|---------|
| **Grado IP55** | Caja sellada apta para instalación exterior junto al tablero eléctrico |
| **127V aislados** | Zona de alto voltaje físicamente separada del procesador mediante transformadores y optoacopladores |
| **Enclosure CAD** | Diseñado con todos los componentes posicionados, listo para impresión 3D |

## Comunicación serial MCU ↔ MPU

La comunicación entre procesadores ocurre vía **UART serial** con un protocolo JSON ligero. El MCU envía lecturas y predicciones al MPU, que las procesa para logging y alertas. Esta separación asegura que un crash en el MPU nunca afecte la capacidad del MCU de activar el relay.
