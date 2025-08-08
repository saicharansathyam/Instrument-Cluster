#include <SPI.h>
#include <mcp_can.h>

// -------------------- CAN 설정 --------------------
const int SPI_CS_PIN = 10;
MCP_CAN CAN(SPI_CS_PIN);

// CAN Message IDs
#define SPEED_MSG_ID    0x100
#define GEAR_MSG_ID     0x102

// -------------------- 속도 센서 설정 --------------------
#define SPEED_SENSOR_PIN 3
#define WHEEL_CIRCUMFERENCE_CM 20.0
#define PULSES_PER_REVOLUTION 20

// -------------------- 속도 계산 변수 --------------------
volatile unsigned long pulse_count = 0;
unsigned long last_speed_calculation = 0;
unsigned long speed_calculation_interval = 1000; // 1초마다 계산
float current_speed_cms = 0.0;

char current_gear = 'P';

// -------------------- ISR --------------------
void speedPulse() {
  pulse_count++;
}

// -------------------- 속도 계산(cm/s) --------------------
float calculateSpeed() {
  unsigned long current_time = millis();
  unsigned long time_elapsed = current_time - last_speed_calculation;

  if (time_elapsed >= speed_calculation_interval) {
    noInterrupts();
    unsigned long pulses = pulse_count;
    pulse_count = 0;
    interrupts();

    float distance_cm = (float(pulses) / PULSES_PER_REVOLUTION) * WHEEL_CIRCUMFERENCE_CM;
    float time_seconds = time_elapsed / 1000.0;

    if (time_seconds > 0.0f) {
      current_speed_cms = distance_cm / time_seconds;
    } else {
      current_speed_cms = 0.0f;
    }

    last_speed_calculation = current_time;

    Serial.print("Pulses: "); Serial.print(pulses);
    Serial.print(", Distance: "); Serial.print(distance_cm, 1);
    Serial.print(" cm, Speed: "); Serial.print(current_speed_cms, 1);
    Serial.println(" cm/s");

    Serial.print("Current pin ");
    Serial.print(SPEED_SENSOR_PIN);
    Serial.print(" state: ");
    Serial.println(digitalRead(SPEED_SENSOR_PIN));
  }

  return current_speed_cms;
}

// -------------------- 속도 기반 자동 기어 --------------------
void updateGearBasedOnSpeed() {
  // New gear thresholds (max speed: 172.7 cm/s)
  if (current_speed_cms < 5.0) {
    current_gear = 'P';
  } else if (current_speed_cms < 60.0) {
    current_gear = '1';
  } else if (current_speed_cms < 120.0) {
    current_gear = '2';
  } else if (current_speed_cms < 172.7) {
    current_gear = '3';
  } else {
    current_gear = '4';
  }
}

// -------------------- CAN 송신: 속도(cm/s × 10) --------------------
void sendSpeedData(float speed_cms) {
  int speed_int = (int)(speed_cms * 10.0f);

  byte data[8] = {0};
  data[0] = highByte(speed_int);
  data[1] = lowByte(speed_int);

  byte result = CAN.sendMsgBuf(SPEED_MSG_ID, 0, 8, data);

  Serial.print("Real Speed: ");
  Serial.print(speed_cms, 1);
  Serial.print(" cm/s - ");
  Serial.println(result == CAN_OK ? "✓" : "✗");
}

// -------------------- CAN 송신: 기어 --------------------
void sendGearData(char gear) {
  byte data[8] = {0};
  data[0] = (byte)gear;

  byte result = CAN.sendMsgBuf(GEAR_MSG_ID, 0, 8, data);

  Serial.print("Auto Gear: ");
  Serial.print(gear);
  Serial.print(" - ");
  Serial.println(result == CAN_OK ? "✓" : "✗");
}

// -------------------- 초기화 --------------------
void setup() {
  Serial.begin(115200);
  Serial.println("=== Real-Time Speed Sensor (Pin 3) CAN Sender ===");

  if (CAN.begin(MCP_ANY, CAN_500KBPS, MCP_16MHZ) == CAN_OK) {
    Serial.println("✓ CAN Ready");
    CAN.setMode(MCP_NORMAL);
  } else {
    Serial.println("✗ CAN Failed");
    while (1);
  }

  pinMode(SPEED_SENSOR_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(SPEED_SENSOR_PIN), speedPulse, FALLING);

  Serial.print("✓ Speed sensor initialized on pin ");
  Serial.println(SPEED_SENSOR_PIN);
  Serial.print("Wheel circumference: ");
  Serial.print(WHEEL_CIRCUMFERENCE_CM);
  Serial.println(" cm");
  Serial.println("Output: Speed in cm/s");

  Serial.println("Testing interrupt pin...");
  for (int i = 0; i < 5; i++) {
    Serial.print("Pin state: ");
    Serial.println(digitalRead(SPEED_SENSOR_PIN));
    delay(500);
  }
}

// -------------------- 메인 루프 --------------------
void loop() {
  calculateSpeed();
  updateGearBasedOnSpeed();

  sendSpeedData(current_speed_cms);
  delay(50);

  sendGearData(current_gear);

  Serial.println("---");
  delay(500);
}
cd 
