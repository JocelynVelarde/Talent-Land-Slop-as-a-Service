#include <Arduino.h>
#include "current_sensor.h"

static int _pin;
static float _offset = 0.0;
static const float VREF = 3.3;
static const int ADC_MAX = 1023;
static const float SENSITIVITY = 0.066;
static const int SAMPLES = 500;

void current_init(int pin) {
  _pin = pin;

  float sum = 0.0;
  for (int i = 0; i < 1000; i++) {
    int raw = analogRead(_pin);
    sum += (raw * VREF) / ADC_MAX;
    delayMicroseconds(200);
  }
  _offset = sum / 1000.0;
}

float current_read_rms() {
  float sumSq = 0.0;
  for (int i = 0; i < SAMPLES; i++) {
    int raw = analogRead(_pin);
    float v = (raw * VREF) / ADC_MAX;
    float centered = v - _offset;
    sumSq += centered * centered;
    delayMicroseconds(200);
  }
  float rms = sqrt(sumSq / SAMPLES);
  if (rms < 0.02) return 0.0;
  return rms / SENSITIVITY;
}