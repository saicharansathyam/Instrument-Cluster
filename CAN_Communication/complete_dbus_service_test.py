#!/usr/bin/env python3
import can
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import threading
import time

# === INA219 Battery Monitoring ===
import board
import busio
from adafruit_ina219 import INA219

# INA219 I2C setup (0x41 per your PiRacer schematic)
i2c_bus = busio.I2C(board.SCL, board.SDA)
ina219 = INA219(i2c_bus, 0x41)

# Battery chemistry settings (3S Li-Ion/LiPo example)
MIN_VOLTAGE = 9.0    # Voltage considered "empty"
MAX_VOLTAGE = 12.6   # Voltage considered "full"

IFACE = 'com.piracer.dashboard'
OBJ = '/com/piracer/dashboard'

class CompleteDashboardService(dbus.service.Object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(IFACE, bus=bus, allow_replacement=True, replace_existing=True, do_not_queue=True)
        super().__init__(bus_name, OBJ)
        
        # Initialize all data
        self.current_speed = 0.0      # cm/s
        self.battery_level = 0.0      # %
        self.current_gear = 'P'
        self.connected = False
        
        print("Complete Dashboard D-Bus service started!")
        print(f"Service name: {IFACE}")
        
        # Connect to CAN
        try:
            self.can_bus = can.interface.Bus(channel='can0', bustype='socketcan')
            self.connected = True
            print("✓ Connected to can0")
        except Exception as e:
            print(f"✗ CAN connection failed: {e}")
            return
        
        # Start reading CAN messages (background thread)
        self.can_thread = threading.Thread(target=self.read_can_data, daemon=True)
        self.can_thread.start()

        # Start battery monitoring (background thread)
        self.batt_thread = threading.Thread(target=self.poll_battery, daemon=True)
        self.batt_thread.start()
    
    # Methods: Get current values
    @dbus.service.method(IFACE, out_signature='d')
    def GetSpeed(self):
        print(f"GetSpeed -> {self.current_speed:.1f} cm/s")
        return float(self.current_speed)
    
    @dbus.service.method(IFACE, out_signature='d')
    def GetBatteryLevel(self):
        # Always return latest battery value
        battery = self.read_battery_percent()
        print(f"GetBatteryLevel -> {battery:.1f}%")
        return float(battery)
    
    @dbus.service.method(IFACE, out_signature='s')
    def GetGear(self):
        print(f"GetGear -> {self.current_gear}")
        return str(self.current_gear)
    
    @dbus.service.method(IFACE, out_signature='b')
    def IsConnected(self):
        return bool(self.connected)
    
    # Signals: Notify when values change
    @dbus.service.signal(IFACE, signature='d')
    def SpeedChanged(self, new_speed):  # cm/s
        pass
    
    @dbus.service.signal(IFACE, signature='d')
    def BatteryChanged(self, new_level):  # %
        pass
    
    @dbus.service.signal(IFACE, signature='s')
    def GearChanged(self, new_gear):
        pass

    # --- emit helpers (메인루프에서 실행되도록 idle_add 사용) ---
    def _emit_speed(self, v_cms):
        self.current_speed = v_cms
        self.SpeedChanged(v_cms)
        return False  # idle_add: 한번만 실행

    def _emit_batt(self, v_percent):
        self.battery_level = v_percent
        self.BatteryChanged(v_percent)
        return False

    def _emit_gear(self, g):
        self.current_gear = g
        self.GearChanged(g)
        return False

    # --- INA219 battery reading ---
    def read_battery_percent(self):
        try:
            bus_voltage = ina219.bus_voltage
            # Battery % calculation (clamped)
            percent = (bus_voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE) * 100
            percent = max(0, min(percent, 100))
            return percent
        except Exception as e:
            print(f"[Battery] INA219 read error: {e}")
            return 0.0

    # Poll battery every 1s and emit signal if changed
    def poll_battery(self):
        print("Battery monitor thread started.")
        while True:
            batt = self.read_battery_percent()
            # Only emit signal if change > 0.1%
            if abs(self.battery_level - batt) > 0.1:
                print(f"Battery (INA219): {batt:.1f}%")
                GLib.idle_add(self._emit_batt, batt)
            time.sleep(1)

    def read_can_data(self):
        print("Listening for CAN: Speed, Gear (battery now via INA219)...")
        while True:
            try:
                message = self.can_bus.recv(timeout=1.0)
                if message:
                    self.process_can_message(message)
            except Exception as e:
                print(f"CAN read error: {e}")
                time.sleep(1)
    
    def process_can_message(self, message):
        try:
            msg_id = message.arbitration_id
            data = message.data

            # Speed: 0x100, 상위바이트|하위바이트 → raw. 스케일: raw/10.0 = cm/s
            if msg_id == 0x100 and len(data) >= 2:
                speed_raw = (data[0] << 8) | data[1]
                speed_cms = speed_raw / 10.0  # 예: 1234 -> 123.4 cm/s

                if abs(self.current_speed - speed_cms) > 0.1:
                    print(f"Speed: {speed_cms:.1f} cm/s")
                    GLib.idle_add(self._emit_speed, speed_cms)

            # Gear: 0x102, 1바이트 문자
            elif msg_id == 0x102 and len(data) >= 1:
                gear_char = chr(data[0]) if data[0] != 0 else 'P'

                if self.current_gear != gear_char:
                    print(f"Gear: {gear_char}")
                    GLib.idle_add(self._emit_gear, gear_char)

        except Exception as e:
            print(f"CAN message processing error: {e}")

    @dbus.service.method(IFACE, out_signature='s')
    def Ping(self):
        print("[METHOD] Ping -> pong", flush=True)
        return "pong"

if __name__ == '__main__':
    try:
        service = CompleteDashboardService()
        if service.connected:
            loop = GLib.MainLoop()
            print("Complete dashboard service ready!")
            print("Receiving: Speed(cm/s), Battery(% from INA219), Gear")
            loop.run()
        else:
            print("Cannot start - CAN connection failed")
    except KeyboardInterrupt:
        print("\nComplete dashboard service stopped")
