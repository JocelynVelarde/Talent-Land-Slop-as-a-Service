---
title: Nuestro Journey
nav_order: 9
---

# Nuestro Journey
{: .fs-8 }

El camino del equipo SAAS durante el hackathon: hitos, progreso y próximos pasos.
{: .fs-5 .fw-300 }

---

## ✅ Hitos completados

### Arquitectura y diseño
- Definición de arquitectura MCU/MPU y separación deliberada de responsabilidades
- Diseño CAD del enclosure con todos los componentes posicionados — listo para impresión 3D

### Pipeline de datos e IA
- Pipeline de datos sintéticos: `tecovolt_synth.py`, `tecovolt_pipeline.py`, `tecovolt_temp_synth.py`, `tecovolt_demand_synth.py`
- Custom DSP blocks en Edge Impulse: `tecovolt_block` (voltaje) y `tecotemp_block` (temperatura)
- 1er entrenamiento Modelo A — accuracy 92.6%
- **2do entrenamiento Modelo A — accuracy 94.5%**
- 1er entrenamiento Modelo C — accuracy 87.5%

### Software e integración
- Configuración de Twilio WhatsApp API en el MPU
- Repositorio en GitHub con backlog de issues etiquetados
- GitHub Actions para gestión automática de labels

### Validación
- Campaña de validación de mercado en Facebook — encuesta con usuarios reales

---

## 🔄 En curso

- Recopilación de datos reales de corriente con ACS712
- Deployment de modelos cuantizados INT8 en el STM32U585
- Aterrizaje del pitch final para jurado Qualcomm
- Debugging de almacenamiento no identificado en el sistema

---

## ⬜ Pendiente

- Reentrenamiento de los 3 modelos con datos reales del hardware
- Integración completa MCU ↔ MPU vía UART serial
- Dashboard Flask funcional en el MPU
- Logger SQLite de eventos históricos
- Pruebas end-to-end (sensor → modelo → relay → WhatsApp)
- Optimización de modelos vía Qualcomm AI Hub con datos reales
- Impresión 3D del enclosure
- Documentación final para entrega

---

## Gestión del proyecto

El proyecto se gestiona con GitHub Projects:

| Columna | Descripción |
|:--------|:------------|
| **Backlog** | Issues pendientes de iniciar |
| **Ready** | Listos para trabajar |
| **In progress** | Trabajo activo |
| **In review** | En revisión |
| **Done** | Completados |

### Labels de issues

| Label | Área |
|:------|:-----|
| `hardware` | Ensamblaje físico, circuitos, enclosure |
| `firmware` | Código MCU (C/C++), Zephyr RTOS |
| `software` | Código MPU (Python), Flask, SQLite |
| `edge-ai` | Modelos, Edge Impulse, Qualcomm AI Hub |
| `integración` | Pruebas end-to-end, comunicación MCU ↔ MPU |

---

## Línea de tiempo

### Semana 1 — Ideación
- Investigación del problema energético en México
- Diseño de arquitectura técnica
- Primer pipeline de datos sintéticos
- Entrega de documento de ideación

### Semana 2 — Desarrollo
- Custom DSP blocks en Edge Impulse
- Entrenamiento de modelos A, B, C
- Configuración de hardware (sensores + relay)
- Setup de Twilio WhatsApp
- Diseño CAD del enclosure

### Semana 3 — Integración (Talent Land)
- Deployment de modelos en Arduino Uno Q
- Captura de datos reales
- Integración MCU ↔ MPU
- Pruebas end-to-end
- Demo para jurado Qualcomm

---

[Ver el repositorio completo en GitHub →](https://github.com/JocelynVelarde/Talent-Land-Slop-as-a-Service){: .btn .btn-primary }
