import board
import busio
from adafruit_ina219 import INA219
import time

# I2C setup
i2c_bus = busio.I2C(board.SCL, board.SDA)
ina219 = INA219(i2c_bus, 0x41)  # 0x41 is the address from your PiRacer schematic

# Define your battery chemistry here
min_v = 9.0    # Voltage considered "empty" (3.0V per cell for 3S)
max_v = 12.6   # Voltage considered "full" (4.2V per cell for 3S)

while True:
    try:
        bus_voltage = ina219.bus_voltage
        current = ina219.current
        power = ina219.power

        # Calculate percentage (clamped to 0-100)
        percent = (bus_voltage - min_v) / (max_v - min_v) * 100
        percent = max(0, min(percent, 100))

        print(f"Battery Voltage: {bus_voltage:.2f} V")
        print(f"Current Draw:   {current:.1f} mA")
        print(f"Power Usage:    {power:.1f} mW")
        print(f"Battery %:      {percent:.1f}%")
        print("-" * 30)

        time.sleep(1)  # Update every 1 second
    except KeyboardInterrupt:
        print("Exiting.")
        break
    except Exception as e:
        print("Error reading INA219:", e)
        time.sleep(1)
