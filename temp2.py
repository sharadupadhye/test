from pymodbus.client import ModbusSerialClient
import time

PORT = "COM4"
BAUDRATE = 9600
SLAVE_ID = 9

START_ADDR = 2100
NUM_REGS = 50

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity='E',
    stopbits=1,
    timeout=1
)

if not client.connect():
    print("❌ Connection failed.")
    exit()

print(f"✅ Connected. Monitoring {NUM_REGS} registers from {START_ADDR}...\n")

prev = [0] * NUM_REGS

while True:
    try:
        res = client.read_holding_registers(address=START_ADDR, count=NUM_REGS, device_id=SLAVE_ID)
        if res.isError():
            print("⚠️ Read error.")
            time.sleep(1)
            continue

        data = res.registers
        for i, val in enumerate(data):
            if abs(val - prev[i]) > 5:  # change threshold
                print(f"Reg {START_ADDR + i}: {val}")
        prev = data
        time.sleep(1)

    except KeyboardInterrupt:
        print("\n🔚 Exiting...")
        break
    except Exception as e:
        print(f"⚠️ Error: {e}")
        break

client.close()
