#include <SPI.h>
#include <mcp_can.h>

#define CS_PIN 10                 // MCP2515 CS pin
MCP_CAN CAN0(CS_PIN);

// MCP2515 crystal: change to MCP_8MHZ if your module says "8.000"
#define MCP_CLK MCP_16MHZ

// --- Encoder config ---
#define ENCODER_PIN 3
const int pulsesPerTurn = 40; // 20 slots × 2 edges
const int wheel_diameter_mm = 64;
const float wheel_circ_cm = 3.1415926f * (wheel_diameter_mm / 10.0f);
const float cm_per_pulse = wheel_circ_cm / pulsesPerTurn;
volatile unsigned long pulseCount = 0;
volatile unsigned long lastEdgeUs = 0;
const unsigned long minPeriodUs = 700; // ignore bounces faster than this

// --- Speed state ---
float speed_cms = 0.0f;
unsigned long lastCalcMs = 0;

// --- Timers ---
unsigned long lastHeartbeat = 0;

void countPulses() {
  unsigned long now = micros();
  if (now - lastEdgeUs >= minPeriodUs) {
    pulseCount++;
    lastEdgeUs = now;
  }
}

void sendSpeedCms10(float cms) {
  int16_t raw = (int16_t)(cms * 10.0f + (cms >= 0 ? 0.5f : -0.5f));
  byte data[2] = { highByte(raw), lowByte(raw) };
  CAN0.sendMsgBuf(0x100, 0, 2, data);
}

void sendGear(char g) {
  byte data[1] = { (byte)g };
  CAN0.sendMsgBuf(0x102, 0, 1, data);
}

void sendHeartbeat(uint8_t cnt) {
  byte data[2] = { 0xAA, cnt };
  CAN0.sendMsgBuf(0x700, 0, 2, data);
}

void setup() {
  Serial.begin(115200);
  pinMode(ENCODER_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN), countPulses, CHANGE);

  Serial.print("Init MCP2515... ");
  if (CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_CLK) == CAN_OK) {
    Serial.println("OK");
  } else {
    Serial.println("FAIL");
    while (1);
  }
  CAN0.setMode(MCP_NORMAL);

  Serial.println("Sending heartbeat (0x700) + real speed (0x100) + gear (0x102)");
}

void loop() {
  unsigned long now = millis();

  // --- Heartbeat every 100ms ---
  static uint8_t hbCnt = 0;
  if (now - lastHeartbeat >= 100) {
    lastHeartbeat = now;
    sendHeartbeat(hbCnt++);
  }

  // --- Speed calc every 50ms ---
  if (now - lastCalcMs >= 50) {
    unsigned long pulses;
    noInterrupts();
    pulses = pulseCount;
    pulseCount = 0;
    interrupts();

    float dt = (now - lastCalcMs) / 1000.0f;
    lastCalcMs = now;

    float inst_cms = (pulses * cm_per_pulse) / dt;

    // EMA smoothing for needle stability (slower response)
    const float alpha = 0.15f;  // lower = smoother
    speed_cms += alpha * (inst_cms - speed_cms);

    // Decay speed when no pulses (slower drop)
    if ((millis() - (lastEdgeUs / 1000UL)) > 300) {
      speed_cms *= 0.98f;  // was 0.96f
      if ((millis() - (lastEdgeUs / 1000UL)) > 1200) speed_cms = 0.0f;
    }

    sendSpeedCms10(speed_cms);

    // Gear: 'D' if moving, else 'P'
    char gear = (speed_cms > 5.0f) ? 'D' : 'P';
    sendGear(gear);

    Serial.print("[CAN] Speed: ");
    Serial.print(speed_cms, 1);
    Serial.print(" cm/s | Gear: ");
    Serial.println(gear);
  }
}
