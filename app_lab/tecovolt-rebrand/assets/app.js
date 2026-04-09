const POLL_INTERVAL = 1000;
const MAX_LOG_LINES = 50;
let lastState = null;

const els = {
  connectionDot:      document.getElementById("connectionDot"),
  connectionText:     document.getElementById("connectionText"),
  statusCard:         document.getElementById("statusCard"),
  statusIcon:         document.getElementById("statusIcon"),
  statusName:         document.getElementById("statusName"),
  statusConfidence:   document.getElementById("statusConfidence"),
  voltageValue:       document.getElementById("voltageValue"),
  voltageBar:         document.getElementById("voltageBar"),
  currentValue:       document.getElementById("currentValue"),
  currentBar:         document.getElementById("currentBar"),
  tempValue:          document.getElementById("tempValue"),
  tempBar:            document.getElementById("tempBar"),
  voltageAnomaly:     document.getElementById("voltageAnomaly"),
  voltageAnomalyConf: document.getElementById("voltageAnomalyConf"),
  tempRisk:           document.getElementById("tempRisk"),
  tempRiskConf:       document.getElementById("tempRiskConf"),
  terminalBody:       document.getElementById("terminalBody"),
};

const STATE_ICONS = { alta: "🔴", media: "🟡", baja: "🟢" };

function clamp(v, min, max) { return Math.min(Math.max(v, min), max); }

function timeNow() {
  return new Date().toLocaleTimeString("es-MX", { hour12: false });
}

function addLog(msg, cls) {
  const line = document.createElement("div");
  line.className = "log-line" + (cls ? " " + cls : "");
  line.innerHTML = '<span class="log-time">' + timeNow() + "</span> " + msg;
  els.terminalBody.appendChild(line);
  while (els.terminalBody.children.length > MAX_LOG_LINES)
    els.terminalBody.removeChild(els.terminalBody.firstChild);
  els.terminalBody.scrollTop = els.terminalBody.scrollHeight;
}

function clearLog() {
  els.terminalBody.innerHTML = "";
  addLog("Log limpiado");
}
window.clearLog = clearLog;

function updateUI(data) {
  els.connectionDot.className = "status-dot connected";
  els.connectionText.textContent = "Conectado";

  var voltage = data.voltage || 0;
  var current = data.current || 0;
  var temp    = data.temperature || 0;
  var state   = data.demand_state || "---";
  var conf    = data.demand_confidence || 0;

  els.voltageValue.textContent = voltage.toFixed(1);
  els.voltageBar.style.width   = clamp(voltage / 140 * 100, 0, 100) + "%";
  els.currentValue.textContent = current.toFixed(2);
  els.currentBar.style.width   = clamp(current / 30 * 100, 0, 100) + "%";
  els.tempValue.textContent    = temp.toFixed(1);
  els.tempBar.style.width      = clamp(temp / 80 * 100, 0, 100) + "%";

  els.statusIcon.textContent       = STATE_ICONS[state] || "⚪";
  els.statusName.textContent       = state.toUpperCase();
  els.statusConfidence.textContent = (conf * 100).toFixed(0) + "% confianza";

  els.statusCard.className = "card card-status";
  if (state === "baja" || state === "media" || state === "alta") {
    els.statusCard.classList.add(state);
  }

  // Voltage anomaly model
  var vAnomaly     = data.voltage_anomaly || "normal";
  var vAnomalyConf = data.voltage_anomaly_confidence || 0;
  els.voltageAnomaly.textContent     = vAnomaly;
  els.voltageAnomaly.className       = "model-result " + vAnomaly;
  els.voltageAnomalyConf.textContent = (vAnomalyConf * 100).toFixed(0) + "%";

  // Temp risk model
  var tRisk     = data.temp_risk || "bajo";
  var tRiskConf = data.temp_risk_confidence || 0;
  els.tempRisk.textContent     = tRisk;
  els.tempRisk.className       = "model-result " + tRisk;
  els.tempRiskConf.textContent = (tRiskConf * 100).toFixed(0) + "%";

  // Log state changes
  if (state !== lastState && state !== "---") {
    var icon = STATE_ICONS[state] || "⚪";
    addLog(
      icon + " Demanda: <strong>" + state.toUpperCase() + "</strong> (" +
      (conf * 100).toFixed(0) + "%) " + current.toFixed(2) + "A",
      state
    );
    lastState = state;
  }

  // Log anomalies
  if (vAnomaly !== "normal") {
    addLog("⚠ Voltaje: " + vAnomaly + " (" + (vAnomalyConf * 100).toFixed(0) + "%)", "warning");
  }
  if (tRisk === "alto") {
    addLog("🔥 Riesgo térmico ALTO (" + (tRiskConf * 100).toFixed(0) + "%)", "error");
  }

var relayLatched = data.relay_latched || false;
  var relayStatus = document.getElementById("relayStatus");
  if (relayStatus) {
    relayStatus.textContent = relayLatched ? "LATCHED" : "OFF";
    relayStatus.className = "relay-status" + (relayLatched ? " active" : "");
  }
}

async function poll() {
  try {
    var res = await fetch("/status");
    if (!res.ok) throw new Error("HTTP " + res.status);
    var data = await res.json();
    updateUI(data);
  } catch (err) {
    els.connectionDot.className = "status-dot error";
    els.connectionText.textContent = "Sin conexión";
  }
}
async function resetRelay() {
  try {
    await fetch("/reset_relay", { method: "POST" });
    addLog("🟢 Relay reset manual", "baja");
  } catch (err) {
    addLog("⚠ Error reseteando relay", "error");
  }
}
window.resetRelay = resetRelay;
addLog("Tecovolt Dashboard iniciado");
addLog("Esperando conexión con MPU...");
setInterval(poll, POLL_INTERVAL);
poll();
