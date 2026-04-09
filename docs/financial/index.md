---
title: Análisis Financiero
nav_order: 8
---

# Análisis Financiero
{: .fs-8 }

Proyección financiera, modelo de negocio y análisis de break-even.
{: .fs-5 .fw-300 }

---

## Modelo de negocio

| Concepto | Precio |
|:---------|:-------|
| **Venta del dispositivo** | $3,500 MXN |
| **Suscripción mensual** (opcional) | $250 MXN |
| **Tasa de suscripción esperada** | 5% de la base instalada |

---

## Supuestos de la proyección

- **Crecimiento mensual de ventas:** 30%
- **Reinversión de revenue:** 15%
- **COGS por unidad:** ~$1,920 MXN (prototipo)
- **Inicio de operaciones:** Julio 2026
- **Mercado objetivo:** Norteamérica

---

## Proyección de ventas — Primer año

| Mes | Dispositivos | Suscripciones | Revenue (MXN) |
|:----|:-------------|:--------------|:--------------|
| Jul 2026 | 20 | 1 | $70,250 |
| Ago | 26 | 2 | $91,500 |
| Sep | 34 | 4 | $120,000 |
| Oct | 44 | 6 | $155,500 |
| Nov | 57 | 9 | $201,750 |
| Dic | 74 | 13 | $262,250 |
| Ene 2027 | 96 | 18 | $340,500 |
| Feb | 125 | 24 | $443,500 |
| Mar | 163 | 32 | $578,500 |
| Abr | 212 | 43 | $752,750 |
| May | 276 | 56 | $980,000 |
| Jun | 359 | 74 | $1,275,000 |

**Revenue total primer año: ~$5,271,500 MXN** (< 0.1% del mercado de Norteamérica)
{: .fs-5 .fw-700 }

---

## Hitos financieros

| Hito | Fecha proyectada |
|:-----|:-----------------|
| **Break-even** | Febrero 2027 (~8 meses) |
| **EBITDA positivo** | Marzo 2027 (~9 meses) |

---

## Costos fijos mensuales

| Concepto | Costo (MXN) |
|:---------|:------------|
| Salarios | $100,000 |
| Renta | $10,000 |
| Computadoras | $10,000 |
| Auth0 Essentials | $626 |
| Vercel Pro | $358 |
| Contador | $2,000 |
| Abogado | $2,000 |
| Gasolina | $1,000 |
| Móvil | $1,000 |
| **Total** | **~$127,000** |

---

## Reducción de costos a escala

El mayor costo variable es el **COGS (hardware)**. A escala se reduce con:

- Diseño de **PCBs dedicados** (eliminando protoboard)
- **Optimización de componentes**
- **Economías de escala** en compras
- Negociación directa con proveedores

{: .note }
> La proyección completa está disponible en el repositorio del proyecto. Los números corresponden a la versión de prototipo sin PCBs especializados ni economías de escala.
