#!/usr/bin/env python3
from piracer.gamepads import ShanWanGamepad
import time

def test_gamepad():
    gamepad = ShanWanGamepad()
    print("Gamepad Input Explorer")
    print("Press different buttons to see available inputs")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    while True:
        try:
            data = gamepad.read_data()
            
            # Show all available attributes
            print(f"\r🎮 Sticks: L({data.analog_stick_left.x:.2f},{data.analog_stick_left.y:.2f}) "
                  f"R({data.analog_stick_right.x:.2f},{data.analog_stick_right.y:.2f}) | ", end="")
            
            # Check for button presses (these vary by gamepad model)
            buttons = []
            
            # Common button names to check
            button_attrs = ['button_x', 'button_y', 'button_a', 'button_b', 
                           'button_l1', 'button_r1', 'button_l2', 'button_r2',
                           'button_select', 'button_start', 'dpad_up', 'dpad_down', 
                           'dpad_left', 'dpad_right']
            
            for attr in button_attrs:
                if hasattr(data, attr):
                    if getattr(data, attr):
                        buttons.append(attr)
            
            if buttons:
                print(f"Pressed: {', '.join(buttons)}", end="")
            else:
                print("No buttons pressed", end="")
            
            print("", flush=True)
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\nGamepad test stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == '__main__':
    test_gamepad()
