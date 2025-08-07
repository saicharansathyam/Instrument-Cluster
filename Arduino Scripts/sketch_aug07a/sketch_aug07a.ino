#include <SPI.h>
#include <mcp_can.h>

const int SPI_CS_PIN = 10;
MCP_CAN CAN(SPI_CS_PIN);

void setup() {
    Serial.begin(115200);
    Serial.println("=== Fixed Speed Sender ===");
    
    // Use 16MHz like your working code
    if(CAN.begin(MCP_ANY, CAN_500KBPS, MCP_16MHZ) == CAN_OK) {
        Serial.println("✓ CAN Ready");
        CAN.setMode(MCP_NORMAL);
    } else {
        Serial.println("✗ CAN Failed");
        while(1);
    }
}

void loop() {
    static float speed = 0;
    
    // Convert to integer format (km/h * 100) like your working code
    int velocity_int = (int)(speed * 100);
    
    // Create 8-byte data array like your working code
    byte data[8] = {0};
    data[0] = highByte(velocity_int);  // MSB
    data[1] = lowByte(velocity_int);   // LSB
    // bytes 2-7 remain zero
    
    byte result = CAN.sendMsgBuf(0x100, 0, 8, data);
    
    Serial.print("Speed: ");
    Serial.print(speed, 1);
    Serial.print(" km/h - ");
    Serial.println(result == CAN_OK ? "✓ SENT" : "✗ FAILED");
    
    speed += 5.0;
    if(speed > 100) speed = 0;
    
    delay(1000);
}
