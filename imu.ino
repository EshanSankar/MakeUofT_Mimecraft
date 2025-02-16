#include <Wire.h>

const int MPU_ADDR = 0x68;  
int iter = 0;
float rollOffset, pitchOffset;

float anglePitch = 0.0;
float angleRoll  = 0.0;
float angleYaw   = 0.0;

// For time delta calculation
unsigned long lastTime = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin();

  // Wake up the MPU6050 (write 0 to the power management register)
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);
  Wire.endTransmission(true);
  
  delay(100);
  lastTime = millis();
  iter = 0;
}

void loop() {
  int16_t rawAccX, rawAccY, rawAccZ;
  int16_t rawGyroX, rawGyroY, rawGyroZ;
  
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 14, true);
  
  // Read accelerometer values
  rawAccX = Wire.read() << 8 | Wire.read();
  rawAccY = Wire.read() << 8 | Wire.read();
  rawAccZ = Wire.read() << 8 | Wire.read();
  
  // Skip temperature readings
  Wire.read(); Wire.read();
  
  // Read gyroscope values
  rawGyroX = Wire.read() << 8 | Wire.read();
  rawGyroY = Wire.read() << 8 | Wire.read();
  rawGyroZ = Wire.read() << 8 | Wire.read();

  // Convert accelerometer readings
  float aX = rawAccX / 16384.0;
  float aY = rawAccY / 16384.0;
  float aZ = rawAccZ / 16384.0;

  Serial.println(aX);
  Serial.println(aY);
  Serial.println(aZ);
  
  // Convert gyroscope readings to deg/s
  float gX = rawGyroX / 131.0;
  float gY = rawGyroY / 131.0;
  float gZ = rawGyroZ / 131.0;
  
  // Calculate elapsed time
  unsigned long currentTime = millis();
  float dt = (currentTime - lastTime) / 1000;
  lastTime = currentTime;
  
  // Calculate pitch and roll from the accelerometer 
  float accRoll = atan2(aY, aZ) * 180.0 / PI;

  float accPitch = atan2(-aX, sqrt(aY * aY + aZ * aZ)) * 180.0 / PI;
  
  const float alpha = 0.98;
  
  // Integrate the gyroscope data
  

  angleRoll  = alpha * (angleRoll + gX * dt) + (1.0 - alpha) * accRoll;
  anglePitch = alpha * (anglePitch + gY * dt) + (1.0 - alpha) * accPitch;

  if (iter == 0) {
    rollOffset = angleRoll;
    pitchOffset = anglePitch;
    iter = 1;
  }
  angleRoll -= rollOffset;
  anglePitch -= pitchOffset;

  // Send a packet with a header (0xAA, 0x55) before the floats
  byte header[2] = {0xAA, 0x55};
  Serial.write(header, sizeof(header));
  Serial.write((byte*)&angleRoll, sizeof(angleRoll));
  Serial.write((byte*)&anglePitch, sizeof(anglePitch));

  
  delay(10);  // Small delay for stability
}