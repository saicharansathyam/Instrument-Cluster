# Embedded Vehicle Control System

## System Overview

```mermaid
graph LR
    A[🤖 Arduino Sender] -->|CAN Bus| B[🖥️ D-Bus Service]
    B -->|D-Bus IPC| C[🎮 Control Dashboard]
    
    A1[Speed Sensor] --> A
    A2[Gear Logic] --> A
    
    B1[Battery Monitor] --> B
    B2[CAN Bridge] --> B
    
    C1[Gamepad Input] --> C
    C2[PiRacer Control] --> C
```

---

## 1. Arduino Sensor Node (Real-time Processing)

```mermaid
flowchart TD
    A[🔧 Setup CAN Controller] --> B[⚡ Configure Speed Sensor Interrupt]
    B --> C[🔄 Main Loop Start]
    
    C --> D[📊 Calculate Speed from Pulses]
    D --> E[⚙️ Determine Gear from Speed]
    E --> F[📡 Send Speed Data CAN ID: 0x100]
    F --> G[📡 Send Gear Data CAN ID: 0x102]
    G --> H[⏱️ Loop Delay]
    H --> C
    
    I[⚡ Speed Sensor ISR] -.-> D
    
    style A fill:#ff6b6b
    style I fill:#ffeb3b
```

---

## 2. D-Bus Service (Protocol Bridge)

```mermaid
flowchart TD
    A[🔧 Initialize D-Bus Service] --> B[🔌 Setup INA219 Battery Monitor]
    B --> C[🧵 Start CAN Reader Thread]
    C --> D[🧵 Start Battery Poll Thread]
    
    subgraph "CAN Thread"
        E[📥 Listen for CAN Messages] --> F{Message Type?}
        F -->|0x100| G[📊 Process Speed Data]
        F -->|0x102| H[⚙️ Process Gear Data]
        G --> I[📢 Emit SpeedChanged Signal]
        H --> J[📢 Emit GearChanged Signal]
    end
    
    subgraph "Battery Thread"
        K[🔋 Read INA219 Every 1s] --> L[📢 Emit BatteryChanged Signal]
        L --> K
    end
    
    C --> E
    D --> K
    
    style A fill:#4ecdc4
    style C fill:#81c784
    style D fill:#81c784
```

---

## 3. Control Dashboard (User Interface)

```mermaid
flowchart TD
    A[🔧 Initialize Gamepad] --> B[🚗 Initialize PiRacer]
    B --> C[🔗 Connect to D-Bus Service]
    C --> D[🔄 Main Control Loop]
    
    D --> E[🎮 Read Gamepad Input]
    E --> F[⚙️ Apply Gear-based Logic]
    F --> G[🚗 Set Steering & Throttle]
    
    D --> H[📊 Poll D-Bus Telemetry]
    H --> I[📺 Update Dashboard Display]
    
    G --> J[⏱️ Control Loop Delay]
    I --> J
    J --> D
    
    style A fill:#45b7d1
    style G fill:#66bb6a
    style I fill:#ab47bc
```

---

## 4. Data Communication Flow

```mermaid
sequenceDiagram
    participant A as Arduino
    participant C as CAN Bus
    participant D as D-Bus Service
    participant R as Dashboard
    
    Note over A: Speed sensor interrupt
    A->>C: Speed Data (0x100)
    A->>C: Gear Data (0x102)
    
    C->>D: CAN Message Received
    D->>D: Process & Validate Data
    
    D->>R: SpeedChanged Signal
    D->>R: GearChanged Signal
    
    Note over D: Every 1 second
    D->>D: Read Battery (INA219)
    D->>R: BatteryChanged Signal
    
    R->>R: Update Dashboard
    Note over R: Gamepad input
    R->>R: Control PiRacer
```

---

## 5. CAN Message Protocol

```mermaid
graph TD
    subgraph "CAN Message Structure"
        A[CAN ID: 0x100<br/>Speed Data] --> B[Byte 0-1: Speed RPM<br/>Byte 2-3: Speed cm/s<br/>Byte 4-7: Timestamp]
        
        C[CAN ID: 0x102<br/>Gear Data] --> D[Byte 0: Current Gear<br/>Byte 1: Gear Status<br/>Byte 2-3: Reserved<br/>Byte 4-7: Timestamp]
    end
    
    style A fill:#ff9800
    style C fill:#2196f3
```

---

## 6. System Architecture Layers

```mermaid
graph TB
    subgraph "Application Layer"
        A1[Control Dashboard]
        A2[Telemetry Display]
    end
    
    subgraph "Service Layer"
        B1[D-Bus Service]
        B2[Protocol Bridge]
        B3[Data Aggregation]
    end
    
    subgraph "Hardware Abstraction"
        C1[CAN Driver]
        C2[I2C Driver]
        C3[GPIO Driver]
    end
    
    subgraph "Hardware Layer"
        D1[Arduino Uno]
        D2[CAN Controller]
        D3[Speed Sensor]
        D4[INA219 Battery Monitor]
        D5[PiRacer Motors]
    end
    
    A1 --> B1
    A2 --> B1
    B1 --> C1
    B2 --> C2
    B3 --> C3
    C1 --> D2
    C2 --> D4
    C3 --> D5
    D2 --> D1
    D3 --> D1
    
    style A1 fill:#e1f5fe
    style B1 fill:#f3e5f5
    style C1 fill:#fff3e0
    style D1 fill:#ffebee
```

---

## Quick Start

1. **Arduino Setup**: Upload sensor code with CAN library
2. **D-Bus Service**: Run Python service script with root privileges
3. **Dashboard**: Launch control interface with gamepad connected

## Hardware Requirements

- Arduino Uno with CAN shield
- Speed sensor (Hall effect or optical encoder)
- INA219 current/voltage sensor
- PiRacer platform
- USB gamepad controller

## Software Dependencies

- Arduino: `mcp_can.h` library
- Python: `python-can`, `dbus-python`, `pygame`
- System: `can-utils` for debugging
