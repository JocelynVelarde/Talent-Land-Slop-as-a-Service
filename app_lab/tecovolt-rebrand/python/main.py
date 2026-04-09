import time
import os
import requests
from arduino.app_utils import *
from arduino.app_bricks.web_ui import WebUI
from edge_impulse_linux.runner import ImpulseRunner

# ─── Configuración de Alertas ──────────────────────────────────────
WHATSAPP_URL = "http://172.20.28.27:3000/alert"
DESTINATION_NUMBER = "5218110517608@c.us"

# ─── Edge Impulse Setup ────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_CURRENT_PATH = os.path.join(BASE_DIR, "models/model_no_acc_.eim")
MODEL_VOLTAGE_PATH = os.path.join(BASE_DIR, "models/volt_model.eim") # Asegúrate de que el nombre coincida

# Inicialización de Corriente
runner_current = ImpulseRunner(MODEL_CURRENT_PATH)
info_current = runner_current.init()
n_samples_curr = info_current["model_parameters"]["input_features_count"]

# Inicialización de Voltaje
runner_voltage = ImpulseRunner(MODEL_VOLTAGE_PATH)
info_voltage = runner_voltage.init()
n_samples_volt = info_voltage["model_parameters"]["input_features_count"]

print(f"Modelos cargados correctamente")

# ─── State ──────────────────────────────────────────────────────────
DEBOUNCE_COUNT = 3

# Estado Corriente (Demanda)
current_state = "---"
pending_state = None
pending_count = 0
last_confidence = 0.0

# Estado Voltaje (Anomalías)
current_v_anomaly = "normal"
pending_v_state = None
pending_v_count = 0
last_v_confidence = 0.0

# Variables de sensor
last_voltage = 0.0
last_current = 0.0
last_temp = 0.0
relay_latched = False

# ─── Funciones de Apoyo ─────────────────────────────────────────────
def send_whatsapp_alert(type_alert, state, value, unit):
    try:
        payload = {
            "number": DESTINATION_NUMBER,
            "message": f"⚠️ ALERTA GRIDGUARD: {type_alert}\nEstado: {state.upper()}\nValor: {value:.2f}{unit}\nHora: {time.strftime('%H:%M:%S')}"
        }
        requests.post(WHATSAPP_URL, json=payload, timeout=2)
    except Exception as e:
        print(f"❌ Error WhatsApp: {e}")

# Lecturas de Bridge (Asegúrate de que 'getRawVoltage' exista en tu C++)
def read_raw_rms(): return float(Bridge.call("getRawRMS") or 0.0)
def read_raw_voltage(): return float(Bridge.call("getRawVoltage") or 0.0) 
def read_amps(): return float(Bridge.call("getAmps") or 0.0)
def read_voltage(): return float(Bridge.call("getVoltage") or 0.0)
def read_temperature(): return float(Bridge.call("getTemperature") or 0.0)

# ─── WebUI ──────────────────────────────────────────────────────────
ui = WebUI()

def on_get_status():
    return {
        "voltage": last_voltage,
        "current": last_current,
        "temperature": last_temp,
        "demand_state": current_state,
        "demand_confidence": last_confidence,
        "voltage_anomaly": current_v_anomaly,
        "voltage_anomaly_confidence": last_v_confidence,
        "temp_risk": "bajo",
        "temp_risk_confidence": 0.0,
        "relay_latched": relay_latched,
    }

ui.expose_api("GET", "/status", on_get_status)

def on_reset_relay():
    global relay_latched
    relay_latched = False
    Bridge.call("setRelay", False)
    print("🟢 RELAY RESET — manual")
    return {"status": "ok"}

ui.expose_api("POST", "/reset_relay", on_reset_relay)

# ─── Main Loop ──────────────────────────────────────────────────────
def loop():
    global current_state, pending_state, pending_count, last_confidence
    global current_v_anomaly, pending_v_state, pending_v_count, last_v_confidence
    global last_voltage, last_current, last_temp, relay_latched

    # 1. Actualizar sensores básicos
    last_voltage = read_voltage()
    last_current = read_amps()
    last_temp = read_temperature()

    # 2. Recolectar muestras para ambos modelos
    samples_curr = []
    samples_volt = []
    
    # Asumimos que n_samples es 200 para ambos según tu metadata
    # 2. Recolectar muestras de forma independiente
    samples_curr = []
    for _ in range(n_samples_curr):
        samples_curr.append(read_raw_rms())

    samples_volt = []
    for _ in range(n_samples_volt):
        samples_volt.append(read_raw_voltage())

    # 3. Clasificación de Corriente (Demanda)
    res_curr = runner_current.classify(samples_curr)
    class_curr = res_curr["result"]["classification"]
    best_curr_label = max(class_curr, key=class_curr.get)
    last_confidence = class_curr[best_curr_label]

    # 4. Clasificación de Voltaje (Calidad de Energía)
    res_volt = runner_voltage.classify(samples_volt)
    class_volt = res_volt["result"]["classification"]
    best_volt_label = max(class_volt, key=class_volt.get)
    last_v_confidence = class_volt[best_volt_label]

    # --- Debounce Corriente ---
    if best_curr_label == pending_state:
        pending_count += 1
    else:
        pending_state = best_curr_label
        pending_count = 1

    if pending_count >= DEBOUNCE_COUNT and best_curr_label != current_state:
        current_state = best_curr_label
        if current_state in ["media", "alta"]:
            send_whatsapp_alert("DEMANDA", current_state, last_current, "A")
        
        if current_state == "alta" and not relay_latched:
            relay_latched = True
            Bridge.call("setRelay", True)
            print(f"🔴 CORTE POR DEMANDA: {current_state.upper()}")

    # --- Debounce Voltaje ---
    if best_volt_label == pending_v_state:
        pending_v_count += 1
    else:
        pending_v_state = best_volt_label
        pending_v_count = 1

    if pending_v_count >= DEBOUNCE_COUNT and best_volt_label != current_v_anomaly:
        current_v_anomaly = best_volt_label
        print(f"⚡ CALIDAD VOLTAJE: {current_v_anomaly.upper()} ({last_v_confidence:.0%})")
        
        # Alerta si hay anomalías serias (flicker, outage, sag, swell)
        if current_v_anomaly != "normal":
            send_whatsapp_alert("CALIDAD VOLTAJE", current_v_anomaly, last_voltage, "V")
            
            # Opcional: Corte preventivo por voltaje severo
            if current_v_anomaly in ["outage", "sag_severo", "swell"] and not relay_latched:
                relay_latched = True
                Bridge.call("setRelay", True)
                print(f"🔴 CORTE PREVENTIVO: {current_v_anomaly.upper()}")

    time.sleep(0.1) # Reducido un poco para compensar la carga de dos modelos

if __name__ == "__main__":
    print("GridGuard: Monitoreo Dual (Corriente + Voltaje) iniciado")
    App.run(user_loop=loop)
