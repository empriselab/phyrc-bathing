#include <Wire.h>

#define FX29K_ADDRESS  0x28      // Your sensor's I2C address
#define FX29K_RANGE_LBS 100      // Adjust to match your sensor's range (lbs)
#define TARE_SAMPLE_COUNT 100    // Number of samples to average for tare
#define GRAVITY 9.8              // 9.8N per kg

uint16_t tare_value = 0;
bool is_tared = false;
bool record_mode = false;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  delay(100); // Allow sensor to stabilize

  Serial.println("Taring... Keep the sensor unloaded.");
  long sum = 0;
  for (int i = 0; i < TARE_SAMPLE_COUNT; i++) {
    sum += getRawFX29K();
    delay(5);
  }
  tare_value = sum / TARE_SAMPLE_COUNT;
  is_tared = true;

  Serial.print("Tare complete. Tare value: ");
  Serial.println(tare_value);
  Serial.println("Press 'r' to START recording force data.");
  Serial.println("Press 's' to STOP recording.");
}

void loop() {
  // Handle serial command
  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == 'r') {
      record_mode = true;
      Serial.println("Recording started...");
    } else if (cmd == 's') {
      record_mode = false;
      Serial.println("Recording stopped.");
    }
  }

  if (!is_tared || !record_mode) return;

  uint16_t raw = getRawFX29K();

  int32_t net = (int32_t)raw - (int32_t)tare_value;
  float pounds = (net * FX29K_RANGE_LBS) / 14000.0;
  float kilograms = pounds * 0.453592;
  float force_N = kilograms * GRAVITY;

  // Output only force value (in Newtons) while recording
  Serial.println(force_N, 5);

  delay(10); 
}

uint16_t getRawFX29K() {
  Wire.beginTransmission(FX29K_ADDRESS);
  Wire.endTransmission();
  delay(10);

  Wire.requestFrom(FX29K_ADDRESS, 2);
  if (Wire.available() == 2) {
    uint8_t msb = Wire.read();
    uint8_t lsb = Wire.read();
    return ((msb << 8) | lsb) & 0x3FFF;
  } else {
    Serial.println("Sensor read failed");
    return 0;
  }
}
