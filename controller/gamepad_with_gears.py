#!/usr/bin/env python3
import pygame
import time
import dbus

class GamepadWithGears:
    def __init__(self):
        # Initialize pygame and gamepad
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() == 0:
            raise Exception("No gamepad detected")
        
        self.gamepad = pygame.joystick.Joystick(0)
        self.gamepad.init()
        
        # Initialize D-Bus connection to your dashboard
        self.setup_dbus()
        
        # Vehicle state
        self.current_gear = 'P'  # Start in Park
        self.gear_changed = False
        
        print(f"🎮 Connected: {self.gamepad.get_name()}")
        print("🚗 RC Car with Gear Control Ready!")
        print()
        print("GEAR CONTROLS (Xbox 360):")
        print("🎯 D-Pad UP    → Drive (D)")
        print("🎯 D-Pad DOWN  → Reverse (R)")
        print("🎯 D-Pad LEFT  → Park (P)")
        print("🎯 D-Pad RIGHT → Neutral (N)")
        print()
        print("MOVEMENT CONTROLS:")
        print("🕹️ Right Stick Y → Throttle")
        print("🕹️ Left Stick X  → Steering")
        print("-" * 50)
    
    def setup_dbus(self):
        """Connect to your dashboard D-Bus service"""
        try:
            bus = dbus.SessionBus()
            self.dashboard = dbus.Interface(
                bus.get_object('com.piracer.dashboard', '/com/piracer/dashboard'),
                'com.piracer.dashboard'
            )
            print("✓ Connected to Dashboard D-Bus")
        except Exception as e:
            print(f"⚠️  Dashboard D-Bus not available: {e}")
            self.dashboard = None
    
    def read_gamepad(self):
        pygame.event.pump()
        
        # Read analog sticks
        left_x = self.gamepad.get_axis(0)    # Steering
        left_y = self.gamepad.get_axis(1)    # Not used
        right_x = self.gamepad.get_axis(3)   # Not used  
        right_y = -self.gamepad.get_axis(4)  # Throttle (inverted)
        
        # Read D-pad for gear selection
        hat = self.gamepad.get_hat(0)
        gear_input = None
        
        if hat[1] == 1:    # D-pad UP
            gear_input = 'D'
        elif hat[1] == -1: # D-pad DOWN  
            gear_input = 'R'
        elif hat[0] == -1: # D-pad LEFT
            gear_input = 'P'
        elif hat[0] == 1:  # D-pad RIGHT
            gear_input = 'N'
        
        return left_x, right_y, gear_input
    
    def update_gear(self, gear_input):
        """Update current gear based on input"""
        if gear_input and gear_input != self.current_gear:
            self.current_gear = gear_input
            self.gear_changed = True
            print(f"⚙️  GEAR CHANGED: {self.current_gear}")
    
    def apply_gear_logic(self, raw_throttle):
        """Apply gear-specific throttle logic"""
        if self.current_gear == 'P':      # Park - no movement
            return 0.0
        elif self.current_gear == 'N':    # Neutral - no power
            return 0.0
        elif self.current_gear == 'R':    # Reverse - invert throttle
            return -abs(raw_throttle) if abs(raw_throttle) > 0.1 else 0.0
        elif self.current_gear == 'D':    # Drive - normal throttle
            return raw_throttle if raw_throttle > 0.1 else 0.0
        
        return 0.0
    
    def get_dashboard_data(self):
        """Get data from dashboard service"""
        if self.dashboard:
            try:
                speed = self.dashboard.GetSpeed()
                battery = self.dashboard.GetBatteryLevel()
                return speed, battery
            except:
                return 0.0, 0.0
        return 0.0, 0.0
    
    def run(self):
   
        try:
            while True:
            # Read gamepad
                steering, raw_throttle, gear_input = self.read_gamepad()
            
            # Update gear
                self.update_gear(gear_input)
            
            # Apply gear logic to throttle
                throttle = self.apply_gear_logic(raw_throttle)
            
            # Get dashboard data
                speed, battery = self.get_dashboard_data()
            
            # Display status with raw throttle and throttle after gear logic
                status = (f"\r🎮 [{self.current_gear}] raw_throttle:{raw_throttle:+.2f} "
                      f"throttle:{throttle:+.2f} steering:{steering:+.2f} | "
                      f"🚗 {speed:.1f}km/h ⚡{battery:.1f}%")
            
                print(status, end="", flush=True)
            
                time.sleep(0.1)  # 10Hz update
            
        except KeyboardInterrupt:
            print("\n🛑 RC Controller stopped")

if __name__ == '__main__':
    try:
        controller = GamepadWithGears()
        print("Starting RC control with gears...")
        print("Use D-pad to change gears, sticks to control movement")
        controller.run()
    except Exception as e:
        print(f"Error: {e}")
