---
title: Blog
nav_order: 11
---

# Blog
{: .fs-8 }

Actualizaciones y reflexiones del equipo durante el desarrollo de Tecovolt.
{: .fs-5 .fw-300 }

---

## Por qué construimos Tecovolt
**Abril 2025**

Cuando CENACE declaró en alerta al Sistema Eléctrico Nacional por tercer día consecutivo en mayo de 2024, no fue una noticia abstracta para nosotros. Fue el momento en que el taller de la familia dejó de funcionar, cuando el refrigerador del negocio de la esquina perdió toda su mercancía, cuando los equipos médicos domiciliarios se apagaron sin aviso.

Somos de Monterrey, Puebla y CDMX — tres estados directamente golpeados. Lo que más nos frustraba no era el apagón en sí, sino que **nadie podía anticiparlo**.

### El origen de la idea

La pregunta que nos obsesionó: ¿qué pasa en el intervalo entre la anomalía eléctrica y el colapso? Ese momento — milisegundos a veces, segundos otras — es cuando aún hay algo que proteger. Pero ningún dispositivo en el mercado mexicano actúa en ese intervalo.

Sense Energy y Emporia Vue son productos excelentes para el mercado norteamericano. Pero dependen de internet y de la nube. Cuando la red eléctrica falla en México, el internet se va con ella. Son dashboards que te dicen lo que pasó; no hacen nada para evitarlo.

### La apuesta técnica

Decidimos construir un sistema que:
1. **Opera sin internet** — toda la inferencia on-device
2. **Actúa físicamente** — relay que protege antes del colapso
3. **Aprende continuamente** — OTA updates vía Foundries.io
4. **Cuesta menos** — $3,500 MXN vs $6,000 MXN del Sense

El Arduino Uno Q de Qualcomm nos dio la arquitectura perfecta: un MCU para tiempo real y un MPU para comunicación. Dos cerebros, un propósito.

Estamos en Talent Land construyendo el prototipo funcional. Cada dato que capturamos, cada modelo que entrenamos, cada línea de código que flasheamos nos acerca a algo que creemos que México necesita.

---

*Más actualizaciones próximamente...*
