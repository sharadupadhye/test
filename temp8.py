from pymodbus.client import ModbusSerialClient
import time
from datetime import datetime

PORT = "COM4"
BAUDRATE = 9600
SLAVE_ID = 9

TEMP_REG = 2098
RH_REG   = 2103

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

print("✅ Connected. Reading Temperature (Reg 2121) & Humidity (Reg 2122)...\n")

try:
    while True:
        rr = client.read_holding_registers(address=TEMP_REG - 1, count=2, device_id=SLAVE_ID)
        if rr.isError():
            print("⚠️ Modbus read error.")
            time.sleep(2)
            continue

        raw_temp, raw_rh = rr.registers

        # Conversion based on your calibration
        temp_c = raw_temp * 0.00755      # °C
        rh_pct = raw_rh  * 0.00269       # %RH

        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"RawT={raw_temp:5d} RawRH={raw_rh:5d} → "
              f"T={temp_c:6.2f}°C RH={rh_pct:6.2f}%")
        time.sleep(2)

except KeyboardInterrupt:
    print("\n🔚 Stopped.")
finally:
    client.close()
