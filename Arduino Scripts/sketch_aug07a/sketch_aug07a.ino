#include <SPI.h>
#include <mcp_can.h>

#define ENCODER_PIN 3
#define CS_PIN 10

MCP_CAN CAN0(CS_PIN);

// If using CHANGE (rising+falling), use 40. If FALLING only, use 20.
const int pulsesPerTurn = 40;                 // encoder 20 slots × 2 edges
const int wheel_diameter_mm = 64;            // mm
const float wheel_circ_cm = 3.1415926f * (wheel_diameter_mm / 10.0f); // cm
const float cm_per_pulse = wheel_circ_cm / pulsesPerTurn;

volatile unsigned long pulseCount = 0;
volatile unsigned long lastEdgeUs = 0;
const unsigned long minPeriodUs = 700;       // ignore bounces faster than this

// display/sender state
float speed_cms = 0.0f;
unsigned long lastCalcMs = 0;

void IRAM_ATTR_dummy() {} // noop for compatibility on ESP; ignored on AVR
void countPulses() {
  unsigned long now = micros();
  if (now - lastEdgeUs >= minPeriodUs) {
    pulseCount++;
    lastEdgeUs = now;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ENCODER_PIN, INPUT);
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
  int16_t raw = (int16_t)(cms * 10.0f + (cms >= 0 ? 0.5f : -0.5f)); // round
  byte data[2] = { (byte)highByte(raw), (byte)lowByte(raw) };
  byte ok = CAN0.sendMsgBuf(0x100, 0, 2, data); // DLC = 2
  // Optional debug:
  // Serial.print("cm/s: "); Serial.print(cms,1);
  // Serial.println(ok==CAN_OK ? " ✓" : " ✗");
}

void loop() {
  unsigned long nowMs = millis();

  // Recalculate every 50 ms (20 Hz)
  if (nowMs - lastCalcMs >= 50) {
    unsigned long pulses;
    // atomic snapshot and reset
    noInterrupts();
    pulses = pulseCount;
    pulseCount = 0;
    interrupts();

    float dt = (nowMs - lastCalcMs) / 1000.0f; // seconds
    lastCalcMs = nowMs;

    float inst_cms = (pulses * cm_per_pulse) / dt;

    // EMA smoothing to keep the needle civilized
    const float alpha = 0.30f;  // higher = snappier, lower = smoother
    speed_cms += alpha * (inst_cms - speed_cms);

    // If no pulses for a while, decay gracefully
    if ((millis() - (lastEdgeUs / 1000UL)) > 300) {
      speed_cms *= 0.96f;
      if ((millis() - (lastEdgeUs / 1000UL)) > 1200) speed_cms = 0.0f;
    }

    sendSpeedCms10(speed_cms);
  }

  // Optional: send gear on 0x102 based on speed thresholds,
  // mirroring your other sketch (not shown here to keep parity).
}
