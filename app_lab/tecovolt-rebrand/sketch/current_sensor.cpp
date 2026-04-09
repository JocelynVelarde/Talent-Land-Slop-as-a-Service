#include <Arduino.h>
#include <zephyr/kernel.h>
#include "current_sensor.h"

static int _pin;
static float _vOffset    = 0.0;
static float _currentRMS = 0.0;
static float _rawRMS     = 0.0;
static float _mVperAmp   = 4.44;

static const float VREF    = 3.3;
static const int   ADC_MAX = 4095;
static const int   SAMPLES = 1000;

K_MUTEX_DEFINE(current_mutex);

static void calibrate_offset() {
  float sum = 0.0;
  for (int i = 0; i < 1000; i++) {
    sum += analogRead(_pin);
    k_usleep(200);
  }
  _vOffset = sum / 1000.0;
}

static void current_thread_fn(void *, void *, void *) {
  while (1) {
    float rmsLocal = 0.0;
    long sumSq = 0;

    for (int i = 0; i < SAMPLES; i++) {
      int raw      = analogRead(_pin);
      int centered = raw - (int)_vOffset;
      sumSq += (long)centered * centered;
      k_usleep(100);
    }

    float mean = sumSq / (float)SAMPLES;
    float rms  = sqrt(mean);

    float amps = 0.0;
    if (rms >= 3.0) {
      float voltageRMS = (rms * VREF) / ADC_MAX;
      amps     = (voltageRMS * 1000.0) / _mVperAmp;
      rmsLocal = rms;
    }

    k_mutex_lock(&current_mutex, K_FOREVER);
    _currentRMS = amps;
    _rawRMS     = rmsLocal;
    k_mutex_unlock(&current_mutex);

    k_msleep(500);
  }
}

K_THREAD_STACK_DEFINE(current_stack, 2048);
static struct k_thread current_thread;

void current_init(int pin) {
  _pin = pin;
  calibrate_offset();

  k_thread_create(&current_thread, current_stack,
                  K_THREAD_STACK_SIZEOF(current_stack),
                  current_thread_fn, NULL, NULL, NULL,
                  5, 0, K_NO_WAIT);
}

float current_get_amps() {
  k_mutex_lock(&current_mutex, K_FOREVER);
  float a = _currentRMS;
  k_mutex_unlock(&current_mutex);
  return a;
}

float current_get_raw_rms() {
  k_mutex_lock(&current_mutex, K_FOREVER);
  float r = _rawRMS;
  k_mutex_unlock(&current_mutex);
  return r;
}
