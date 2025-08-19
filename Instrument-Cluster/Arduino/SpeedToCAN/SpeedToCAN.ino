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

unsigned long lastCalcMs = 0;
unsigned long lastDebugMs = 0;

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
  
  // Print calibration info
  Serial.println("Ready.");
  Serial.print("Wheel circumference: "); Serial.print(wheel_circ_cm); Serial.println(" cm");
  Serial.print("CM per pulse: "); Serial.println(cm_per_pulse, 4);
  Serial.print("Min period filter: "); Serial.print(minPeriodUs); Serial.println(" us");
  Serial.println("Format: [Pulses | Raw_Speed | TX_Raw_Int | CAN_Bytes]");
}

void sendSpeedCms10(float cms) {
  if (cms < 0) cms = 0;
  if (cms > 1000.0f) cms = 1000.0f;
  
  uint16_t raw = (uint16_t)(cms + 0.5f);
  byte data[2] = { (byte)(raw >> 8), (byte)(raw & 0xFF) }; // big-endian
  
  // DEBUG: Print CAN transmission details for significant speeds
  if (cms > 30.0f) {
    Serial.print("TX: "); Serial.print(cms, 1); 
    Serial.print(" cms → raw="); Serial.print(raw);
    Serial.print(" → bytes=["); 
    Serial.print(data[0], HEX); Serial.print(",");
    Serial.print(data[1], HEX); Serial.println("]");
  }
  
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

    // Instantaneous speed from pulses in this window
    float raw_cms = (pulses * cm_per_pulse) / dt;
    float inst_cms = raw_cms;

    // Guard against wild spikes
    if (inst_cms > 300.0f) inst_cms = 300.0f;

    // Check if no edges for a while
    unsigned long lastEdgeMs = lastEdgeUs / 1000UL;
    unsigned long edgeAge = millis() - lastEdgeMs;
    
    if (edgeAge > 1200) {
      inst_cms = 0.0f;
    }

    // Send the speed via CAN
    sendSpeedCms10(inst_cms);

    // Debug output for encoder data
    if ((nowMs - lastDebugMs >= 200) && (pulses > 0 || inst_cms > 5.0)) {
      Serial.print("ENC: ["); Serial.print(pulses); 
      Serial.print(" | "); Serial.print(raw_cms, 1);
      Serial.print(" | dt="); Serial.print(dt * 1000, 0); 
      Serial.println("ms]");
      lastDebugMs = nowMs;
    }
  }
}
