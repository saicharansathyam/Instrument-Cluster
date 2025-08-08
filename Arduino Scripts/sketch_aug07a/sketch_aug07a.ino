#include <SPI.h>
#include <mcp_can.h>

// -------------------- CAN 설정 --------------------
const int SPI_CS_PIN = 10;
MCP_CAN CAN(SPI_CS_PIN);

// CAN Message IDs
#define SPEED_MSG_ID    0x100
#define BATTERY_MSG_ID  0x101
#define GEAR_MSG_ID     0x102

// -------------------- 속도 센서 설정 --------------------
// 인터럽트 가능한 핀 사용(Arduino UNO 기준: 2 or 3)
#define SPEED_SENSOR_PIN 3
#define WHEEL_CIRCUMFERENCE_CM 20.0   // 바퀴 둘레(cm)
#define PULSES_PER_REVOLUTION 20      // 엔코더 1회전 펄스 수

// -------------------- 속도 계산 변수 --------------------
volatile unsigned long pulse_count = 0;      // ISR에서 증가
unsigned long last_speed_calculation = 0;
unsigned long speed_calculation_interval = 1000; // 1초마다 계산
float current_speed_cms = 0.0;               // cm/s

// -------------------- 기타 차량 데이터 --------------------
static float battery_level = 95.0;           // %
char current_gear = 'P';

// -------------------- ISR --------------------
void speedPulse() {
  pulse_count++;
  // 디버그가 필요하면 아래 주석 해제
  // Serial.println("PULSE!");
}

// -------------------- 속도 계산(cm/s) --------------------
float calculateSpeed() {
  unsigned long current_time = millis();
  unsigned long time_elapsed = current_time - last_speed_calculation;

  if (time_elapsed >= speed_calculation_interval) {
    // 안전하게 펄스 카운트 읽기
    noInterrupts();
    unsigned long pulses = pulse_count;
    pulse_count = 0;
    interrupts();

    // 이동거리(cm) = (펄스수 / 회전당펄스) * 둘레(cm)
    float distance_cm = (float(pulses) / PULSES_PER_REVOLUTION) * WHEEL_CIRCUMFERENCE_CM;

    // 시간(s)
    float time_seconds = time_elapsed / 1000.0;

    // 속도(cm/s)
    if (time_seconds > 0.0f) {
      current_speed_cms = distance_cm / time_seconds;
    } else {
      current_speed_cms = 0.0f;
    }

    last_speed_calculation = current_time;

    // 디버그 출력
    Serial.print("Pulses: ");
    Serial.print(pulses);
    Serial.print(", Distance: ");
    Serial.print(distance_cm, 1);
    Serial.print(" cm, Speed: ");
    Serial.print(current_speed_cms, 1);
    Serial.println(" cm/s");

    // 핀 상태 확인(노이즈/배선점검용)
    Serial.print("Current pin ");
    Serial.print(SPEED_SENSOR_PIN);
    Serial.print(" state: ");
    Serial.println(digitalRead(SPEED_SENSOR_PIN));
  }

  return current_speed_cms;
}

// -------------------- 속도 기반 자동 기어 --------------------
void updateGearBasedOnSpeed() {
  // cm/s 기준 임계값 (m/s로는 0.1, 2.0, 5.0, 8.0)
  if (current_speed_cms < 10.0) {
    current_gear = 'P';
  } else if (current_speed_cms < 200.0) {
    current_gear = '1';
  } else if (current_speed_cms < 500.0) {
    current_gear = '2';
  } else if (current_speed_cms < 800.0) {
    current_gear = '3';
  } else {
    current_gear = '4';
  }
}

// -------------------- CAN 송신: 속도(cm/s × 10) --------------------
void sendSpeedData(float speed_cms) {
  // 소수점 1자리 해상도 유지: cm/s × 10 → 정수
  int speed_int = (int)(speed_cms * 10.0f);

  byte data[8] = {0};
  data[0] = highByte(speed_int);
  data[1] = lowByte(speed_int);
  // 나머지 바이트는 0으로 둠

  byte result = CAN.sendMsgBuf(SPEED_MSG_ID, 0, 8, data);

  Serial.print("Real Speed: ");
  Serial.print(speed_cms, 1);
  Serial.print(" cm/s - ");
  Serial.println(result == CAN_OK ? "✓" : "✗");
}

// -------------------- CAN 송신: 배터리(%) --------------------
void sendBatteryData(float battery_percent) {
  // 해상도 0.01%: % × 100 → 정수
  int battery_int = (int)(battery_percent * 100.0f);

  byte data[8] = {0};
  data[0] = highByte(battery_int);
  data[1] = lowByte(battery_int);

  byte result = CAN.sendMsgBuf(BATTERY_MSG_ID, 0, 8, data);

  Serial.print("Battery: ");
  Serial.print(battery_percent, 1);
  Serial.print("% - ");
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

  // CAN 초기화
  if (CAN.begin(MCP_ANY, MCP_500KBPS, MCP_16MHZ) == CAN_OK) {
    Serial.println("✓ CAN Ready");
    CAN.setMode(MCP_NORMAL);
  } else {
    Serial.println("✗ CAN Failed");
    while (1);
  }

  // 속도 센서 인터럽트 설정
  pinMode(SPEED_SENSOR_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(SPEED_SENSOR_PIN), speedPulse, FALLING);

  Serial.print("✓ Speed sensor initialized on pin ");
  Serial.println(SPEED_SENSOR_PIN);
  Serial.print("Wheel circumference: ");
  Serial.print(WHEEL_CIRCUMFERENCE_CM);
  Serial.println(" cm");
  Serial.println("Output: Speed in cm/s");

  // 인터럽트 핀 기본 상태 확인
  Serial.println("Testing interrupt pin...");
  for (int i = 0; i < 5; i++) {
    Serial.print("Pin state: ");
    Serial.println(digitalRead(SPEED_SENSOR_PIN));
    delay(500);
  }
}

// -------------------- 메인 루프 --------------------
void loop() {
  // 1) 속도 계산 (1초 주기)
  calculateSpeed();

  // 2) 속도 기반 기어 업데이트
  updateGearBasedOnSpeed();

  // 3) 주행 중 배터리 소모 (데모용)
  if (current_speed_cms > 10.0) { // 0.1 m/s 초과일 때만 소모
    battery_level -= 0.01f;
  }
  if (battery_level < 20.0f) battery_level = 100.0f;

  // 4) CAN 송신
  sendSpeedData(current_speed_cms);
  delay(50);

  sendBatteryData(battery_level);
  delay(50);

  sendGearData(current_gear);

  Serial.println("---");
  delay(500); // 500ms 주기
}

