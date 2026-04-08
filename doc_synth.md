## Docs Tecovoltianos Impulse

### tecovolt_synth.py

> basically crea los datos de acuerdo a la red eléctrica mexicana, agrega ruido sintético compatible con las condiciones de aglomeraciones urbanas y/o rurales.

Toma en cuenta los factores de ruido del Periscope para una aplicación on the edge.

### tecovolt_pipeline.py

> lee los csvs de el dir seleccionado, calcula las features necesarias para el classifier + at the same time hace augmentation para poder tener un insight

Features:

1. RMS,
2. peak-to-peak,
3. crest factor,
4. RMS ripple,
5. freq dominante

El ruido medido se basa en datos realistas del picoscope 2000.

```python
N_SAMPLES   = 1260      # muestras por waveform (PicoScope 200ms @ 6280Hz)
SAMPLE_RATE = 6279.8    # Hz
N_AUG       = 50        # variaciones sinteticas por captura real
OUTPUT_DIR  = "./edge_impulse_output"
```

## Tipo de modelo

Classifier:
Una vex integrado el pre processing en edge impulse con un output de 5 features, los datos son lo suficientemente separables entre sí.

**_¿Qué hace?_**

> El modelo detecta el fenómeno actual, y el MPU en Python decide si la secuencia de fenómenos recientes constituye una alerta compuesta. Eso es exactamente la separación MCU/MPU que nos hace diferentes.

```python
MCU (STM32U585)          MPU (QRB2210 Python)
─────────────────        ──────────────────────────────
Modelo A → clase         Buffer últimas N clasificaciones
Modelo B → clase    ───► Lógica de riesgo compuesto
Modelo C → clase         "sag_leve × 3 seguidos = alerta"
                         Activa relay + WhatsApp
```

## Model Features

#### Window Size: 200 ms -> ah doc con buffer de periscope.

> Trabajando con ondas de voltaje, con una freq. average de 60 Hz, una window size de 200 ms permite capturar exactamente 1 ciclo.

#### Window Stride: 200 ms -> sin overlap.

> Al usar un relay, añadir un overlap es risky. Clasificamos cada 200 ms.

### Frequency:

> 1000 Hz porque es la freq de muestreo óptima para el stmu. Para detectar una señal de 60 Hz necesitas mínimo 120 Hz de muestreo. A 1000 Hz hay un margen de 8x, suficiente para capturar hasta el 8° armónico (480 Hz), que cubre toda la distorsión relevante de cargas no lineales en redes mexicanas.

> El STM32U585 ejecutando inferencia cada 200ms a 1000 Hz tiene un presupuesto de 1ms por sample. Con el timer interrupt a 1ms exacto, el ADC lee, almacena y avanza sin bloquear la inferencia del modelo.

### Normalization:

Las 5 features de Tecovolt Pre ya tienen significado físico en sus unidades reales (mV, Hz).

Si normalizamos, el modelo **pierde** la referencia absoluta de RMS que es crítica para distinguir sag/swell/outage —un outage a 2mV RMS y un normal a 117mV RMS son mUY diferentes en escala real, pero normalizados se acercan.

### First Training

#### Unoptimized: float32

     En optimized no hay buenos results, pero no nos preocupa porque el Qualcomm AI hub hace la quantification.
     Esa data en INT8 va a la STM32.

Accuracy: 92.6%

### Ideas de Improvement:

     sag_leve (13.6% confusion) y swell→normal (7.4%)

1.  Subir training cycles de 50 a 100.

2.  Si no jala -> más datos en normal y sag_leve.

        sus datos de Rms se traslapan en bordes.
        CORRER again tecovolt_synth.py con --n 400

3.  Añadir un Flatten

### Second Training

Accuracy: 94.5%

### Ideas de Improvement:

1. Mejorar el dataset con datos de voltaje raw real desde el Arduino Q.

### Main functions:

#### compute_features

> Obtiene: rms, peak, crest, ptp.

#### augment

> genera n variaciones sinteticas de una senal real. Ruido basado en el perfil de ruido medido del instrumento Picoscope.

#### process_folder

> Procesa todos los CSVs en input_dir con el label dado. Devuelve (raw_rows, feature_rows)

## Output

Un master csv con labels para classifier clásico.

## Temp Anomaly Detection

> Usa datos del BMP280 para clasificar la integrdad del tablero energético. Clasifica riesgo: bajo, alto, medio.

## Tipo de modelo

Flatten:
Es ideal, ya que, aunque recibamos datos a 1 Hz, la temperatura cambia lento. No es necesario sobrecargar el flujo de recibimiento de la Arduino Q.

_Usa temperatura y humedad del BMP280 a 1 Hz para clasificar el riesgo térmico del tablero en tres niveles. Elegimos Flatten como bloque de procesamiento porque el calor es un fenómeno lento, así que no necesita análisis de frecuencia. Lo entrenamos con datos sintéticos generados a partir de rangos documentados para tableros residenciales mexicanos."_

## Data Acquisition ACS 712

Sensor de corriente - 30 A
Demasiada potencia para poder notar una fluctuación grande.

Observando en un picoscope + osciloscopio, la variación era de +- 0.200 V.

### Keys para que esto funcione

1. Circuito en serie (obviamente), con el sensor ANTES de la corriente a medir.

2. Consumo mayor a 100 Watts

3. Generar flicker con dremmel.

### Data Acquisition TM101B

Sensor de voltaje.
Debe ajustarse con el POT hasta que la señal senoidal esté centrada y no achatada.
