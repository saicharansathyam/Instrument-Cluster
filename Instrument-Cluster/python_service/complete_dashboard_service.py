#!/usr/bin/env python3
"""
PiRacer dashboard D-Bus service with Kalman filter:
- Reads speed over CAN (0x100: cm/s)
- Smooths speed with a 2-state Kalman filter (v, a)
- Reads battery % from INA219
- Exposes values via D-Bus + signals
- Allows setting gear/turn signals via D-Bus
- Auto-detects CAN interface (prefers can0 over can1)
"""

import os
import time
import argparse
import can
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import threading
import numpy as np

# ---- INA219 (I2C) ----
import board
import busio
from adafruit_ina219 import INA219

# ==================== Tunables ====================
DT0 = 0.05           # nominal period (s) if dt not measured

# Kalman noise settings - tuned for stability
PROCESS_VAR = 4.0    # Reduced for more stable filtering
MEAS_VAR = 3.0       # Increased to trust measurements less

# Battery chemistry (3S Li-ion)
MIN_VOLTAGE = 9.0
MAX_VOLTAGE = 12.6

IFACE = 'com.piracer.dashboard'
OBJ = '/com/piracer/dashboard'

# ==================== Kalman Filter ====================
class KalmanSpeedFilter:
    def __init__(self, dt=DT0, process_var=PROCESS_VAR, meas_var=MEAS_VAR):
        # State: [v, a]ᵀ
        self.x = np.zeros((2, 1))
        self.P = np.eye(2) * 100.0  # Reduced initial uncertainty
        self.dt = dt

        self.F = np.array([[1, dt],
                           [0, 1]])
        self.H = np.array([[1, 0]])      # only speed measured
        self.R = np.array([[meas_var]])
        self.Q = np.array([[dt**4/4, dt**3/2],
                           [dt**3/2, dt**2]]) * process_var

    def update(self, z, dt=None):
        if dt is not None and abs(dt - self.dt) > 1e-3:
            self.dt = dt
            self.F = np.array([[1, dt],
                               [0, 1]])
            self.Q = np.array([[dt**4/4, dt**3/2],
                               [dt**3/2, dt**2]]) * PROCESS_VAR

        # Predict
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q

        # Update
        y = np.array([[z]]) - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(2) - K @ self.H) @ self.P

        # Clamp to non-negative
        if self.x[0, 0] < 0.0:
            self.x[0, 0] = 0.0

        return float(self.x[0, 0])

