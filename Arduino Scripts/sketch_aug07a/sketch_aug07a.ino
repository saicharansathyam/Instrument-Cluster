#include <SPI.h>
#include <mcp_can.h>

const int SPI_CS_PIN = 10;
MCP_CAN CAN(SPI_CS_PIN);

// CAN Message IDs
#define SPEED_MSG_ID    0x100  // Your existing speed
#define BATTERY_MSG_ID  0x101  // New: Battery level
#define GEAR_MSG_ID     0x102  // New: Gear info

void setup() {
    Serial.begin(115200);
    Serial.println("=== Multi-Data CAN Sender ===");
    
    if(CAN.begin(MCP_ANY, CAN_500KBPS, MCP_16MHZ) == CAN_OK) {
        Serial.println("✓ CAN Ready");
        CAN.setMode(MCP_NORMAL);
    } else {
        Serial.println("✗ CAN Failed");
        while(1);
    }
}

void sendSpeedData(float speed_kmh) {
    int velocity_int = (int)(speed_kmh * 100);
    byte data[8] = {0};
    data[0] = highByte(velocity_int);
    data[1] = lowByte(velocity_int);
    
    byte result = CAN.sendMsgBuf(SPEED_MSG_ID, 0, 8, data);
    Serial.print("Speed: ");
    Serial.print(speed_kmh, 1);
    Serial.print(" km/h - ");
    Serial.println(result == CAN_OK ? "✓" : "✗");
}

void sendBatteryData(float battery_percent) {
    int battery_int = (int)(battery_percent * 100);  // 85.5% -> 8550
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
    data[0] = (byte)gear;  // 'P', 'D', 'R', 'N'
    // bytes 1-7 remain zero for now
    
    byte result = CAN.sendMsgBuf(GEAR_MSG_ID, 0, 8, data);
    Serial.print("Gear: ");
    Serial.print(gear);
    Serial.print(" - ");
    Serial.println(result == CAN_OK ? "✓" : "✗");
}

void loop() {
    // Simulate realistic vehicle data
    static float current_speed = 0;
    static float battery_level = 95.0;
    static int gear_counter = 0;
    static bool accelerating = true;
    
    // Update speed (like before)
    if(accelerating) {
        current_speed += 5.0;
        if(current_speed >= 100) accelerating = false;
    } else {
        current_speed -= 3.0;
        if(current_speed <= 0) {
            current_speed = 0;
            accelerating = true;
        }
    }
    
    // Simulate battery drain
    battery_level -= 0.02;  // Drain slowly
    if(battery_level < 20) battery_level = 100;  // Reset when low
    
    // Simulate gear changes based on speed
    char current_gear;
    if(current_speed == 0) {
        current_gear = 'P';  // Park
    } else if(current_speed < 20) {
        current_gear = '1';  // First gear
    } else if(current_speed < 50) {
        current_gear = '2';  // Second gear
    } else if(current_speed < 80) {
        current_gear = '3';  // Third gear
    } else {
        current_gear = '4';  // Fourth gear
    }
    
    // Send all three data types
    sendSpeedData(current_speed);
    delay(50);  // Small delay between messages
    
    sendBatteryData(battery_level);
    delay(50);
    
    sendGearData(current_gear);
    
    Serial.println("---");
    delay(1000);  // Send complete set every 1 second
}
