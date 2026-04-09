#include <Arduino.h>
#include <zephyr/kernel.h>
#include "voltage_sensor.h"

static int _pin;
static float _vOffset           = 0.0;
static float _voltageRMS        = 0.0;
static float _calibrationFactor = 1.5628;
static float _lastRawVoltage = 0.0; // Nueva variable global estática

static const float VREF      = 3.3;
static const int   ADC_MAX   = 4095;
static const int   N_SAMPLES = 200;
static const int   SAMPLE_US = 1000;

K_MUTEX_DEFINE(voltage_mutex);

static void calibrate_offset() {
  float sum = 0.0;
  for (int i = 0; i < 2000; i++) {
    sum += (analogRead(_pin) * VREF) / ADC_MAX;
    k_usleep(200);
  }
  _vOffset = sum / 2000.0;
}

static void voltage_thread_fn(void *, void *, void *) {
  while (1) {
    float sumSq = 0.0;

    for (int i = 0; i < N_SAMPLES; i++) {
      float raw = (analogRead(_pin) * VREF) / (float)ADC_MAX;
      float centered = raw - _vOffset;
      
      // Guardamos la muestra centrada para el Bridge
      k_mutex_lock(&voltage_mutex, K_FOREVER);
      _lastRawVoltage = centered; 
      k_mutex_unlock(&voltage_mutex);

      sumSq += centered * centered;
      k_usleep(SAMPLE_US);
    }

    float rms = sqrt(sumSq / N_SAMPLES);
    float volts = 0.0;

    if (rms > 0.01) {
      volts = rms * _calibrationFactor;
    }

    k_mutex_lock(&voltage_mutex, K_FOREVER);
    _voltageRMS = volts;
    k_mutex_unlock(&voltage_mutex);

    k_msleep(500);
  }
}

K_THREAD_STACK_DEFINE(voltage_stack, 2048);
static struct k_thread voltage_thread;

void voltage_init(int pin) {
  _pin = pin;
  calibrate_offset();

  k_thread_create(&voltage_thread, voltage_stack,
                  K_THREAD_STACK_SIZEOF(voltage_stack),
                  voltage_thread_fn, NULL, NULL, NULL,
                  5, 0, K_NO_WAIT);
}

float voltage_get_rms() {
  k_mutex_lock(&voltage_mutex, K_FOREVER);
  float v = _voltageRMS;
  k_mutex_unlock(&voltage_mutex);
  return v;
}

float voltage_get_raw() {
  k_mutex_lock(&voltage_mutex, K_FOREVER);
  float v = _lastRawVoltage;
  k_mutex_unlock(&voltage_mutex);
  return v;
}