# ==================== Service ====================
class CompleteDashboardService(dbus.service.Object):
    def __init__(self, can_iface: str = "auto", debug=False):
        self.debug = debug
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(
            IFACE, bus=bus,
            allow_replacement=True, replace_existing=True, do_not_queue=True
        )
        super().__init__(bus_name, OBJ)

        # State
        self.current_speed = 0.0
        self.battery_level = 0.0
        self.current_gear = 'P'
        self.turn_mode = 'off'
        self.connected = False

        self._speed_filt = KalmanSpeedFilter()
        self._last_speed_ts = None

        # CAN
        self.can_bus = None
        self.connected = self._open_can(can_iface)
        if not self.connected:
            print("CAN connection failed; exiting init")
            return

        # INA219
        try:
            self.i2c_bus = busio.I2C(board.SCL, board.SDA)
            self.ina219 = INA219(self.i2c_bus, 0x41)
            print("✓ INA219 ready (0x41)")
        except Exception as e:
            print(f"INA219 init failed: {e}")
            self.ina219 = None

        # Threads
        threading.Thread(target=self.read_can_data, daemon=True).start()
        threading.Thread(target=self.poll_battery, daemon=True).start()

    # ---------- CAN open ----------
    def _open_can(self, iface: str) -> bool:
        tried = []
        candidates = []
        env_iface = os.environ.get("CAN_IFACE")
        if env_iface:
            candidates.append(env_iface)
        if iface and iface != "auto":
            candidates.append(iface)
        # prefer can0 first
        candidates += ["can0", "can1"]
        seen = set()
        candidates = [x for x in candidates if not (x in seen or seen.add(x))]

        for ifc in candidates:
            try:
                self.can_bus = can.interface.Bus(channel=ifc, bustype='socketcan')
                print(f"✓ CAN connected ({ifc})")
                return True
            except Exception as e:
                tried.append((ifc, str(e)))
        for ifc, err in tried:
            print(f"✗ CAN open failed {ifc}: {err}")
        return False

    # ---------- D-Bus Methods ----------
    @dbus.service.method(IFACE, out_signature='d')
    def GetSpeed(self):
        return float(self.current_speed)

    @dbus.service.method(IFACE, out_signature='d')
    def GetBatteryLevel(self):
        return float(self.battery_level)

    @dbus.service.method(IFACE, out_signature='s')
    def GetGear(self):
        return str(self.current_gear)

    @dbus.service.method(IFACE, in_signature='s', out_signature='')
    def SetGear(self, gear):
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

    # ---------- D-Bus Signals ----------
    @dbus.service.signal(IFACE, signature='d')
    def SpeedChanged(self, new_speed):
        pass

    @dbus.service.signal(IFACE, signature='d')
    def BatteryChanged(self, new_level):
        pass

    @dbus.service.signal(IFACE, signature='s')
    def GearChanged(self, new_gear):
        pass

    @dbus.service.signal(IFACE, signature='s')
    def TurnSignalChanged(self, mode):
        pass

    # ---------- Emit helpers ----------
    def _emit_speed(self, v_cms):
        self.current_speed = max(0.0, v_cms)
        self.SpeedChanged(self.current_speed)
        return False

    def _emit_batt(self, v_percent):
        self.battery_level = max(0.0, min(100.0, v_percent))
        self.BatteryChanged(self.battery_level)
        return False

    def _emit_gear(self, g):
        self.current_gear = g
        self.GearChanged(g)
        return False

    # ---------- Battery ----------
    def read_battery_percent(self):
        if not self.ina219:
            return 0.0
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
        print("Listening: CAN 0x100 (speed), 0x102 (gear)")
        while True:
            try:
                message = self.can_bus.recv(timeout=1.0)
                now = time.monotonic()
                if message:
                    self.process_can_message(message, now)
            except Exception as e:
                print(f"CAN read error: {e}")
                time.sleep(1)

    def process_can_message(self, message, now_ts):
        try:
            msg_id = message.arbitration_id
            data = message.data

            if msg_id == 0x100 and len(data) >= 2:
                speed_raw = (data[0] << 8) | data[1]   # big-endian
                meas_cms = float(speed_raw)            # Arduino sends cm/s directly

                dt = None
                if self._last_speed_ts is not None:
                    dt = now_ts - self._last_speed_ts
                self._last_speed_ts = now_ts

                # Apply Kalman filtering
                filt_cms = self._speed_filt.update(meas_cms, dt=dt)
                
                # Simple timeout-based zero forcing (no complex hysteresis)
                if (now_ts - self._last_speed_ts if self._last_speed_ts else 0) > 0.5:
                    filt_cms = 0.0

                if self.debug:
                    print(f"Raw={meas_cms:5.1f}  Filt={filt_cms:5.1f}  Out={filt_cms:5.1f}")

                if abs(self.current_speed - filt_cms) > 0.1:
                    GLib.idle_add(self._emit_speed, float(filt_cms))

            elif msg_id == 0x102 and len(data) >= 1:
                gear_char = chr(data[0]) if data[0] != 0 else 'P'
                if self.current_gear != gear_char:
                    GLib.idle_add(self._emit_gear, gear_char)

        except Exception as e:
            print(f"CAN message processing error: {e}")

# ==================== Main ====================
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--can', dest='can_iface', default='auto',
                        help='CAN interface (can0, can1, or auto)')
    parser.add_argument('--debug', action='store_true',
                        help='Print raw + filtered + output speeds')
    args = parser.parse_args()

    try:
        service = CompleteDashboardService(can_iface=args.can_iface, debug=args.debug)
        if service.connected:
            GLib.MainLoop().run()
        else:
            print("Cannot start - CAN connection failed")
    except KeyboardInterrupt:
        pass
