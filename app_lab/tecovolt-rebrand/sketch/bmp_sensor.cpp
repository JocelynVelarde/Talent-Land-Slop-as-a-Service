#include <Arduino.h>
#include <Wire.h>
#include <zephyr/kernel.h>
#include <Adafruit_BMP085_U.h>
#include "bmp_sensor.h"

static Adafruit_BMP085_Unified _bmp = Adafruit_BMP085_Unified(10085);
static bool _ready       = false;
static float _temperature = 0.0;
static float _pressure    = 0.0;

K_MUTEX_DEFINE(bmp_mutex);

static void bmp_thread_fn(void *, void *, void *) {
  while (1) {
    if (_ready) {
      float t, p;
      _bmp.getTemperature(&t);
      _bmp.getPressure(&p);

      k_mutex_lock(&bmp_mutex, K_FOREVER);
      _temperature = t;
      _pressure = p / 100.0;
      k_mutex_unlock(&bmp_mutex);
    }
    k_msleep(1000);
  }
}

K_THREAD_STACK_DEFINE(bmp_stack, 2048);
static struct k_thread bmp_thread;

bool bmp_init() {
  _ready = _bmp.begin();

  if (_ready) {
    k_thread_create(&bmp_thread, bmp_stack,
                    K_THREAD_STACK_SIZEOF(bmp_stack),
                    bmp_thread_fn, NULL, NULL, NULL,
                    6, 0, K_NO_WAIT);
  }

  return _ready;
}

float bmp_get_temperature() {
  k_mutex_lock(&bmp_mutex, K_FOREVER);
  float t = _temperature;
  k_mutex_unlock(&bmp_mutex);
  return t;
}

float bmp_get_pressure() {
  k_mutex_lock(&bmp_mutex, K_FOREVER);
  float p = _pressure;
  k_mutex_unlock(&bmp_mutex);
  return p;
}
