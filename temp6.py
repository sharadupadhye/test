from pymodbus.client import ModbusSerialClient
import time
from datetime import datetime

# === CONNECTION SETTINGS ===
PORT = "COM4"           # Replace with your actual Modbus COM port
BAUDRATE = 9600
SLAVE_ID = 9            # Fuji VFD Modbus address (set per drive)
TEMP_REG = 2121         # AI1 (Temperature, terminal 12)
RH_REG = 2122           # AI2 (Humidity, terminal V2)

# === FULL SCALE VALUES ===
TEMP_FULL_SCALE = 60.0   # Temperature 0–60°C
RH_FULL_SCALE = 100.0    # Humidity 0–100% RH

# === CONNECT TO MODBUS ===
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity='E',  # Usually Even parity for Fuji
    stopbits=1,
    timeout=1
)

print("🔌 Connecting to Fuji FRENIC-HVAC VFD...")
if not client.connect():
    print("❌ Connection failed. Check COM port, wiring, or Modbus address.")
    exit()
print("✅ Connected successfully.\n")

print(f"Reading Temperature (Reg {TEMP_REG}) and Humidity (Reg {RH_REG})...\n")

try:
    while True:
        # Read both registers together
        rr = client.read_holding_registers(address=TEMP_REG, count=2, device_id=SLAVE_ID)
        if rr.isError():
            print("❌ Modbus read error. Check wiring or register range.")
            time.sleep(1)
            continue

        raw_temp = rr.registers[0]
        raw_rh = rr.registers[1]

        # Convert signed values (handle negatives)
        if raw_temp > 32767:
            raw_temp -= 65536
        if raw_rh > 32767:
            raw_rh -= 65536

        # Apply scaling (Data format [29]: ±20000 = ±100%)
        temp_c = (raw_temp / 20000) * TEMP_FULL_SCALE
        rh_percent = (raw_rh / 20000) * RH_FULL_SCALE

        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"RawTemp={raw_temp:6d} RawRH={raw_rh:6d} → "
              f"Temp={temp_c:6.2f} °C  RH={rh_percent:6.2f} %")

        time.sleep(2)

except KeyboardInterrupt:
    print("\n🔚 Stopped by user.")

finally:
    client.close()
