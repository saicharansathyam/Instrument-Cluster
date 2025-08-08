#!/usr/bin/env python3
from piracer.vehicles import PiRacerStandard
from piracer.gamepads import ShanWanGamepad
import pygame
import time
import dbus

# rc_example.py 참고로 PiRacer 임포트 가정
  # 실제 경로나 모듈명에 맞게 수정하세요

class GamepadWithGears:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() == 0:
            raise Exception("No gamepad detected")
        
        self.gamepad = pygame.joystick.Joystick(0)
        self.gamepad.init()
        
        self.setup_dbus()

        # PiRacer 초기화
        self.piracer = PiRacerStandard()
        
        
        self.current_gear = 'P'  # 시작은 Park
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
        left_x = self.gamepad.get_axis(0)
        right_y = -self.gamepad.get_axis(4)
        hat = self.gamepad.get_hat(0)
        gear_input = None
        if hat[1] == 1:
            gear_input = 'D'
        elif hat[1] == -1:
            gear_input = 'R'
        elif hat[0] == -1:
            gear_input = 'P'
        elif hat[0] == 1:
            gear_input = 'N'
        return left_x, right_y, gear_input
    
    def update_gear(self, gear_input):
        if gear_input and gear_input != self.current_gear:
            self.current_gear = gear_input
            self.gear_changed = True
            print(f"⚙️  GEAR CHANGED: {self.current_gear}")
    
    def apply_gear_logic(self, raw_throttle):
        if self.current_gear == 'P':
            return 0.0
        elif self.current_gear == 'N':
            return 0.0
        elif self.current_gear == 'R':
            return -abs(raw_throttle) if abs(raw_throttle) > 0.1 else 0.0
        elif self.current_gear == 'D':
            return raw_throttle if raw_throttle > 0.1 else 0.0
        return 0.0
    
    def get_dashboard_data(self):
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
                steering, raw_throttle, gear_input = self.read_gamepad()
                self.update_gear(gear_input)
                throttle = self.apply_gear_logic(raw_throttle)
                speed, battery = self.get_dashboard_data()
                
                # PiRacer에 제어명령 전달
                self.piracer.set_throttle_percent(throttle * 100)  # 0~100% 스케일로 전달
                self.piracer.set_steering_percent(steering * 100)  # -100~100% 스케일 가정
                
                status = (f"\r🎮 [{self.current_gear}] raw_throttle:{raw_throttle:+.2f} "
                          f"throttle:{throttle:+.2f} steering:{steering:+.2f} | "
                          f"🚗 {speed:.1f}km/h ⚡{battery:.1f}%")
                print(status, end="", flush=True)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 RC Controller stopped")
        finally:
            # 종료시 안전하게 정지
            self.piracer.set_throttle_percent(0)
            self.piracer.set_steering_percent(0)
            # self.piracer.close()

if __name__ == '__main__':
    try:
        controller = GamepadWithGears()
        print("Starting RC control with gears...")
        print("Use D-pad to change gears, sticks to control movement")
        controller.run()
    except Exception as e:
        print(f"Error: {e}")
