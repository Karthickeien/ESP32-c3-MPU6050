# ESP32C3 MPU6050 BLE Data Logger

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![MicroPython](https://img.shields.io/badge/MicroPython-Latest-green.svg)](https://micropython.org/)
[![ESP32](https://img.shields.io/badge/ESP32-C3-red.svg)](https://www.espressif.com/)
[![BLE](https://img.shields.io/badge/BLE-5.0-blue.svg)](https://www.bluetooth.com/)

A robust system for collecting, transmitting, and logging motion sensor data from multiple ESP32C3 microcontrollers equipped with MPU6050 accelerometer/gyroscope sensors via Bluetooth Low Energy (BLE).

## 📋 Overview

This project enables real-time motion data collection from multiple ESP32C3 devices, each connected to an MPU6050 inertial measurement unit (IMU). The system uses Bluetooth Low Energy (BLE) for wireless communication between the microcontrollers and a computer running Python-based data loggers. Key features include:

- Real-time data collection from MPU6050 sensors (acceleration, gyroscope, and euler angles)
- Bluetooth Low Energy (BLE) communication
- Automatic sensor calibration
- Multi-device support with unique device IDs
- CSV data logging with timestamps
- Process management for multiple data loggers

## 🔧 Hardware Requirements

- Xiao ESP32C3 microcontrollers
- MPU6050 accelerometer/gyroscope modules
- Computer with Bluetooth capabilities (for running the logger)

## 📦 Software Dependencies

### For ESP32C3 (MicroPython):
- MicroPython firmware for ESP32C3
- Built-in libraries: `machine`, `bluetooth`, `json`, `time`, `math`

### For PC (Python):
- Python 3.6+
- Bleak (`pip install bleak`)
- Keyboard (`pip install keyboard`)

## 🚀 Project Structure

The project consists of the following components:

1. **MCU Code** (`MCU_Datalogger_with_MPU6050_Calibration.py`): MicroPython code that runs on the ESP32C3 device, interfaces with the MPU6050, and broadcasts data via BLE.

2. **PC Data Logger** (`PC_data_logger_MAC.py`): Python script that connects to a specific ESP32C3 device via BLE and logs the data to a CSV file.

3. **BLE Scanner** (`BLE_scan.py`): Utility to scan for available BLE devices and get their addresses.

4. **Multi-Logger Manager** (`Multi_Logger_response.py`): Process manager to control multiple logger instances for different devices.

## ⚙️ Installation and Setup

### 1. Flash MicroPython to ESP32C3

First, make sure your ESP32C3 has MicroPython firmware installed. Follow the [official MicroPython documentation](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html) for flashing instructions.

### 2. Install Required Python Packages

```bash
pip install bleak keyboard
```

### 3. Upload MCU Code to ESP32C3

Upload the `MCU_Datalogger_with_MPU6050_Calibration.py` file to your ESP32C3 device and rename it to `main.py` for auto-execution on boot.

### 4. Identify Your ESP32C3 Devices

Run the BLE scanner script to identify your ESP32C3 devices:

```bash
python BLE_scan.py
```

Note the MAC addresses of your devices for configuration.

## 🔍 Configuration

### MPU6050 Sensor Configuration

The MPU6050 sensor is configured with the following settings in the MCU code:

```python
# MPU6050 I2C address and registers
MPU6050_ADDR = 0x68
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47
PWR_MGMT_1 = 0x6B

# Configuration registers
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C

# Configure gyroscope (±250°/s)
i2c.writeto_mem(MPU6050_ADDR, GYRO_CONFIG, b'\x00')

# Configure accelerometer (±2g)
i2c.writeto_mem(MPU6050_ADDR, ACCEL_CONFIG, b'\x00')
```

### BLE Service Configuration

The BLE service is configured with these UUIDs:

```python
# BLE configs
SENSOR_SERVICE_UUID = bluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
SENSOR_CHAR_UUID = bluetooth.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')
```

### Device Configuration

For each ESP32C3 device, update the device ID and MAC address in the MCU code:

```python
# Device specific configuration
MAC_ADDR = ""  # Replace with your device's MAC address
BLE_NAME = f"ESP_32C3_{MAC_ADDR[-8:]}"
DEV_ID = 1  # Unique device ID number
```

For each PC data logger, update the target MAC address:

```python
# Device Configuration
TARGET_MAC = ""  # Replace with your device's MAC address
CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
```

## 📊 Usage

### 1. Start the ESP32C3 Device

Power on your ESP32C3 device with the MPU6050 properly connected. The device will:
1. Initialize the MPU6050 sensor
2. Run automatic calibration (keep the sensor still during this process)
3. Begin advertising via BLE
4. Wait for a connection from the PC data logger

### 2. Single Device Data Collection

To collect data from a single ESP32C3 device:

```bash
python PC_data_logger_MAC.py
```

### 3. Multiple Device Data Collection

Configure the `Multi_Logger_response.py` script with your device-specific data logger scripts:

```python
scripts = [
    'PC_data_logger_MAC_dev_id_1.py',
    'PC_data_logger_MAC_dev_id_2.py',
    'PC_data_logger_MAC_dev_id_3.py'
]
```

Then run the multi-logger manager:

```bash
python Multi_Logger_response.py
```

Use the following keyboard controls:
- `S`: Start all loggers
- `E`: End all loggers
- `Q`: Quit program

## 📈 Data Format

The collected data is saved in CSV format with the following columns:

```
Timestamp, Device_ID, Accel_X, Accel_Y, Accel_Z, Gyro_X, Gyro_Y, Gyro_Z, Roll, Pitch
```

Each file is named with the pattern: `ESP_32C3_<MAC_ADDRESS>_<TIMESTAMP>.csv`

## 🧠 Key Components Explained

### Automatic Sensor Calibration

The MPU6050 is calibrated on startup to reduce sensor bias:

```python
def calibrate_mpu6050(samples=500):
    print("Starting MPU6050 calibration... Keep the sensor still!")
    
    # Collect multiple samples
    for _ in range(samples):
        # Read and sum raw values
        # ...
    
    # Calculate average offsets
    calibration.accel_offset_x = accel_x_sum / samples
    calibration.accel_offset_y = accel_y_sum / samples
    calibration.accel_offset_z = (accel_z_sum / samples) - 16384  # Remove 1g offset
    calibration.gyro_offset_x = gyro_x_sum / samples
    calibration.gyro_offset_y = gyro_y_sum / samples
    calibration.gyro_offset_z = gyro_z_sum / samples
```

### Euler Angle Calculation

The system calculates roll and pitch angles from accelerometer data:

```python
def calculate_euler(accel_x, accel_y, accel_z):
    roll = atan2(accel_y, accel_z) * (180 / pi)
    pitch = atan2(-accel_x, sqrt(accel_y**2 + accel_z**2)) * (180 / pi)
    return roll, pitch
```

### BLE Data Format

Data is sent in JSON format via BLE notifications:

```python
data = {
    "timestamp": timestamp,
    "accel": {
        "x": round(accel_x, 2),
        "y": round(accel_y, 2),
        "z": round(accel_z, 2)
    },
    "gyro": {
        "x": round(gyro_x, 2),
        "y": round(gyro_y, 2),
        "z": round(gyro_z, 2)
    },
    "angles": {
        "roll": round(roll, 2),
        "pitch": round(pitch, 2)
    }
}
```

## 🔄 Process Management

The multi-logger manager can launch and monitor multiple data logger instances. It supports different operating systems (Windows, macOS, Linux) with appropriate terminal handling:

```python
def launch_script(self, script_path):
    # ...
    if self.system == 'windows':
        process = subprocess.Popen(['python', full_path], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
    elif self.system in ['linux', 'darwin']:
        if self.system == 'darwin':  # macOS
            terminal_script = os.path.join(self.script_dir, f'run_{script_path}.command')
            with open(terminal_script, 'w') as f:
                f.write(f'#!/bin/bash\ncd "{self.script_dir}"\npython3 "{script_path}"\n')
            os.chmod(terminal_script, 0o755)
            process = subprocess.Popen(['open', terminal_script])
        else:  # Linux
            process = subprocess.Popen(['gnome-terminal', '--', 'python3', full_path])
```

## 🛠️ Troubleshooting

### Common Issues

1. **Cannot find BLE device**
   - Ensure the ESP32C3 is powered on
   - Verify the MAC address configuration
   - Run `BLE_scan.py` to check if the device is advertising

2. **Connection drops frequently**
   - The PC data logger has automatic reconnection logic:
     ```python
     while True:
         try:
             # Connection and data collection
         except Exception as e:
             print(f"Connection error: {e}")
             print("Retrying in 3 seconds...")
             await asyncio.sleep(3)
     ```

3. **MPU6050 readings are inaccurate**
   - Ensure proper calibration by keeping the device still during startup
   - Check I2C connections and address (default 0x68)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

