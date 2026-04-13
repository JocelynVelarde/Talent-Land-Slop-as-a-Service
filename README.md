# ⚡ Tecovolt

> Edge AI-powered electrical grid monitoring system for Mexican residential infrastructure, built on the Arduino UNO Q dual-processor platform.

**Qualcomm Sustainable Power Cities** · Talent Land 2026

---

<img width="425" height="410" alt="image" src="https://github.com/user-attachments/assets/903da4e4-8b4b-450b-849b-f280763b103b" />


## The Problem

Mexico's residential electrical infrastructure suffers from chronic power quality issues — voltage sags, swells, outages, and demand overloads that damage appliances, cause fires in electrical panels, and go undetected until failure. Traditional monitoring solutions are expensive, cloud-dependent, and inaccessible to the 35M+ households that need them most.

## Our Solution

Tecovolt is an edge-first power monitoring system that runs three AI models simultaneously on a single Arduino UNO Q board, classifying voltage anomalies, energy demand levels, and thermal risk in real-time — with no cloud dependency, sub-second response times, and automated protective relay actuation.

```
MCU (STM32U585 · Zephyr RTOS)        MPU (QRB2210 · Debian Linux)
────────────────────────────          ─────────────────────────────
3 sensor threads (voltage,            3 Edge Impulse models (INT8)
current, temperature) running         Compound risk logic engine
concurrently via k_threads            WhatsApp alerts + Web dashboard
ADC sampling @ 10kHz                  Relay actuation decisions
         ↕ Arduino RouterBridge RPC ↕
```

## Architecture
<img width="2545" height="281" alt="Captura de pantalla 2026-04-09 021258" src="https://github.com/user-attachments/assets/033be4da-f630-4fb1-973a-f24cef2d9dc0" />



## Edge AI Models

| Model | Input | Classes | Window | Accuracy | Block |
|-------|-------|---------|--------|----------|-------|
| Voltage Anomaly | ZMPT101B raw waveform | normal, sag_leve, sag_severo, swell, outage, flicker | 200ms @ 1kHz | 94.5% | Custom DSP (5 features: RMS, PtP, Crest, Ripple, Freq) |
| Energy Demand | ACS712 rawRMS | baja, media, alta | 5000ms @ 2Hz | 87.5% | Flatten (3 features: RMS, avg, stddev) |
| Thermal Risk | BMP180 temp+pressure | bajo, medio, alto | 10s @ 1Hz | 89.6% | Flatten (avg temp, avg humidity) |

All models are trained in Edge Impulse Studio, quantized to INT8, and deployed as `.eim` files to the QRB2210.

## Hardware

| Component | Role | Interface |
|-----------|------|-----------|
| Arduino UNO Q (4GB) | Dual-processor platform | — |
| ZMPT101B | AC voltage sensing (0-250V) | A1 + voltage divider (10k/20k) |
| ACS712-30A | AC current sensing (0-30A) | A0 + voltage divider (10k/20k) |
| BMP180 | Temperature & pressure | I2C (D20 SDA, D21 SCL) |
| 4-channel relay module | Circuit protection actuation | D2, D3, D4, D5 |
| 7" display | Dashboard visualization | USB-C DisplayPort Alt-Mode |

**Important:** The UNO Q's ADC is 3.3V max (12-bit, 0-4095). Both the ZMPT101B and ACS712 run on 5V and require voltage dividers (10kΩ + 20kΩ) to scale their outputs to the safe 0-3.3V range.

## Project Structure

```
├── app_lab/tecovolt-rebrand/     # Arduino App Lab project
│   ├── assets/                   # WebUI dashboard (HTML/CSS/JS)
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   ├── python/                   # MPU-side Python application
│   │   ├── main.py               # Model inference + Bridge + WebUI API
│   │   ├── models/               # Edge Impulse .eim model files
│   │   └── requirements.txt
│   ├── sketch/                   # MCU-side C++ (Zephyr RTOS)
│   │   ├── sketch.ino            # Main: Bridge providers + relay
│   │   ├── current_sensor.cpp/h  # ACS712 RTOS thread
│   │   ├── voltage_sensor.cpp/h  # ZMPT101B RTOS thread
│   │   └── bmp_sensor.cpp/h      # BMP180 RTOS thread
│   └── app.yaml
├── data_generation/              # Synthetic + real data pipelines
│   ├── voltage/                  # Voltage anomaly dataset tools
│   │   ├── tecovolt_synth.py     # Synthetic waveform generator
│   │   └── tecovolt_pipeline.py  # Feature extraction + augmentation
│   ├── demmand/                  # Energy demand dataset tools
│   │   └── tecovolt_demand_synth.py
│   └── temp/                     # Thermal risk dataset tools
│       └── tecovolt_temp_synth.py
├── ei_custom_blocks/             # Edge Impulse custom DSP blocks
│   ├── tecovolt_block/           # Voltage quality features (6 features)
│   └── tecotemp_block/           # Thermal averaging block
├── datacapture_amp.py            # Serial DAQ for real ACS712 data
├── docs/                         # Hugo + Docsy documentation site
└── doc_synth.md                  # Technical decisions & model notes
```

