#!/usr/bin/env python3
"""
PiRacer-specific Battery SOC implementation
For 2S Li-ion battery pack (7.4V nominal, 2600mAh)
"""

import time
import board
import busio
from adafruit_ina219 import INA219

class PiRacerBatterySOC:
    def __init__(self):
        # 2S Li-ion discharge curve (voltage per cell * 2)
        # Specific to PiRacer's 7.4V 2S Li-ion battery pack
        self.voltage_soc_table = [
            (8.40, 100),  # 4.20V per cell - Full charge
            (8.30, 95),   # 4.15V per cell
            (8.20, 90),   # 4.10V per cell
            (8.10, 85),   # 4.05V per cell
            (8.00, 80),   # 4.00V per cell
            (7.90, 75),   # 3.95V per cell
            (7.80, 70),   # 3.90V per cell
            (7.72, 65),   # 3.86V per cell
            (7.64, 60),   # 3.82V per cell
            (7.56, 55),   # 3.78V per cell
            (7.48, 50),   # 3.74V per cell - Mid discharge
            (7.40, 45),   # 3.70V per cell (nominal voltage)
            (7.32, 40),   # 3.66V per cell
            (7.24, 35),   # 3.62V per cell
            (7.16, 30),   # 3.58V per cell
            (7.08, 25),   # 3.54V per cell
            (7.00, 20),   # 3.50V per cell
            (6.90, 15),   # 3.45V per cell
            (6.80, 10),   # 3.40V per cell
            (6.70, 5),    # 3.35V per cell
            (6.60, 2),    # 3.30V per cell
            (6.50, 1),    # 3.25V per cell
            (6.00, 0),    # 3.00V per cell - Cutoff
        ]
        
        self.load_compensation_history = []
        self.max_history_samples = 10
        
    def interpolate_soc(self, voltage):
        """Linear interpolation between lookup table points"""
        if voltage >= self.voltage_soc_table[0][0]:
            return 100.0
        if voltage <= self.voltage_soc_table[-1][0]:
            return 0.0
            
        for i in range(len(self.voltage_soc_table) - 1):
            v_high, soc_high = self.voltage_soc_table[i]
            v_low, soc_low = self.voltage_soc_table[i + 1]
            
            if v_low <= voltage <= v_high:
                ratio = (voltage - v_low) / (v_high - v_low)
                return soc_low + ratio * (soc_high - soc_low)
        
        return 0.0
    
    def apply_load_compensation(self, voltage, current_ma):
        """Compensate for voltage drop under load"""
        if current_ma is None:
            return voltage
            
        # 2S pack internal resistance (lower than 3S)
        internal_resistance_ohms = 0.10  # 100mΩ total for 2S pack
        
        current_amps = abs(current_ma) / 1000.0
        compensated_voltage = voltage + (current_amps * internal_resistance_ohms)
        
        return min(compensated_voltage, 8.4)  # Cap at 2S max voltage
    
    def get_soc_from_ina219(self, ina219):
        """Get SOC from INA219 with PiRacer-specific calibration"""
        try:
            voltage = ina219.bus_voltage
            current_ma = None
            
            try:
                current_ma = ina219.current
            except:
                pass
            
            # Apply load compensation
            compensated_voltage = self.apply_load_compensation(voltage, current_ma)
            
            # Get SOC from 2S lookup table
            soc = self.interpolate_soc(compensated_voltage)
            
            return {
                'soc_percent': soc,
                'voltage_raw': voltage,
                'voltage_compensated': compensated_voltage,
                'current_ma': current_ma,
                'battery_type': '2S Li-ion (7.4V)'
            }
            
        except Exception as e:
            return {
                'soc_percent': 0.0,
                'voltage_raw': 0.0,
                'voltage_compensated': 0.0,
                'current_ma': None,
                'error': str(e)
            }

def main():
    print("PiRacer 2S Li-ion Battery Monitor - Press Ctrl+C to exit")
    print("=" * 65)
    
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ina219 = INA219(i2c, 0x41)
        print("✓ INA219 initialized successfully")
        
        battery_soc = PiRacerBatterySOC()
        print("✓ PiRacer 2S Battery SOC calculator ready")
        print()
        
        print(f"{'Time':<8} {'SOC':<6} {'Raw V':<8} {'Comp V':<8} {'Current':<10} {'Status'}")
        print("-" * 65)
        
        while True:
            battery_data = battery_soc.get_soc_from_ina219(ina219)
            current_time = time.strftime("%H:%M:%S")
            
            if 'error' in battery_data:
                print(f"{current_time:<8} ERROR: {battery_data['error']}")
            else:
                soc = battery_data['soc_percent']
                v_raw = battery_data['voltage_raw']
                v_comp = battery_data['voltage_compensated']
                current = battery_data['current_ma']
                
                if soc > 75:
                    status = "GOOD"
                elif soc > 50:
                    status = "OK"
                elif soc > 25:
                    status = "LOW"
                elif soc > 10:
                    status = "VERY LOW"
                else:
                    status = "CRITICAL"
                
                current_str = f"{current:.0f}mA" if current is not None else "N/A"
                
                print(f"{current_time:<8} {soc:5.1f}% {v_raw:6.2f}V {v_comp:6.2f}V {current_str:<10} {status}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nExiting battery monitor...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
