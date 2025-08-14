#!/usr/bin/env python3
import struct
import can
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import threading
import time

import board
import busio
from adafruit_ina219 import INA219

MIN_VOLTAGE = 9.0
MAX_VOLTAGE = 12.6

IFACE = 'com.piracer.dashboard'
OBJ = '/com/piracer/dashboard'

class ABFilter:
    def __init__(self, alpha=0.4, beta=0.05, dt=0.05):
        self.v = 0.0
        self.a = 0.0
        self.dt = dt
        self.alpha = alpha
        self.beta = beta
    def update(self, meas_v):
        v_pred = self.v + self.a * self.dt
        r = meas_v - v_pred
        self.v = v_pred + self.alpha * r
        self.a = self.a + (self.beta / self.dt) * r
        return self.v

class CompleteDashboardService(dbus.service.Object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(
            IFACE, bus=bus,
            allow_replacement=True, replace_existing=True, do_not_queue=True
        )
        super().__init__(bus_name, OBJ)

        self.current_speed = 0.0
        self.battery_level = 0.0
        self.current_gear  = 'P'      # default
        self.turn_mode     = 'off'
        self.connected     = False
        self._speed_filt   = ABFilter(alpha=0.4, beta=0.07, dt=0.05)

        try:
            self.can_bus = can.interface.Bus(channel='can0', bustype='socketcan')
            self.connected = True
            print("✓ CAN connected (can0)")
        except Exception as e:
            print(f"CAN connection failed: {e}")
            return

        self.i2c_bus = busio.I2C(board.SCL, board.SDA)
        self.ina219 = INA219(self.i2c_bus, 0x41)

        threading.Thread(target=self.read_can_data, daemon=True).start()
        threading.Thread(target=self.poll_battery, daemon=True).start()

    # ---------- Methods ----------
    @dbus.service.method(IFACE, out_signature='d')
    def GetSpeed(self):
        return float(self.current_speed)

    @dbus.service.method(IFACE, out_signature='d')
    def GetBatteryLevel(self):
        return float(self.read_battery_percent())

    @dbus.service.method(IFACE, out_signature='s')
    def GetGear(self):
        return str(self.current_gear)

    @dbus.service.method(IFACE, in_signature='s', out_signature='')
    def SetGear(self, gear):
        """Set gear via D-Bus: 'P','R','N','D'."""
        gear = str(gear).upper()
        if gear not in ('P', 'R', 'N', 'D'):
            raise dbus.DBusException('Invalid gear (use P/R/N/D)')
        if gear != self.current_gear:
            print(f"[Dash] Gear -> {gear}")
            GLib.idle_add(self._emit_gear, gear)

    @dbus.service.method(IFACE, in_signature='s', out_signature='')
    def SetTurnSignal(self, mode):
        if mode not in ('off', 'left', 'right', 'hazard'):
            raise dbus.DBusException('Invalid turn signal mode')
        if mode != self.turn_mode:
            self.turn_mode = mode
            print(f"[Dash] TurnSignal -> {mode}")
            self.TurnSignalChanged(mode)

    @dbus.service.method(IFACE, out_signature='s')
    def GetTurnSignal(self):
        return str(self.turn_mode)

    # ---------- Signals ----------
    @dbus.service.signal(IFACE, signature='d')
    def SpeedChanged(self, new_speed): pass

    @dbus.service.signal(IFACE, signature='d')
    def BatteryChanged(self, new_level): pass

    @dbus.service.signal(IFACE, signature='s')
    def GearChanged(self, new_gear): pass

    @dbus.service.signal(IFACE, signature='s')
    def TurnSignalChanged(self, mode): pass

    # ---------- Emit helpers ----------
    def _emit_speed(self, v_cms):
        self.current_speed = v_cms
        self.SpeedChanged(v_cms)
        return False

    def _emit_batt(self, v_percent):
        self.battery_level = v_percent
        self.BatteryChanged(v_percent)
        return False

    def _emit_gear(self, g):
        self.current_gear = g
        self.GearChanged(g)
        return False

    # ---------- Battery ----------
    def read_battery_percent(self):
        try:
            bus_voltage = self.ina219.bus_voltage
            percent = (bus_voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE) * 100.0
            return max(0.0, min(percent, 100.0))
        except Exception as e:
            print(f"INA219 read error: {e}")
            return 0.0

    def poll_battery(self):
        while True:
            batt = self.read_battery_percent()
            if abs(self.battery_level - batt) > 0.1:
                GLib.idle_add(self._emit_batt, batt)
            time.sleep(1)

    # ---------- CAN handling ----------
    def read_can_data(self):
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

            # Speed: 0x100, unsigned int16 big-endian, /10.0 = cm/s
            if msg_id == 0x100 and len(data) >= 2:
                speed_raw = (data[0] << 8) | data[1]
                meas_cms = speed_raw / 10.0
                filt_cms = self._speed_filt.update(meas_cms)
                if abs(self.current_speed - filt_cms) > 0.1:
                    GLib.idle_add(self._emit_speed, float(filt_cms))

            # Gear via CAN (optional): 0x102, 1 byte ASCII
            elif msg_id == 0x102 and len(data) >= 1:
                gear_char = chr(data[0]) if data[0] != 0 else 'P'
                if self.current_gear != gear_char:
                    GLib.idle_add(self._emit_gear, gear_char)

        except Exception as e:
            print(f"CAN message processing error: {e}")

if __name__ == '__main__':
    try:
        service = CompleteDashboardService()
        if service.connected:
            GLib.MainLoop().run()
        else:
            print("Cannot start - CAN connection failed")
    except KeyboardInterrupt:
        pass
