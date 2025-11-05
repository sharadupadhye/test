from pymodbus.client import ModbusSerialClient
import time
from datetime import datetime

PORT = "COM4"
BAUDRATE = 9600
SLAVE_ID = 9
INTERVAL = 2

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='E',
    stopbits=1,
    bytesize=8,
    timeout=1
)

if not client.connect():
    print("❌ Connection failed.")
    exit()

print("✅ Connected. Reading AI1 (2120) as 4–20mA Temp, AI2 (2121) as 0–10V RH\n")

try:
    while True:
        res = client.read_holding_registers(address=2120, count=2, device_id=SLAVE_ID)
        if res.isError():
            print("⚠️ Modbus read error.")
            time.sleep(INTERVAL)
            continue

        raw_temp, raw_rh = res.registers
        temp = (raw_temp - 4000) * 60 / 16000          # 4–20 mA
        rh   = raw_rh * 100 / 10000                    # 0–10 V

        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"RawT={raw_temp:5d} RawRH={raw_rh:5d} → "
              f"T={temp:5.2f}°C RH={rh:5.2f}%")
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\n🔚 Stopped.")
finally:
    client.close()
