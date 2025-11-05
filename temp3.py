from pymodbus.client import ModbusSerialClient
import time
from datetime import datetime

PORT = "COM4"
BAUDRATE = 9600
SLAVE_ID = 7
INTERVAL = 2

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='E',
    stopbits=1,
    bytesize=8,
    timeout=1
)

print("🔌 Connecting to VFD...")

if not client.connect():
    print("❌ Connection failed.")
    exit()

print("✅ Connected. Reading Temperature (Reg 2120) & Humidity (Reg 2121)...\n")

try:
    while True:
        res = client.read_holding_registers(address=2120, count=2, device_id=SLAVE_ID)
        if res.isError():
            print("⚠️ Modbus read error.")
            time.sleep(INTERVAL)
            continue

        raw_temp, raw_rh = res.registers  # 2120 = Temp, 2121 = RH

        # --- Calibrated formulas ---
        temp_c = (raw_temp + 2990) * 60 / 16000
        rh = (raw_rh - 4000) * 0.00358

        print(f"[{datetime.now().strftime('%H:%M:%S')}]  "
              f"RawTemp={raw_temp:5d}  RawRH={raw_rh:5d}  "
              f"=>  Temp={temp_c:6.2f} °C  RH={rh:6.2f} %")

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\n🔚 Stopped by user.")
finally:
    client.close()
