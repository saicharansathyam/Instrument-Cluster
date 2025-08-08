#include <SPI.h>
#include <mcp_can.h>

const int SPI_CS_PIN = 10;
MCP_CAN CAN(SPI_CS_PIN);

// CAN Message IDs
#define SPEED_MSG_ID    0x100
#define BATTERY_MSG_ID  0x101
#define GEAR_MSG_ID     0x102

// Speed sensor configuration
#define SPEED_SENSOR_PIN 3  // Changed to pin 3 (interrupt pin)
#define WHEEL_CIRCUMFERENCE_CM 20.0  // Wheel circumference in cm
#define PULSES_PER_REVOLUTION 20     // Encoder pulses per wheel revolution

// Speed calculation variables
volatile unsigned long pulse_count = 0;
unsigned long last_speed_calculation = 0;
unsigned long speed_calculation_interval = 1000; // Calculate every 1 second
float current_speed_ms = 0.0;  // Speed in m/s

// Other vehicle data
static float battery_level = 95.0;
char current_gear = 'P';

void setup() {
    Serial.begin(115200);
    Serial.println("=== Real-Time Speed Sensor (Pin 3) CAN Sender ===");
    
    // Initialize CAN
    if(CAN.begin(MCP_ANY, CAN_500KBPS, MCP_16MHZ) == CAN_OK) {
        Serial.println("✓ CAN Ready");
        CAN.setMode(MCP_NORMAL);
    } else {
        Serial.println("✗ CAN Failed");
        while(1);
    }
    
    // Setup speed sensor on interrupt pin 3
    pinMode(SPEED_SENSOR_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(SPEED_SENSOR_PIN), speedPulse, FALLING);
    
    Serial.println("✓ Speed sensor initialized on pin " + String(SPEED_SENSOR_PIN));
    Serial.println("Wheel circumference: " + String(WHEEL_CIRCUMFERENCE_CM) + " cm");
    Serial.println("Output: Speed in m/s");
    
    // Test the interrupt pin
    Serial.println("Testing interrupt pin 3...");
    for(int i = 0; i < 5; i++) {
        Serial.print("Pin 3 reading: ");
        Serial.println(digitalRead(SPEED_SENSOR_PIN));
        delay(500);
    }
}

// Interrupt function for speed sensor
void speedPulse() {
    pulse_count++;
    // Optional: Add a brief debug message (comment out for final version)
    // Serial.println("PULSE!");
}

float calculateSpeed() {
    unsigned long current_time = millis();
    unsigned long time_elapsed = current_time - last_speed_calculation;
    
    if (time_elapsed >= speed_calculation_interval) {
        // Read pulse count safely
        noInterrupts();
        unsigned long pulses = pulse_count;
        pulse_count = 0; // Reset counter
        interrupts();
        
        // Calculate speed in m/s
        // Distance = (pulses / pulses_per_rev) * circumference_cm
        float distance_cm = (float(pulses) / PULSES_PER_REVOLUTION) * WHEEL_CIRCUMFERENCE_CM;
        
        // Convert distance to meters
        float distance_m = distance_cm / 100.0;
        
        // Convert time to seconds
        float time_seconds = time_elapsed / 1000.0;
        
        // Calculate speed in m/s
        if(time_seconds > 0) {
            current_speed_ms = distance_m / time_seconds;
        } else {
            current_speed_ms = 0.0;
        }
        
        last_speed_calculation = current_time;
        
        Serial.print("Pulses: ");
        Serial.print(pulses);
        Serial.print(", Distance: ");
        Serial.print(distance_m, 3);
        Serial.print(" m, Speed: ");
        Serial.print(current_speed_ms, 3);
        Serial.println(" m/s");
        
        // Show current pin state for debugging
        Serial.print("Current pin 3 state: ");
        Serial.println(digitalRead(SPEED_SENSOR_PIN));
    }
    
    return current_speed_ms;
}

void updateGearBasedOnSpeed() {
    // Automatic gear selection based on speed in m/s
    if(current_speed_ms < 0.1) {
        current_gear = 'P';  // Park when very slow/stopped
    } else if(current_speed_ms < 2.0) {
        current_gear = '1';  // First gear (0.1 - 2.0 m/s)
    } else if(current_speed_ms < 5.0) {
        current_gear = '2';  // Second gear (2.0 - 5.0 m/s)
    } else if(current_speed_ms < 8.0) {
        current_gear = '3';  // Third gear (5.0 - 8.0 m/s)
    } else {
        current_gear = '4';  // Fourth gear (8.0+ m/s)
    }
}

void sendSpeedData(float speed_ms) {
    // Send speed in m/s * 1000 (for precision as integer)
    int speed_int = (int)(speed_ms * 1000);
    byte data[8] = {0};
    data[0] = highByte(speed_int);
    data[1] = lowByte(speed_int);
    
    byte result = CAN.sendMsgBuf(SPEED_MSG_ID, 0, 8, data);
    Serial.print("Real Speed: ");
    Serial.print(speed_ms, 3);
    Serial.print(" m/s - ");
    Serial.println(result == CAN_OK ? "✓" : "✗");
}

void sendBatteryData(float battery_percent) {
    int battery_int = (int)(battery_percent * 100);
    byte data[8] = {0};
    data[0] = highByte(battery_int);
    data[1] = lowByte(battery_int);
    
    byte result = CAN.sendMsgBuf(BATTERY_MSG_ID, 0, 8, data);
    Serial.print("Battery: ");
    Serial.print(battery_percent, 1);
    Serial.print("% - ");
    Serial.println(result == CAN_OK ? "✓" : "✗");
}

void sendGearData(char gear) {
    byte data[8] = {0};
    data[0] = (byte)gear;
    
    byte result = CAN.sendMsgBuf(GEAR_MSG_ID, 0, 8, data);
    Serial.print("Auto Gear: ");
    Serial.print(gear);
    Serial.print(" - ");
    Serial.println(result == CAN_OK ? "✓" : "✗");
}

void loop() {
    // Calculate real-time speed from sensor on pin 3
    calculateSpeed();
    
    // Update gear based on actual speed
    updateGearBasedOnSpeed();
    
    // Simulate battery drain when moving
    if(current_speed_ms > 0.1) {
        battery_level -= 0.01; // Drain when moving
    }
    if(battery_level < 20) battery_level = 100; // Reset when low
    
    // Send all CAN data
    sendSpeedData(current_speed_ms);
    delay(50);
    
    sendBatteryData(battery_level);
    delay(50);
    
    sendGearData(current_gear);
    
    Serial.println("---");
    delay(500); // Update every 500ms
}
