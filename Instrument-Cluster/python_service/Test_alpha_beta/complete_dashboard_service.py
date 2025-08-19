#!/usr/bin/env python3
"""
PiRacer dashboard D-Bus service with comprehensive debugging:
- Reads speed over CAN (0x100: cm/s * 10)
- Smooths speed with an α–β filter (simple Kalman-like)
- Reads battery % from INA219
- Exposes values via D-Bus + signals
- Allows setting gear/turn signals via D-Bus
- Detailed debug output to diagnose data loss
"""

import can
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import threading
import time
import argparse
import os

# ---- INA219 (I2C) ----
import board
import busio
from adafruit_ina219 import INA219

# ==================== Tunables ====================
# α–β filter: higher alpha/beta = snappier (less smoothing)
ALPHA = 0.40   # measurement weight (0..1). 0.40 is a good starting point
BETA  = 0.07   # acceleration correction per second
DT    = 0.05   # assumed sample period (s) ~20 Hz incoming messages

# Battery chemistry (3S Li-ion)
MIN_VOLTAGE = 9.0
MAX_VOLTAGE = 12.6

IFACE = 'com.piracer.dashboard'
OBJ   = '/com/piracer/dashboard'

# ==================== α–β filter ====================
class ABFilter:
    """
    Simple α–β filter for 1D kinematics (position/velocity).
    We apply it on speed directly by treating "position" as speed
    and "velocity" as acceleration (works well for smoothing speed).
    """
    def __init__(self, alpha=ALPHA, beta=BETA, dt=DT):
        self.v = 0.0  # filtered speed (cm/s)
        self.a = 0.0  # estimated accel (cm/s^2)
        self.dt = dt
        self.alpha = alpha
        self.beta  = beta

    def update(self, meas_v):
        # Predict
        v_pred = self.v + self.a * self.dt
        # Residual (innovation)
        r = (meas_v - v_pred)
        # Correct
        self.v = v_pred + self.alpha * r
        self.a = self.a   + (self.beta / self.dt) * r
        # Never negative speed
        if self.v < 0.0:
            self.v = 0.0
        return self.v

# ==================== Service ====================
class CompleteDashboardService(dbus.service.Object):
    def __init__(self, can_iface="auto", debug=False):
        self.debug = debug
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(
            IFACE, bus=bus,
            allow_replacement=True, replace_existing=True, do_not_queue=True
        )
        super().__init__(bus_name, OBJ)

        # State
        self.current_speed = 0.0      # cm/s (filtered)
        self.battery_level = 0.0      # %
        self.current_gear  = 'P'
        self.turn_mode     = 'off'
        self.connected     = False

        # α–β filter instance
        self._speed_filt = ABFilter(alpha=ALPHA, beta=BETA, dt=DT)

        # Debug statistics
        self.msg_count = 0
        self.high_speed_count = 0
        self.last_stats_time = time.time()

        # CAN - auto-detect interface
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
        if self.debug:
            threading.Thread(target=self._print_stats, daemon=True).start()

    def _open_can(self, iface):
        """Auto-detect CAN interface"""
        tried = []
        candidates = []
        
        env_iface = os.environ.get("CAN_IFACE")
        if env_iface:
            candidates.append(env_iface)
        if iface and iface != "auto":
            candidates.append(iface)
        # prefer can0 first
        candidates += ["can0", "can1"]
        
        # Remove duplicates while preserving order
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

    def _print_stats(self):
        """Print statistics every 5 seconds in debug mode"""
        while True:
            time.sleep(5)
            if self.msg_count > 0:
                elapsed = time.time() - self.last_stats_time
                msg_rate = self.msg_count / elapsed
                high_pct = (self.high_speed_count / self.msg_count) * 100 if self.msg_count > 0 else 0
                print(f"STATS: {self.msg_count} msgs in {elapsed:.1f}s = {msg_rate:.1f} Hz, {self.high_speed_count} high-speed ({high_pct:.1f}%)")
                self.msg_count = 0
                self.high_speed_count = 0
                self.last_stats_time = time.time()

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
        """Set gear via D-Bus: 'P','R','N','D'."""
        gear = str(gear).upper()
        if gear not in ('P','R','N','D'):
            raise dbus.DBusException('Invalid gear (use P/R/N/D)')
        if gear != self.current_gear:
            print(f"[Dash] Gear -> {gear}")
            GLib.idle_add(self._emit_gear, gear)

    @dbus.service.method(IFACE, in_signature='s', out_signature='')
    def SetTurnSignal(self, mode):
        if mode not in ('off','left','right','hazard'):
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
    def SpeedChanged(self, new_speed): pass

    @dbus.service.signal(IFACE, signature='d')
    def BatteryChanged(self, new_level): pass

    @dbus.service.signal(IFACE, signature='s')
    def GearChanged(self, new_gear): pass

    @dbus.service.signal(IFACE, signature='s')
    def TurnSignalChanged(self, mode): pass

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
            # emit if changed by >0.1%
            if abs(self.battery_level - batt) > 0.1:
                GLib.idle_add(self._emit_batt, batt)
            time.sleep(1)

    # ---------- CAN handling ----------
    def read_can_data(self):
        print("Listening: CAN 0x100 (speed), 0x102 (gear)")
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

            # Speed: 0x100, unsigned int16 BE, /10.0 = cm/s
            if msg_id == 0x100 and len(data) >= 2:
                self.msg_count += 1
                
                speed_raw = (data[0] << 8) | data[1]
                meas_cms = float(speed_raw)
                
                # Track high-speed messages
                if meas_cms > 50.0:
                    self.high_speed_count += 1
                
                # COMPREHENSIVE DEBUG for high speeds
                if self.debug and meas_cms > 30.0:
                    print(f"RX: bytes=[{data[0]:02X},{data[1]:02X}] raw_int={speed_raw} meas={meas_cms:6.1f}")
                
                filt_cms = self._speed_filt.update(meas_cms)
                
                # Debug output for all significant values
                if self.debug and (meas_cms > 5.0 or filt_cms > 5.0):
                    print(f"PROC: Raw={meas_cms:6.1f}  Filt={filt_cms:6.1f}  Out={filt_cms:6.1f}")
                
                if abs(self.current_speed - filt_cms) > 0.1:
                    GLib.idle_add(self._emit_speed, float(filt_cms))

            # Optional gear via CAN: 0x102, 1 byte ASCII
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
                        help='Print detailed CAN and processing debug info')
    args = parser.parse_args()
    
    try:
        service = CompleteDashboardService(can_iface=args.can_iface, debug=args.debug)
        if service.connected:
            if args.debug:
                print("DEBUG MODE: Detailed CAN reception and processing logging enabled")
            GLib.MainLoop().run()
        else:
            print("Cannot start - CAN connection failed")
    except KeyboardInterrupt:
        pass
