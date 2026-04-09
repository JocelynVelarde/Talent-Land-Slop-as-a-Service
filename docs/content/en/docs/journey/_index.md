---
title: "Nuestro Journey"
linkTitle: "Journey"
weight: 8
description: >
  El camino del equipo SAAS durante el hackathon: hitos completados, trabajo en curso y próximos pasos.
---

## Hitos completados

### Arquitectura y diseño

- ✅ Definición de arquitectura MCU/MPU y separación deliberada de responsabilidades
- ✅ Diseño CAD del enclosure con todos los componentes posicionados (Arduino Uno Q, ZMPT101B, ACS712, BMP280, relay, LiPo) — listo para impresión 3D

### Pipeline de datos e IA

- ✅ Pipeline de datos sintéticos: `tecovolt_synth.py`, `tecovolt_pipeline.py`, `tecovolt_temp_synth.py`, `tecovolt_demand_synth.py`
- ✅ Custom DSP blocks desplegables en Edge Impulse: `tecovolt_block` (voltaje) y `tecotemp_block` (temperatura)
- ✅ 1er entrenamiento del Modelo A — accuracy 92.6%
- ✅ **2do entrenamiento del Modelo A — accuracy 94.5%** (mejoras: +100 ciclos, Flatten layer, dataset ampliado)
- ✅ 1er entrenamiento del Modelo C — accuracy 87.5%

### Software e integración

- ✅ Configuración de Twilio WhatsApp API en el MPU
- ✅ Repositorio en GitHub con backlog de issues etiquetados (hardware, firmware, software, edge-ai, integración)
- ✅ GitHub Actions para gestión automática de labels

### Validación

- ✅ Campaña de validación de mercado en Facebook — encuesta con usuarios reales para validar disposición a pagar y casos de uso

## En curso

- 🔄 Recopilación de datos reales de corriente con ACS712 — captura física de clase 'media' de demanda
- 🔄 Deployment de modelos cuantizados INT8 en el STM32U585 (debugging activo de pipeline de flasheo)
- 🔄 Aterrizaje del pitch final para jurado Qualcomm
- 🔄 Debugging de 6.6 GB de almacenamiento no identificado en el sistema

## Pendiente

- ⬜ Reentrenamiento de los 3 modelos con datos reales del hardware
- ⬜ Integración completa MCU ↔ MPU vía UART serial
- ⬜ Dashboard Flask funcional en el MPU
- ⬜ Logger SQLite de eventos históricos
- ⬜ Pruebas end-to-end del flujo completo (sensor → modelo → relay → WhatsApp)
- ⬜ Optimización de modelos vía Qualcomm AI Hub con datos reales
- ⬜ Impresión 3D del enclosure
- ⬜ Documentación final para entrega

## Backlog del repositorio

El proyecto se gestiona con un board de GitHub Projects con las siguientes columnas:

- **Backlog** — Issues pendientes de iniciar
- **Ready** — Listos para trabajar
- **In progress** — Trabajo activo
- **In review** — En revisión
- **Done** — Completados

### Issues activos

Los issues están etiquetados por área:

| Label | Área |
|-------|------|
| `hardware` | Ensamblaje físico, circuitos, enclosure |
| `firmware` | Código MCU (C/C++), Zephyr RTOS |
| `software` | Código MPU (Python), Flask, SQLite |
| `edge-ai` | Modelos, Edge Impulse, Qualcomm AI Hub |
| `integración` | Pruebas end-to-end, comunicación MCU ↔ MPU |

{{% alert title="Repositorio" color="primary" %}}
[Ver el repositorio completo en GitHub →](https://github.com/JocelynVelarde/Talent-Land-Slop-as-a-Service)
{{% /alert %}}

## Línea de tiempo

```
Semana 1 (Ideación)
├── Investigación del problema energético en México
├── Diseño de arquitectura técnica
├── Primer pipeline de datos sintéticos
└── Entrega de documento de ideación

Semana 2 (Desarrollo)
├── Custom DSP blocks en Edge Impulse
├── Entrenamiento de modelos A, B, C
├── Configuración de hardware (sensores + relay)
├── Setup de Twilio WhatsApp
└── Diseño CAD del enclosure

Semana 3 (Integración — Talent Land)
├── Deployment de modelos en Arduino Uno Q
├── Captura de datos reales
├── Integración MCU ↔ MPU
├── Pruebas end-to-end
└── Demo para jurado Qualcomm
```
