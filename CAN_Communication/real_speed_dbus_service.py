#!/usr/bin/env python3
import can
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import threading
import time

class RealSpeedService(dbus.service.Object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName('com.piracer.speed', bus=dbus.SessionBus())
        super().__init__(bus_name, '/com/piracer/speed')
        
        self.current_speed = 0.0
        self.connected = False
        
        print("Real Speed D-Bus service started!")
        print("Connecting to CAN...")
        
        # Connect to your working CAN interface
        try:
            self.can_bus = can.interface.Bus(channel='can1', bustype='socketcan')
            self.connected = True
            print("✓ Connected to can1")
        except Exception as e:
            print(f"✗ CAN connection failed: {e}")
            return
        
        # Start reading CAN messages (like your working Python script)
        self.can_thread = threading.Thread(target=self.read_can_data, daemon=True)
        self.can_thread.start()
    
    # Method: Get current speed (same as before)
    @dbus.service.method('com.piracer.speed', out_signature='d')
    def GetSpeed(self):
        print(f"Someone asked for speed: {self.current_speed}")
        return self.current_speed
    
    # Method: Check if CAN is connected
    @dbus.service.method('com.piracer.speed', out_signature='b')
    def IsConnected(self):
        return self.connected
    
    # Signal: Speed changed (same as before)
    @dbus.service.signal('com.piracer.speed', signature='d')
    def SpeedChanged(self, new_speed):
        pass
    
    def read_can_data(self):
        """Read real CAN data from Arduino (using your working method)"""
        print("Listening for real CAN speed data...")
        
        while True:
            try:
                message = self.can_bus.recv(timeout=1.0)
                
                if message and message.arbitration_id == 0x100:
                    # Use your proven decode method
                    speed_raw = (message.data[0] << 8) | message.data[1]
                    speed_kmh = speed_raw / 100.0
                    
                    # Only update if speed changed significantly
                    if abs(self.current_speed - speed_kmh) > 0.5:
                        self.current_speed = speed_kmh
                        print(f"Real speed from CAN: {speed_kmh:.1f} km/h")
                        
                        # Send D-Bus signal
                        self.SpeedChanged(speed_kmh)
                        
            except Exception as e:
                print(f"CAN read error: {e}")
                time.sleep(1)

if __name__ == '__main__':
    try:
        service = RealSpeedService()
        if service.connected:
            loop = GLib.MainLoop()
            print("Real speed service ready! Reading from Arduino CAN...")
            loop.run()
        else:
            print("Cannot start - CAN connection failed")
    except KeyboardInterrupt:
        print("\nReal speed service stopped")
