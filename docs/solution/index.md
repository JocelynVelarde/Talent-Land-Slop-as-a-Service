---
title: La Solución
nav_order: 3
---

# Tecovolt: La Solución

{: .fs-8 }

Un nodo inteligente instalado junto al tablero eléctrico del hogar que detecta, anticipa y responde a fallas eléctricas de forma autónoma.
{: .fs-5 .fw-300 }

---

## ¿Qué es Tecovolt?

Un dispositivo embebido construido sobre el **Arduino Uno Q de Qualcomm** que opera **sin internet ni intervención humana**.

> No reacciona al apagón. Lo predice. El sistema actúa en el intervalo entre la anomalía y el colapso — el momento en que aún hay algo que proteger.

---

## Tres capacidades integradas

### ⚡ Detecta

3 modelos Edge AI corriendo en tiempo real sobre el MCU STM32U585:

- **Anomalías de voltaje** (6 clases): normal, sag_leve, sag_severo, swell, outage, flicker — **99.3% accuracy**
- **Riesgo térmico** del tablero (3 niveles): bajo, medio, alto
- **Predicción de nivel de demanda**: baja, media, alta

Toda la inferencia ocurre on-device sin latencia de red.

### 🛡️ Actúa

- Relay físico que protege el transformador local antes del colapso
- **Respuesta autónoma < 1ms**
- Lógica de predicción compuesta: el MPU acumula historial de las últimas 10 clasificaciones antes de actuar — no reacciona a detecciones aisladas
- Desconecta cargas no críticas cuando el modelo detecta patrón de riesgo sostenido
- Batería LiPo 5000 mAh mantiene el nodo operativo durante el apagón

### 📱 Notifica

- Alertas concretas por **WhatsApp vía Twilio** al momento crítico
- Instrucciones de acción para el usuario
- Comandos remotos bidireccionales para controlar el relay
- Canal más usado en México como medio de comunicación

---

## ¿Qué nos hace diferentes?

Las soluciones más avanzadas del mercado — **Sense Energy Monitor** (~$299 USD) y **Emporia Vue 3** (~$100 USD) — comparten limitaciones estructurales que las hacen inviables para México y Latinoamérica:

| Característica              | Sense / Emporia  | Tecovolt               |
| :-------------------------- | :--------------- | :--------------------- |
| Requiere internet           | ✅ Sí            | ❌ No                  |
| Procesamiento en la nube    | ✅ Sí            | ❌ On-device           |
| Actuación física ante falla | ❌ No            | ✅ Relay < 1ms         |
| Funciona durante apagón     | ❌ No            | ✅ Batería de respaldo |
| Precio objetivo             | $2,000–6,000 MXN | **~$3,500 MXN**        |

**Cuando la red falla, el internet del hogar se va con ella.** Por eso toda la inferencia ocurre en el dispositivo, sin una sola petición a la nube.

---

## Seis decisiones de diseño clave

**1. Qualcomm AI Hub + Dragonwing**
Cuantización INT8 y perfilado de potencia. La diferencia entre un nodo que dura 12 horas de batería y uno que dura 72.

**2. Tres modelos simultáneos en un solo MCU**
No un modelo, una tarea, un sensor. Tres modelos en paralelo en tiempo real con gestión de memoria embebida en 786 KB RAM.

**3. Arquitectura dual MCU + MPU conscientemente separada**
C/C++ en el microcontrolador para inferencia < 1ms, Python en el microprocesador para lógica de predicción compuesta y comunicación.

**4. Actuación física con relay**
Cierra el loop de protección. No es un dashboard con alertas — es una respuesta autónoma instalable.

**5. OTA vía Foundries.io**
Cada mejora del modelo se despliega en todos los nodos activos sin intervención física.

**6. DSP block custom con THD**
Feature de Total Harmonic Distortion que detecta `flicker` por distorsión armónica, no por amplitud — imposible con los bloques estándar de Edge Impulse. Flicker y normal tienen el mismo RMS; el THD los separa con una diferencia de 10–20x.
