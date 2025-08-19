#!/usr/bin/env python3
import time
import pygame
import dbus
import dbus.mainloop.glib
from gi.repository import GLib
from piracer.vehicles import PiRacerStandard

BUS_NAME   = 'com.piracer.dashboard'
OBJ_PATH   = '/com/piracer/dashboard'
IFACE_NAME = 'com.piracer.dashboard'

LB_BTN = 4
RB_BTN = 5

class RCExample:
    def __init__(self):
        self.piracer = PiRacerStandard()

        pygame.init(); pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise Exception("No gamepad detected")
        self.pad = pygame.joystick.Joystick(0); self.pad.init()

        self.prev_buttons = {}
        self.turn_mode = "off"
        self.current_gear = 'P'
        self.last_speed = 0.0
        self.last_batt  = 0.0

        self.dashboard = None
        self.dbus_loop = None
        self.setup_dbus()

    def setup_dbus(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()

        obj = bus.get_object(BUS_NAME, OBJ_PATH, introspect=False)
        self.dashboard = dbus.Interface(obj, IFACE_NAME)

        # Subscribe to asynchronous updates
        bus.add_signal_receiver(self.on_speed,   dbus_interface=IFACE_NAME, signal_name='SpeedChanged')
        bus.add_signal_receiver(self.on_battery, dbus_interface=IFACE_NAME, signal_name='BatteryChanged')
        bus.add_signal_receiver(self.on_gear,    dbus_interface=IFACE_NAME, signal_name='GearChanged')

        # Spin a loop so signals are processed
        self.dbus_loop = GLib.MainLoop()
        import threading
        threading.Thread(target=self.dbus_loop.run, daemon=True).start()

    # --- Signal handlers ---
    def on_speed(self, v):   self.last_speed = float(v)
    def on_battery(self, p): self.last_batt  = float(p)
    def on_gear(self, g):    self.current_gear = str(g)

    # --- Input helpers ---
    def read_axes(self):
        pygame.event.pump()
        steering = -self.pad.get_axis(0)
        throttle = abs(self.pad.get_axis(4))
        hat = self.pad.get_hat(0)
        gear = None
        if   hat[1] ==  1: gear = 'D'
        elif hat[1] == -1: gear = 'R'
        elif hat[0] == -1: gear = 'P'
        elif hat[0] ==  1: gear = 'N'
        return steering, throttle, gear

    def read_button_edges(self):
        edges = {}
        for i in range(self.pad.get_numbuttons()):
            cur = self.pad.get_button(i) == 1
            prev = self.prev_buttons.get(i, False)
            if cur != prev:
                edges[i] = "down" if cur else "up"
            self.prev_buttons[i] = cur
        return edges

    def set_turn_signal(self, mode):
        if mode == self.turn_mode: return
        self.turn_mode = mode
        try:
            self.dashboard.SetTurnSignal(mode, timeout=0.3)
        except Exception as e:
            print(f"SetTurnSignal failed: {e}")

    def update_turn_from_buttons(self, edges):
        lb_down = edges.get(LB_BTN) == "down"
        rb_down = edges.get(RB_BTN) == "down"
        lb_up   = edges.get(LB_BTN) == "up"
        rb_up   = edges.get(RB_BTN) == "up"

        if lb_down and rb_down:
            self.set_turn_signal("hazard")
            return
        if lb_up:
            self.set_turn_signal("off" if self.turn_mode == "left" else "left")
        if rb_up:
            self.set_turn_signal("off" if self.turn_mode == "right" else "right")

    def apply_gear_logic(self, t):
        if self.current_gear in ('P', 'N'): return 0.0
        if self.current_gear == 'R': return -abs(t) if abs(t) > 0.1 else 0.0
        if self.current_gear == 'D': return  t      if t      > 0.1 else 0.0
        return 0.0

    def run(self):
        try:
            while True:
                steering, raw_t, gear = self.read_axes()

                # On gear change, tell the dashboard service
                if gear and gear != self.current_gear:
                    self.current_gear = gear
                    self.piracer.set_throttle_percent(0.0)  # jerk guard
                    try:
                        self.dashboard.SetGear(gear, timeout=0.3)
                    except Exception as e:
                        print(f"SetGear failed: {e}")

                throttle = self.apply_gear_logic(raw_t)

                edges = self.read_button_edges()
                if edges:
                    self.update_turn_from_buttons(edges)

                self.piracer.set_steering_percent(steering)
                self.piracer.set_throttle_percent(throttle)

                print(f"\r[{self.current_gear}] T:{throttle:+.2f} S:{steering:+.2f} | "
                      f"Speed:{self.last_speed:5.1f} cm/s Batt:{self.last_batt:4.1f}% Turn:{self.turn_mode}",
                      end="", flush=True)
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.piracer.set_throttle_percent(0.0)
            self.piracer.set_steering_percent(0.0)
            self.set_turn_signal("off")

if __name__ == "__main__":
    RCExample().run()
