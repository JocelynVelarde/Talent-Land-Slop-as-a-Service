---
title: "Análisis Financiero"
linkTitle: "Financiero"
weight: 7
description: >
  Proyección financiera, modelo de negocio y análisis de break-even del proyecto Tecovolt.
---

## Modelo de negocio

Tecovolt opera con un modelo híbrido de **venta de hardware + suscripción mensual**:

| Concepto | Precio |
|----------|--------|
| **Precio de venta del dispositivo** | $3,500 MXN |
| **Suscripción mensual** (opcional) | $250 MXN |
| **Tasa de suscripción esperada** | 5% de la base instalada |

## Supuestos de la proyección

- **Crecimiento mensual de ventas:** 30%
- **Reinversión de revenue:** 15% destinado a acelerar crecimiento
- **Costo de hardware por unidad (COGS):** ~$1,920 MXN (prototipo)
- **Inicio de operaciones:** Julio 2026
- **Mercado objetivo:** Norteamérica (cercanía + alta tasa de adopción)

## Proyección de ventas — Primer año

| Mes | Dispositivos vendidos | Suscripciones | Revenue total (MXN) |
|-----|----------------------|---------------|-------------------|
| Julio 2026 | 20 | 1 | $70,250 |
| Agosto | 26 | 2 | $91,500 |
| Septiembre | 34 | 4 | $120,000 |
| Octubre | 44 | 6 | $155,500 |
| Noviembre | 57 | 9 | $201,750 |
| Diciembre | 74 | 13 | $262,250 |
| Enero 2027 | 96 | 18 | $340,500 |
| Febrero | 125 | 24 | $443,500 |
| Marzo | 163 | 32 | $578,500 |
| Abril | 212 | 43 | $752,750 |
| Mayo | 276 | 56 | $980,000 |
| Junio | 359 | 74 | $1,275,000 |

**Revenue total primer año: ~$5,271,500 MXN**

Esto representa mucho menos que el 0.1% del mercado de Norteamérica.

## Break-even

Con los supuestos actuales, se proyecta alcanzar el **break-even a mediados de febrero 2027**, aproximadamente 8 meses después del inicio de operaciones.

## Costos fijos mensuales

| Concepto | Costo mensual (MXN) |
|----------|---------------------|
| Auth0 Essentials | $626 |
| Vercel Pro | $358 |
| Dominio | Variable |
| Salarios | $100,000 |
| Renta | $10,000 |
| Móvil | $1,000 |
| Computadoras | $10,000 |
| Contador | $2,000 |
| Gasolina | $1,000 |
| Abogado | $2,000 |
| **Total costos fijos** | **~$127,000** |

## EBITDA

Se proyecta un **EBITDA positivo en marzo 2027**, nueve meses después del inicio de operaciones.

## Reducción de costos a escala

El mayor costo variable es el **COGS (costo de hardware)**. A escala, se espera que este baje significativamente con:

- Diseño de **PCBs** dedicados (eliminando protoboard)
- **Optimización de hardware** (componentes más eficientes)
- **Economías de escala** en compra de componentes
- Negociación directa con proveedores

{{% alert title="Nota" color="info" %}}
La proyección financiera completa está disponible en el repositorio del proyecto. Los números presentados aquí corresponden a la versión de prototipo sin diseño especializado de PCBs ni acceso a economías de escala.
{{% /alert %}}

## Viabilidad

La viabilidad del proyecto no es solo conceptual, sino también financiera. Con un mercado objetivo conservador (0.1% de Norteamérica) y un precio competitivo frente a Sense Energy y Emporia Vue, Tecovolt tiene un camino claro hacia la rentabilidad en menos de un año de operaciones.
