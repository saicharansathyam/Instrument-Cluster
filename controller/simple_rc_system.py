#!/usr/bin/env python3
import pygame
import time
import dbus
from gpio_piracer import GPIOPiRacer

class SimpleRCSystem:
    def __init__(self):
        # Initialize car
        self.car = GPIOPiRacer()
        
        # Initialize gamepad
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() == 0:
            raise Exception("❌ No gamepad detected")
        
        self.gamepad = pygame.joystick.Joystick(0)
        self.gamepad.init()
        
        # Initialize D-Bus
        self.setup_dbus()
        
        # State
        self.current_gear = 'P'
        
        print(f"✅ RC System ready with {self.gamepad.get_name()}")
    
    def setup_dbus(self):
        try:
            bus = dbus.SessionBus()
            self.dashboard = dbus.Interface(
                bus.get_object('com.piracer.dashboard', '/com/piracer/dashboard'),
                'com.piracer.dashboard'
            )
            print("✓ Dashboard connected")
        except:
            print("⚠️ Dashboard not available")
            self.dashboard = None
    
    def read_controls(self):
        pygame.event.pump()
        
        # Get stick inputs
        steering = self.gamepad.get_axis(0)     # Left stick X
        throttle = -self.gamepad.get_axis(4)    # Right stick Y (inverted)
        
        # Get gear from D-pad
        hat = self.gamepad.get_hat(0)
        gear = None
        
        if hat[1] == 1:    # UP
            gear = 'D'
        elif hat[1] == -1: # DOWN
            gear = 'R' 
        elif hat[0] == -1: # LEFT
            gear = 'P'
        elif hat[0] == 1:  # RIGHT
            gear = 'N'
        
        return steering, throttle, gear
    
    def update_gear(self, new_gear):
        if new_gear and new_gear != self.current_gear:
            self.current_gear = new_gear
            print(f"⚙️ Gear: {self.current_gear}")
    
    def apply_gear_logic(self, raw_throttle):
        """Apply gear restrictions"""
        if self.current_gear == 'P':      # Park
            return 0.0
        elif self.current_gear == 'N':    # Neutral
            return 0.0
        elif self.current_gear == 'R':    # Reverse
            return -abs(raw_throttle) if abs(raw_throttle) > 0.1 else 0.0
        elif self.current_gear == 'D':    # Drive
            return raw_throttle if raw_throttle > 0.1 else 0.0
        return 0.0
    
    def get_dashboard_data(self):
        if self.dashboard:
            try:
                speed = self.dashboard.GetSpeed()
                battery = self.dashboard.GetBatteryLevel()
                return speed, battery
            except:
                pass
        return 0.0, 0.0
    
    def run(self):
        print("🚀 RC Control active!")
        print("Controls: D-pad=gears, Left stick=steering, Right stick=throttle")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Read inputs
                steering, raw_throttle, gear_input = self.read_controls()
                
                # Update gear
                self.update_gear(gear_input)
                
                # Apply gear logic
                throttle = self.apply_gear_logic(raw_throttle)
                
                # Control car (scale to percentage)
                self.car.set_steering_percent(steering * 100)
                self.car.set_throttle_percent(throttle * 100)
                
                # Get telemetry
                speed, battery = self.get_dashboard_data()
                
                # Display status
                status = (f"\r🎮 [{self.current_gear}] "
                         f"T:{throttle:+.2f} S:{steering:+.2f} | "
                         f"🚗 {speed:.1f}km/h ⚡{battery:.1f}%")
                print(status, end="", flush=True)
                
                time.sleep(0.1)  # 10Hz
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping RC control...")
            self.car.stop()
            self.car.cleanup()

if __name__ == '__main__':
    try:
        rc = SimpleRCSystem()
        rc.run()
    except Exception as e:
        print(f"❌ Error: {e}")
