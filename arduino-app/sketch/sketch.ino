#include <Arduino_RouterBridge.h>

#define ACS_PIN A0

const float VREF    = 3.3;
const int   ADC_MAX = 4095;
const int   SAMPLES = 1000;

// ACS712-30A: 66mV/A at 5V
// After voltage divider (same ratio as ZMPT), adjust this value
float mVperAmp = 10.52;

float rawRMS    = 0.0;
float vOffset   = 0.0;
float currentRMS = 0.0;

void calibrateOffset() {
  float sum = 0.0;
  for (int i = 0; i < 1000; i++) {
    sum += analogRead(ACS_PIN);
    delayMicroseconds(200);
  }
  vOffset = sum / 1000.0;
  Monitor.print("ACS712 offset (raw): ");
  Monitor.println(vOffset, 2);
}

float readCurrentRMS() {
  long sumSq = 0;

  for (int i = 0; i < SAMPLES; i++) {
    int raw = analogRead(ACS_PIN);
    int centered = raw - (int)vOffset;
    sumSq += (long)centered * centered;
    delayMicroseconds(100);
  }

  float mean = sumSq / (float)SAMPLES;
  float rms = sqrt(mean);

  if (rms < 3.0) {
    rawRMS = 0.0;
    return 0.0;
  }

  rawRMS = rms;
  float voltageRMS = (rms * VREF) / ADC_MAX;
  float amps = (voltageRMS * 1000.0) / mVperAmp;
  currentRMS = amps;
  return amps;
}

float getCurrent() {
  return readCurrentRMS();
}

float getRawRMS() {
  return rawRMS;
}

void setup() {
  Bridge.begin();
  Monitor.begin();

  Monitor.println("Calibrating ACS712 offset (no load)...");
  calibrateOffset();

  Bridge.provide("getCurrent", getCurrent);
  Bridge.provide("getRawRMS", getRawRMS);

  Monitor.println("ACS712 ready.");
}

void loop() {
  float a = readCurrentRMS();
  Monitor.print("AC Current RMS: ");
  Monitor.print(a, 3);
  Monitor.print(" A | Raw RMS: ");
  Monitor.println(rawRMS, 2);

  delay(2000);
}