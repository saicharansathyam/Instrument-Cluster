#!/usr/bin/env python3
import can
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import threading
import time

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
    
    # Methods: Get current values
    @dbus.service.method(IFACE, out_signature='d')
    def GetSpeed(self):
        print(f"GetSpeed -> {self.current_speed:.1f} cm/s")
        return float(self.current_speed)
    
    @dbus.service.method(IFACE, out_signature='d')
    def GetBatteryLevel(self):
        print(f"GetBatteryLevel -> {self.battery_level:.1f}%")
        return float(self.battery_level)
    
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
    
    def read_can_data(self):
        print("Listening for all CAN data types...")
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

            # Battery: 0x101, raw/100.0 = %
            elif msg_id == 0x101 and len(data) >= 2:
                battery_raw = (data[0] << 8) | data[1]
                battery_percent = battery_raw / 100.0

                if abs(self.battery_level - battery_percent) > 0.1:
                    print(f"Battery: {battery_percent:.1f}%")
                    GLib.idle_add(self._emit_batt, battery_percent)

            # Gear: 0x102, 1바이트 문자
            elif msg_id == 0x102 and len(data) >= 1:
                gear_char = chr(data[0]) if data[0] != 0 else 'P'

                if self.current_gear != gear_char:
                    print(f"Gear: {gear_char}")
                    GLib.idle_add(self._emit_gear, gear_char)

        except Exception as e:
            print(f"CAN message processing error: {e}")

if __name__ == '__main__':
    try:
        service = CompleteDashboardService()
        if service.connected:
            loop = GLib.MainLoop()
            print("Complete dashboard service ready!")
            print("Receiving: Speed(cm/s), Battery(%), Gear")
            loop.run()
        else:
            print("Cannot start - CAN connection failed")
    except KeyboardInterrupt:
        print("\nComplete dashboard service stopped")
@dbus.service.method(IFACE, out_signature='s')
def Ping(self):
    print("[METHOD] Ping -> pong", flush=True)
    return "pong"
