```mermaid
graph TD
    subgraph Gamepad Input
        A[Shawnpad Gamepad] --> B{User Input};
        B -- Left Joystick (X) --> C[Steering Input];
        B -- Right Joystick (Y) --> D[Throttle Input];
    end

    subgraph Raspberry Pi Python Script
        C --> E[Reads Gamepad Events (evdev)];
        D --> E;
        E --> F{Maps Input to Control Values};
        F -- Mapped Steering (-1.0 to 1.0) --> G[Sends PWM Commands (adafruit_pca9685)];
        F -- Mapped Throttle (-1.0 to 1.0) --> G;
    end

    subgraph Waveshare Periphery Board
        G -- I2C Command --> H1[PCA9685 (0x40) - Steering];
        G -- I2C Command --> H2[PCA9685 (0x60) - Throttle];
        H1 --> I[Generates PWM Signal (CH0)];
        H2 --> J[Generates PWM Signals (H-Bridge Channels)];
    end

    subgraph PiRacer Actuators
        I --> K[Steering Servo];
        J --> L[DC Motors via H-Bridge];
    end

    K --> M[Turns Wheels Left/Right];
    L --> N[Moves Car Forward/Backward];

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#ccf,stroke:#333,stroke-width:2px
    style C fill:#ccf,stroke:#333,stroke-width:2px
    style D fill:#ccf,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#9cf,stroke:#333,stroke-width:2px
    style G fill:#7cf,stroke:#333,stroke-width:2px
    style H1 fill:#aaffaa,stroke:#333,stroke-width:2px
    style H2 fill:#aaffaa,stroke:#333,stroke-width:2px
    style I fill:#ccffcc,stroke:#333,stroke-width:2px
    style J fill:#ccffcc,stroke:#333,stroke-width:2px
    style K fill:#ffcc99,stroke:#333,stroke-width:2px
    style L fill:#ffcc99,stroke:#333,stroke-width:2px
    style M fill:#f0f0f0,stroke:#333,stroke-width:1px
    style N fill:#f0f0f0,stroke:#333,stroke-width:1px
```


