#include <SPI.h>
#include <mcp_can.h>

#define ENCODER_PIN 3
#define CS_PIN 10

MCP_CAN CAN0(CS_PIN);

// Encoder parameters
const int pulsesPerTurn = 40;                 // encoder 20 slots × 2 edges
const int wheel_diameter_mm = 64;             // mm
const float wheel_circ_cm = 3.1415926f * (wheel_diameter_mm / 10.0f); // cm
const float cm_per_pulse = wheel_circ_cm / pulsesPerTurn;

volatile unsigned long pulseCount = 0;
volatile unsigned long lastEdgeUs = 0;
const unsigned long minPeriodUs = 300;        // ignore edges faster than this

float speed_cms = 0.0f;
unsigned long lastCalcMs = 0;

void countPulses() {
  unsigned long now = micros();
  if ((long)(now - lastEdgeUs) >= (long)minPeriodUs) {
    pulseCount++;
    lastEdgeUs = now;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ENCODER_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN), countPulses, CHANGE);

  Serial.print("Initializing MCP2515... ");
  if (CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_16MHZ) == CAN_OK) {
    Serial.println("OK");
  } else {
    Serial.println("FAIL");
    while (1);
  }
  CAN0.setMode(MCP_NORMAL);
  Serial.println("Ready.");
}

void sendSpeedCms10(float cms) {
  if (cms < 0) cms = 0;
  if (cms > 1000.0f) cms = 1000.0f;
  uint16_t raw = (uint16_t)(cms * 10.0f + 0.5f);
  byte data[2] = { (byte)(raw >> 8), (byte)(raw & 0xFF) }; // big-endian
  CAN0.sendMsgBuf(0x100, 0, 2, data);
}

void loop() {
  unsigned long nowMs = millis();

  if (nowMs - lastCalcMs >= 50) { // 20 Hz
    unsigned long pulses;
    noInterrupts();
    pulses = pulseCount;
    pulseCount = 0;
    interrupts();

    float dt = (nowMs - lastCalcMs) / 1000.0f;
    lastCalcMs = nowMs;

    float inst_cms = (pulses * cm_per_pulse) / dt;
    if (inst_cms > 300.0f) inst_cms = 300.0f; // spike guard

    const float alpha = 0.30f;
    speed_cms += alpha * (inst_cms - speed_cms);

    unsigned long lastEdgeMs = lastEdgeUs / 1000UL;
    unsigned long since = (millis() - lastEdgeMs);
    if (since > 300) {
      speed_cms *= 0.96f;
      if (since > 1200) speed_cms = 0.0f;
    }

    sendSpeedCms10(speed_cms);
  }
}
