#!/usr/bin/env python3
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import threading
import time

class SpeedService(dbus.service.Object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName('com.piracer.speed', bus=dbus.SessionBus())
        super().__init__(bus_name, '/com/piracer/speed')
        
        self.current_speed = 0.0
        
        print("Speed D-Bus service started!")
        print("Service name: com.piracer.speed")
        
        # Simulate changing speed (like your counter example)
        self.speed_thread = threading.Thread(target=self.simulate_speed_changes, daemon=True)
        self.speed_thread.start()
    
    # Method: Someone can ask "What's the current speed?"
    @dbus.service.method('com.piracer.speed', out_signature='d')
    def GetSpeed(self):
        print(f"Someone asked for speed: {self.current_speed}")
        return self.current_speed
    
    # Signal: Automatically notify when speed changes
    @dbus.service.signal('com.piracer.speed', signature='d')
    def SpeedChanged(self, new_speed):
        pass
    
    def simulate_speed_changes(self):
        """Simulate speed changing (like a real car accelerating)"""
        accelerating = True
        
        while True:
            time.sleep(1)  # Update every 1 second
            
            # Simulate realistic acceleration/deceleration
            if accelerating:
                self.current_speed += 5.0
                if self.current_speed >= 100:
                    accelerating = False
            else:
                self.current_speed -= 3.0
                if self.current_speed <= 0:
                    self.current_speed = 0
                    accelerating = True
            
            print(f"Speed updated to: {self.current_speed:.1f} km/h")
            
            # Send signal to notify anyone listening
            self.SpeedChanged(self.current_speed)

if __name__ == '__main__':
    try:
        service = SpeedService()
        loop = GLib.MainLoop()
        print("Speed service ready! Speed will change every 1 second...")
        loop.run()
    except KeyboardInterrupt:
        print("\nSpeed service stopped")
