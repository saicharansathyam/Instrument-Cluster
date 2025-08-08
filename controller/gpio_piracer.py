#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

class GPIOPiRacer:
    def __init__(self):
        """Simple GPIO-based PiRacer control"""
        print("🚗 Initializing GPIO PiRacer...")
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Define pins (adjust these based on your actual wiring)
        self.steering_pin = 18  # GPIO pin for steering servo
        self.throttle_pin = 19  # GPIO pin for ESC/motor
        
        # Setup PWM (50Hz for servos/ESCs)
        GPIO.setup(self.steering_pin, GPIO.OUT)
        GPIO.setup(self.throttle_pin, GPIO.OUT)
        
        self.steering_pwm = GPIO.PWM(self.steering_pin, 50)
        self.throttle_pwm = GPIO.PWM(self.throttle_pin, 50)
        
        # Start with neutral positions (1.5ms pulse = 7.5% duty cycle at 50Hz)
        self.steering_pwm.start(7.5)
        self.throttle_pwm.start(7.5)
        
        print("✅ GPIO PiRacer initialized")
        print(f"   Steering: GPIO {self.steering_pin}")
        print(f"   Throttle: GPIO {self.throttle_pin}")
    
    def set_steering_percent(self, percent):
        """Set steering: -100 (full left) to +100 (full right)"""
        try:
            # Clamp to valid range
            percent = max(-100, min(100, percent))
            
            # Convert to PWM duty cycle
            # Servo range: 1ms (5%) to 2ms (10%) pulse width
            # Neutral: 1.5ms (7.5%)
            duty_cycle = 7.5 + (percent * 2.5 / 100)  # 5% to 10% range
            
            self.steering_pwm.ChangeDutyCycle(duty_cycle)
            
        except Exception as e:
            print(f"Steering error: {e}")
    
    def set_throttle_percent(self, percent):
        """Set throttle: -100 (full reverse) to +100 (full forward)"""
        try:
            # Clamp to valid range
            percent = max(-100, min(100, percent))
            
            # Convert to PWM duty cycle
            duty_cycle = 7.5 + (percent * 2.5 / 100)  # 5% to 10% range
            
            self.throttle_pwm.ChangeDutyCycle(duty_cycle)
            
        except Exception as e:
            print(f"Throttle error: {e}")
    
    def stop(self):
        """Stop vehicle safely"""
        self.set_throttle_percent(0)
        self.set_steering_percent(0)
        print("🛑 Vehicle stopped")
    
    def cleanup(self):
        """Clean up GPIO"""
        self.steering_pwm.stop()
        self.throttle_pwm.stop()
        GPIO.cleanup()
        print("🧹 GPIO cleaned up")

# Simple test
if __name__ == '__main__':
    print("Testing GPIO PiRacer...")
    
    try:
        car = GPIOPiRacer()
        
        print("Testing steering...")
        for angle in [-100, -50, 0, 50, 100, 0]:
            print(f"  Steering: {angle}%")
            car.set_steering_percent(angle)
            time.sleep(1)
        
        print("Testing throttle (be careful!)...")
        for throttle in [0, 20, 0, -20, 0]:
            print(f"  Throttle: {throttle}%")
            car.set_throttle_percent(throttle)
            time.sleep(1)
        
        car.stop()
        print("✅ Test complete")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        if 'car' in locals():
            car.cleanup()
