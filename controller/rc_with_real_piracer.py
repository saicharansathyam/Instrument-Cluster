#!/usr/bin/env python3
import time
import pygame
import dbus
from piracer.vehicles import PiRacerStandard

BUS_NAME   = 'com.piracer.dashboard'
OBJ_PATH   = '/com/piracer/dashboard'
IFACE_NAME = 'com.piracer.dashboard'

class RealPiRacerSystem:
    def __init__(self):
        print("🚗 Initializing PiRacer Standard...")
        self.piracer = PiRacerStandard()

        print("🎮 Initializing gamepad...")
        pygame.init(); pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise Exception("❌ No gamepad detected")
        self.gamepad = pygame.joystick.Joystick(0); self.gamepad.init()

        self.dashboard = None
        self.last_speed = 0.0
        self.last_batt  = 0.0
        self.setup_dbus()

        self.current_gear = 'P'
        print(f"✅ Real PiRacer system ready with {self.gamepad.get_name()}")

    def setup_dbus(self):
        """D-Bus 동기 폴링 전용 연결 (메인루프/스레드 사용 안 함)."""
        try:
            # 같은 세션버스 사용
            bus = dbus.SessionBus()

            # 서비스 소유 확인 (최대 5초 대기)
            dbus_iface = dbus.Interface(
                bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus'),
                'org.freedesktop.DBus'
            )
            for _ in range(50):
                if dbus_iface.NameHasOwner(BUS_NAME):
                    break
                time.sleep(0.1)
            else:
                print("⚠️ com.piracer.dashboard not running yet")
                return

            # 인트로스펙션 끄고 프록시 생성
            obj = bus.get_object(BUS_NAME, OBJ_PATH, introspect=False)
            self.dashboard = dbus.Interface(obj, IFACE_NAME)

            # 첫 읽기(타임아웃 넉넉히)
            try:
                self.last_speed = float(self.dashboard.GetSpeed(timeout=2.0))
                self.last_batt  = float(self.dashboard.GetBatteryLevel(timeout=2.0))
                print(f"✓ Dashboard connected (init {self.last_speed:.1f} cm/s, {self.last_batt:.1f}%)")
            except Exception as e:
                print(f"⚠️ initial fetch failed: {e}")

        except Exception as e:
            print(f"⚠️ Dashboard connect failed: {e}")
            self.dashboard = None

    def read_controls(self):
        pygame.event.pump()
        steering = -self.gamepad.get_axis(0)
        throttle = abs(self.gamepad.get_axis(4))
        hat = self.gamepad.get_hat(0)
        gear = None
        if   hat[1] ==  1: gear = 'D'
        elif hat[1] == -1: gear = 'R'
        elif hat[0] == -1: gear = 'P'
        elif hat[0] ==  1: gear = 'N'
        return steering, throttle, gear

    def update_gear(self, g):
        if g and g != self.current_gear:
            self.current_gear = g
            print(f"\n⚙️ GEAR CHANGED: {self.current_gear}")

    def apply_gear_logic(self, t):
        if self.current_gear in ('P','N'): return 0.0
        if self.current_gear == 'R': return -abs(t) if abs(t) > 0.1 else 0.0
        if self.current_gear == 'D': return  t      if t      > 0.1 else 0.0
        return 0.0

    def poll_dashboard(self):
        """0.2s마다 동기 호출. 실패해도 마지막 값 유지."""
        if not self.dashboard:
            return self.last_speed, self.last_batt
        try:
            self.last_speed = float(self.dashboard.GetSpeed(timeout=0.8))          # cm/s
            self.last_batt  = float(self.dashboard.GetBatteryLevel(timeout=0.8))   # %
        except Exception:
            pass
        return self.last_speed, self.last_batt

    def run(self):
        print("🚀 Real PiRacer control active!\n"
              "CONTROLS:\n"
              "🎯 D-pad UP    = Drive (D)\n"
              "🎯 D-pad DOWN  = Reverse (R)\n"
              "🎯 D-pad LEFT  = Park (P)\n"
              "🎯 D-pad RIGHT = Neutral (N)\n"
              "🕹️ Left stick X  = Steering\n"
              "🕹️ Right stick Y = Throttle\n"
              "------------------------------------------------------------")

        try:
            next_poll = 0.0
            while True:
                steering, raw_t, gear = self.read_controls()
                self.update_gear(gear)
                throttle = self.apply_gear_logic(raw_t)

                self.piracer.set_steering_percent(steering)
                self.piracer.set_throttle_percent(throttle)

                now = time.time()
                if now >= next_poll:
                    speed_cms, batt = self.poll_dashboard()
                    next_poll = now + 0.2  # 5Hz 폴링

                print(f"\r🎮 [{self.current_gear}] "
                      f"T:{throttle:+.2f} S:{steering:+.2f} | "
                      f"🚗 {self.last_speed:.1f} cm/s ⚡{self.last_batt:.1f}%",
                      end="", flush=True)
                time.sleep(0.05)  # 제어 루프 20Hz

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping RC control...")
            self.piracer.set_throttle_percent(0.0)
            self.piracer.set_steering_percent(0.0)
            print("✅ PiRacer stopped safely")

if __name__ == '__main__':
    try:
        print("=" * 60)
        print("         PIRACER RC CONTROL WITH GEARS")
        print("=" * 60)
        RealPiRacerSystem().run()
    except Exception as e:
        print(f"\n❌ Error: {e}\nCheck:\n- Service running (complete_dbus_service.py)\n- Same session bus\n- Gamepad connected\n- I2C enabled")
