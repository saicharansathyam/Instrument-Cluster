
```mermaid
graph TD
    subgraph "Gamepad Input"
        A[Shawnpad Gamepad] --> B{User Input}
        B --> C[Steering Input]
        B --> D[Throttle Input]
    end

    subgraph "Raspberry Pi Python Script"
        C --> E[Reads Gamepad Events evdev]
        D --> E
        E --> F{Maps Input to Control Values}
        F --> G[Sends PWM Commands adafruit_pca9685]
    end

    subgraph "Waveshare Periphery Board"
        G --> H1[PCA9685 0x40 - Steering]
        G --> H2[PCA9685 0x60 - Throttle]
        H1 --> I[Generates PWM Signal CH0]
        H2 --> J[Generates PWM Signals H-Bridge Channels]
    end

    subgraph "PiRacer Actuators"
        I --> K[Steering Servo]
        J --> L[DC Motors via H-Bridge]
    end

    K --> M[Turns Wheels Left/Right]
    L --> N[Moves Car Forward/Backward]

    style A fill:#f9f,stroke:#333,stroke-width:2px,color:#000
    style B fill:#ccf,stroke:#333,stroke-width:2px,color:#000
    style C fill:#ccf,stroke:#333,stroke-width:2px,color:#000
    style D fill:#ccf,stroke:#333,stroke-width:2px,color:#000
    style E fill:#bbf,stroke:#333,stroke-width:2px,color:#000
    style F fill:#9cf,stroke:#333,stroke-width:2px,color:#000
    style G fill:#7cf,stroke:#333,stroke-width:2px,color:#000
    style H1 fill:#aaffaa,stroke:#333,stroke-width:2px,color:#000
    style H2 fill:#aaffaa,stroke:#333,stroke-width:2px,color:#000
    style I fill:#ccffcc,stroke:#333,stroke-width:2px,color:#000
    style J fill:#ccffcc,stroke:#333,stroke-width:2px,color:#000
    style K fill:#ffcc99,stroke:#333,stroke-width:2px,color:#000
    style L fill:#ffcc99,stroke:#333,stroke-width:2px,color:#000
    style M fill:#f0f0f0,stroke:#333,stroke-width:1px,color:#000
    style N fill:#f0f0f0,stroke:#333,stroke-width:1px,color:#000
```

Explanation of the Signal Flow:
User Input (Shawnpad Gamepad) :

Turning Left/Right: When you push the left joystick horizontally (left for left turn, right for right turn), the gamepad generates an analog signal for the X-axis.

Throttle Forward/Backward: When you push the right joystick vertically (up for forward, down for backward), the gamepad generates an analog signal for the Y-axis.

Raspberry Pi Reads Gamepad Events (via evdev) :

The gamepad transmits these analog signals to the Raspberry Pi.

The piracer-gamepad-control.py script, running on the Raspberry Pi, uses the evdev library to continuously read raw input events from the gamepad's device file (e.g., /dev/input/event0).

It specifically detects EV_ABS (absolute axis) events:

ABS_X for the left joystick's horizontal movement (steering).

ABS_RY (or similar, depending on your gamepad) for the right joystick's vertical movement (throttle).

Maps Input to Control Values :

The raw integer values from evdev (typically -32768 to 32767 for joysticks) are mapped by the Python script to a floating-point range, usually -1.0 to 1.0.

For steering, -1.0 means full left, 0.0 is center, and 1.0 is full right.

For throttle, 1.0 means full forward, 0.0 is stop, and -1.0 means full reverse (the sign might be inverted depending on joystick orientation).

Sends PWM Commands (via adafruit_pca9685) :

The Python script then uses the adafruit_pca9685 library to send commands over the I2C bus to the appropriate PCA9685 PWM driver based on the mapped control values.

PCA9685 Generates PWM Signals :

For Steering: The PCA9685 at I2C address 0x40 receives the command for the steering angle. It generates a precise Pulse Width Modulation (PWM) signal on its Channel 0 (CH0), which is dedicated to the steering servo. The width of this pulse determines the servo's position.

For Throttle: The PCA9685 at I2C address 0x60 receives the command for motor speed/direction. It generates PWM signals on the channels connected to the H-Bridge (e.g., CH0_PWM, CH1_PWM, CH2_EN, CH3_EN as per your diagram). These signals control the H-Bridge's operation.

Controls Steering Servo (Turns Left/Right) :

The PWM signal from PCA9685 (0x40, CH0) is sent to the steering servo.

The servo rotates its arm to the commanded angle, physically turning the PiRacer's front wheels left or right.

Controls DC Motors via H-Bridge (Forward/Backward) :

The PWM signals from PCA9685 (0x60) are sent to the H-Bridge.

The H-Bridge interprets these signals to control the dual DC motors, causing them to spin forward or backward at the commanded speed, moving the PiRacer accordingly.