## Quick Start

### Prerequisites

- Arduino UNO Q (4GB variant recommended)
- Arduino App Lab installed on PC or running in SBC mode
- Edge Impulse account (for model training)
- Sensors wired as described in the Hardware section

### Deploy

1. Open Arduino App Lab and connect to your UNO Q
2. Create a new app or clone this repo's `app_lab/tecovolt-rebrand/` folder
3. Place `.eim` model files in `python/models/`
4. Add the WebUI Brick and the required Sketch Libraries (Arduino_RouterBridge, Adafruit BMP085 Unified)
5. Press **Run** — App Lab compiles the sketch, deploys Python, and starts the WebUI
6. Access the dashboard at `http://<board-ip>:7000`

### Sensor Calibration

**Voltage (ZMPT101B):**
1. Adjust the potentiometer for gain (not offset — offset is software-calibrated)
2. Verify on oscilloscope: clean sine wave within 0-3.3V at A1
3. Run the app, note the `Raw RMS` value, measure actual voltage with multimeter
4. Calculate: `calibrationFactor = 0.45 * (multimeter_reading / serial_reading)`

**Current (ACS712-30A):**
1. Boot with no load for auto-offset calibration
2. Apply known load, compare with clamp meter
3. Adjust `MV_PER_AMP` in `current_sensor.cpp`

### Generate Training Data

```bash
# Voltage anomaly data (synthetic)
python data_generation/voltage/tecovolt_synth.py --n 200

# Energy demand data (synthetic)
python data_generation/demmand/tecovolt_demand_synth.py --n 200

# Thermal risk data (synthetic)
python data_generation/temp/tecovolt_temp_synth.py

# Real current data via serial capture
python datacapture_amp.py --port /dev/ttyACM0 --label baja
python datacapture_amp.py --port /dev/ttyACM0 --label media
python datacapture_amp.py --port /dev/ttyACM0 --label alta
python datacapture_amp.py --combine
```

## Key Design Decisions

**Why Zephyr RTOS threads instead of blocking `delay()`?**
Each sensor runs in its own `k_thread` with `k_usleep`/`k_msleep`, allowing concurrent ADC sampling without blocking. Bridge callbacks return cached values instantly.

**Why software offset calibration?**
The ZMPT101B's potentiometer controls gain, not DC offset. The offset drifts with temperature. `calibrateOffset()` measures the true midpoint at boot with 1000+ samples.

**Why voltage dividers?**
The UNO Q's STM32U585 ADC pins are 3.3V max (absolute maximum 3.6V). Both sensors output signals centered around 2.5V (5V supply). The 10k+20k divider scales by 2/3, bringing the midpoint to ~1.67V and keeping peaks within safe range.

**Why debounce + latch for relay actuation?**
Debounce (3 consecutive classifications) prevents spurious relay triggers. Latching prevents oscillation — when the relay cuts load, current drops to zero, model sees "baja", relay turns off, load returns, cycle repeats. The latch holds until manual reset from the dashboard.

**Why no normalization on model features?**
The 5 voltage features have physical meaning in their real units (mV, Hz). Normalizing would collapse the absolute RMS difference between an outage (2mV) and normal operation (117mV), destroying the most discriminative signal.

## Documentation

Full documentation is available at [jocelynvelarde.github.io/Talent-Land-Slop-as-a-Service](https://jocelynvelarde.github.io/Talent-Land-Slop-as-a-Service/)

Built with Hugo + Docsy. Run locally:

```bash
cd docs && npm install && hugo server
```

## Team — Slop as a Service (SAAS)

| | Name | Campus |
|---|------|--------|
| 🧠 | Bini Vázquez | Signal Processing |
| ⚡ | Diego Pérez Rossi | Electronics |
| 🔧 | Jocelyn Velarde Barrón | Interfaces |
| 🤖 | Armando Mac Beath | Machine Learning |

## Pitch Deck

Talent Land's Final deck is available at [canva deck](https://canva.link/7u7g7evsr49j3x1)

## License

MIT
