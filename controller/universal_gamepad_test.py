#!/usr/bin/env python3
import pygame
import time
import sys

def test_gamepad():
    pygame.init()
    pygame.joystick.init()
    
    # Check for connected gamepads
    if pygame.joystick.get_count() == 0:
        print("❌ No gamepad detected!")
        print("Make sure your ShanWan gamepad is connected")
        return
    
    # Initialize first gamepad
    gamepad = pygame.joystick.Joystick(0)
    gamepad.init()
    
    print(f"🎮 Gamepad detected: {gamepad.get_name()}")
    print(f"📊 Axes: {gamepad.get_numaxes()}")
    print(f"🔘 Buttons: {gamepad.get_numbuttons()}")
    print(f"🎯 Hats (D-pad): {gamepad.get_numhats()}")
    print("-" * 60)
    print("Press buttons and move sticks to see inputs:")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    clock = pygame.time.Clock()
    
    try:
        while True:
            pygame.event.pump()
            
            # Clear screen and show current inputs
            print("\r", end="")
            
            # Analog sticks (axes)
            if gamepad.get_numaxes() >= 4:
                left_x = gamepad.get_axis(0)
                left_y = gamepad.get_axis(1)
                right_x = gamepad.get_axis(2) if gamepad.get_numaxes() > 2 else 0
                right_y = gamepad.get_axis(3) if gamepad.get_numaxes() > 3 else 0
                
                print(f"🕹️ L({left_x:+.2f},{left_y:+.2f}) R({right_x:+.2f},{right_y:+.2f}) ", end="")
            
            # Buttons
            pressed_buttons = []
            for i in range(gamepad.get_numbuttons()):
                if gamepad.get_button(i):
                    pressed_buttons.append(f"B{i}")
            
            # D-pad (hat)
            hat_directions = []
            for i in range(gamepad.get_numhats()):
                hat = gamepad.get_hat(i)
                if hat != (0, 0):
                    if hat[0] == -1: hat_directions.append("LEFT")
                    if hat[0] == 1:  hat_directions.append("RIGHT")
                    if hat[1] == 1:  hat_directions.append("UP")
                    if hat[1] == -1: hat_directions.append("DOWN")
            
            # Display pressed inputs
            inputs = pressed_buttons + hat_directions
            if inputs:
                print(f"🔘 {', '.join(inputs)}", end="")
            else:
                print("No buttons pressed", end="")
            
            print(" " * 20, end="", flush=True)  # Clear rest of line
            
            clock.tick(10)  # 10 Hz update rate
            
    except KeyboardInterrupt:
        print("\n\n🛑 Gamepad test stopped")
    finally:
        pygame.quit()

if __name__ == '__main__':
    test_gamepad()
