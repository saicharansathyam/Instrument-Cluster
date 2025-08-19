#!/usr/bin/env python3
"""
Stable Battery SOC Monitor for PiRacer with INA219
Addresses voltage fluctuation issues with averaging and proper calibration
"""

import time
import board
import busio
from adafruit_ina219 import INA219
import statistics

class StableBatterySOC:
    def __init__(self):
        # 3S 18650 Li-ion discharge curve
        self.voltage_soc_table = [
            (12.60, 100),  # 4.20V per cell - Full charge
            (12.45, 95),   # 4.15V per cell
            (12.30, 90),   # 4.10V per cell
            (12.15, 85),   # 4.05V per cell
            (12.00, 80),   # 4.00V per cell
            (11.85, 75),   # 3.95V per cell
            (11.70, 70),   # 3.90V per cell
            (11.58, 65),   # 3.86V per cell
            (11.46, 60),   # 3.82V per cell
            (11.34, 55),   # 3.78V per cell
            (11.22, 50),   # 3.74V per cell - Mid discharge
            (11.10, 45),   # 3.70V per cell
            (10.98, 40),   # 3.66V per cell
            (10.86, 35),   # 3.62V per cell
            (10.74, 30),   # 3.58V per cell
            (10.62, 25),   # 3.54V per cell
            (10.50, 20),   # 3.50V per cell
            (10.35, 15),   # 3.45V per cell
            (10.20, 10),   # 3.40V per cell
            (10.05, 5),    # 3.35V per cell
            (9.90,  2),    # 3.30V per cell
            (9.75,  1),    # 3.25V per cell
            (9.00,  0),    # 3.00V per cell - Cutoff
        ]
        
        # Smoothing parameters
        self.voltage_history = []
        self.current_history = []
        self.max_history_samples = 10
        self.internal_resistance_ohms = 0.15  # 3S pack estimate
        
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
    
    def get_stable_voltage(self, ina219, samples=5):
        """Get averaged voltage reading to reduce noise"""
        voltage_readings = []
        
        for _ in range(samples):
            try:
                voltage_readings.append(ina219.bus_voltage)
                time.sleep(0.02)  # 20ms between samples
            except:
                continue
        
        if not voltage_readings:
            return None
            
        # Remove outliers if we have enough samples
        if len(voltage_readings) >= 3:
            voltage_readings.sort()
            # Remove highest and lowest reading
            voltage_readings = voltage_readings[1:-1]
        
        return statistics.mean(voltage_readings)
    
    def get_stable_current(self, ina219, samples=3):
        """Get averaged current reading"""
        current_readings = []
        
        for _ in range(samples):
            try:
                current = ina219.current
                current_readings.append(current)
                time.sleep(0.01)
            except:
                continue
        
        if not current_readings:
            return None
            
        return statistics.mean(current_readings)
    
    def apply_load_compensation(self, voltage, current_ma):
        """Compensate for voltage drop under load"""
        if current_ma is None or voltage is None:
            return voltage
            
        current_amps = abs(current_ma) / 1000.0
        compensated_voltage = voltage + (current_amps * self.internal_resistance_ohms)
        
        return min(compensated_voltage, 12.6)
    
    def update_history(self, voltage, current):
        """Maintain rolling history for trend analysis"""
        if voltage is not None:
            self.voltage_history.append(voltage)
            if len(self.voltage_history) > self.max_history_samples:
                self.voltage_history.pop(0)
        
        if current is not None:
            self.current_history.append(current)
            if len(self.current_history) > self.max_history_samples:
                self.current_history.pop(0)
    
    def get_soc_from_ina219(self, ina219):
        """Get stable SOC reading with noise reduction"""
        try:
            # Get stable measurements
            voltage = self.get_stable_voltage(ina219, samples=5)
            current_ma = self.get_stable_current(ina219, samples=3)
            
            if voltage is None:
                return {'error': 'Failed to read voltage'}
            
            # Update history
            self.update_history(voltage, current_ma)
            
            # Apply load compensation
            compensated_voltage = self.apply_load_compensation(voltage, current_ma)
            
            # Calculate SOC
            soc = self.interpolate_soc(compensated_voltage)
            
            # Get trend information
            voltage_trend = "stable"
            if len(self.voltage_history) >= 3:
                recent_avg = statistics.mean(self.voltage_history[-3:])
                older_avg = statistics.mean(self.voltage_history[:3]) if len(self.voltage_history) >= 6 else recent_avg
                
                if recent_avg > older_avg + 0.05:
                    voltage_trend = "rising"
                elif recent_avg < older_avg - 0.05:
                    voltage_trend = "falling"
            
            return {
                'soc_percent': soc,
                'voltage_raw': voltage,
                'voltage_compensated': compensated_voltage,
                'current_ma': current_ma,
                'voltage_trend': voltage_trend,
                'voltage_stability': self.get_voltage_stability(),
                'battery_type': '3S 18650 Li-ion'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_voltage_stability(self):
        """Calculate voltage stability metric"""
        if len(self.voltage_history) < 3:
            return "unknown"
        
        std_dev = statistics.stdev(self.voltage_history)
        
        if std_dev < 0.02:
            return "very stable"
        elif std_dev < 0.05:
            return "stable"
        elif std_dev < 0.10:
            return "moderate"
        else:
            return "unstable"

def main():
    print("Stable PiRacer Battery Monitor - Press Ctrl+C to exit")
    print("=" * 70)
    
    try:
        # Initialize I2C and INA219
        i2c = busio.I2C(board.SCL, board.SDA)
        ina219 = INA219(i2c, 0x41)
        
        # Set proper calibration for expected current range
        # Adjust this based on your system's current draw
        try:
            ina219.set_calibration_16V_400mA()  # For 0-400mA range
            print("✓ INA219 calibrated for 16V/400mA range")
        except:
            print("! Using default INA219 calibration")
        
        print("✓ INA219 initialized successfully")
        
        # Initialize SOC calculator
        battery_soc = StableBatterySOC()
        print("✓ Stable Battery SOC calculator ready")
        print()
        
        # Print header
        print(f"{'Time':<8} {'SOC':<6} {'Raw V':<8} {'Comp V':<8} {'Current':<10} {'Trend':<8} {'Stability':<12} {'Status'}")
        print("-" * 70)
        
        while True:
            # Get battery data
            battery_data = battery_soc.get_soc_from_ina219(ina219)
            current_time = time.strftime("%H:%M:%S")
            
            if 'error' in battery_data:
                print(f"{current_time:<8} ERROR: {battery_data['error']}")
            else:
                soc = battery_data['soc_percent']
                v_raw = battery_data['voltage_raw']
                v_comp = battery_data['voltage_compensated']
                current = battery_data['current_ma']
                trend = battery_data['voltage_trend']
                stability = battery_data['voltage_stability']
                
                # Determine status
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
                
                # Format current
                current_str = f"{current:.0f}mA" if current is not None else "N/A"
                
                print(f"{current_time:<8} {soc:5.1f}% {v_raw:6.2f}V {v_comp:6.2f}V {current_str:<10} {trend:<8} {stability:<12} {status}")
            
            time.sleep(3)  # Update every 3 seconds for stability
            
    except KeyboardInterrupt:
        print("\nExiting battery monitor...")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure INA219 is connected to I2C bus at address 0x41")
        print("Check wiring and connections")

if __name__ == "__main__":
    main()
