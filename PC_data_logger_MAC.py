import asyncio
from bleak import BleakScanner, BleakClient
import json
from datetime import datetime
import csv
import os

# Device Configuration
TARGET_MAC = "" # MAC address of the ESP32-C3 device
CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

class DataLogger:
    def __init__(self, device_name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"ESP_32C3_{device_name}_{timestamp}.csv"
        self.device_name = device_name
        
        self.file = open(self.filename, 'w', newline='')
        self.csv_writer = csv.writer(self.file)
        
        self.csv_writer.writerow([
            'Timestamp',
            'Device_ID',
            'Accel_X', 'Accel_Y', 'Accel_Z',
            'Gyro_X', 'Gyro_Y', 'Gyro_Z',
            'Roll', 'Pitch'
        ])
        
        self.count = 0

    def log_data(self, data):
        self.csv_writer.writerow([
            data['timestamp'],
            data.get('device_id', TARGET_MAC),
            data['accel']['x'], data['accel']['y'], data['accel']['z'],
            data['gyro']['x'], data['gyro']['y'], data['gyro']['z'],
            data['angles']['roll'], data['angles']['pitch']
        ])
        self.file.flush()
        
        self.count += 1
        if self.count % 100 == 0:
            print(f"Samples collected: {self.count}")

    def close(self):
        self.file.close()
        print(f"\nData collection completed. Total samples: {self.count}")
        print(f"Data saved to: {self.filename}")

async def find_target_device():
    print(f"Scanning for MPU6050 device with MAC: {TARGET_MAC}...")
    devices = await BleakScanner.discover()
    
    target_device = next((d for d in devices if d.address.upper() == TARGET_MAC.upper()), None)
    
    if target_device:
        print(f"Found target device: {target_device.name or 'Unknown'} ({target_device.address})")
        return target_device
    
    print("\nTarget device not found. Available devices:")
    for i, device in enumerate(devices):
        print(f"{i+1}. Name: {device.name or 'Unknown'}")
        print(f"   Address: {device.address}")
        print(f"   RSSI: {device.rssi}")
    return None

async def run_data_collection():
    try:
        device = await find_target_device()
        if not device:
            print(f"Could not find device with MAC: {TARGET_MAC}")
            return
        
        logger = DataLogger(device.address.replace(':', ''))
        
        def notification_handler(sender, data):
            try:
                decoded_data = json.loads(data.decode())
                logger.log_data(decoded_data)
            except Exception as e:
                print(f"Error processing data: {e}")
        
        while True:
            try:
                print(f"\nConnecting to {device.name or device.address}...")
                async with BleakClient(device) as client:
                    print("Connected! Starting data collection...")
                    print("Press Ctrl+C to stop...")
                    
                    await client.start_notify(CHAR_UUID, notification_handler)
                    
                    while True:
                        await asyncio.sleep(0.1)
                        
            except Exception as e:
                print(f"Connection error: {e}")
                print("Retrying in 3 seconds...")
                await asyncio.sleep(3)

    except KeyboardInterrupt:
        print("\nData collection stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'logger' in locals():
            logger.close()

if __name__ == "__main__":
    print("MPU6050 BLE Scanner and Logger")
    asyncio.run(run_data_collection())