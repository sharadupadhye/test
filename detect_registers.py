from pymodbus.client import ModbusSerialClient
import time

# === USER SETTINGS ===
PORT = "COM4"          # Replace with your port (e.g. '/dev/ttyUSB0' on Linux)
BAUDRATE = 9600
SLAVE_ID = 9           # Fuji VFD default = 1 (check your drive)
START_ADDR = 2100      # Scan start address
NUM_REGS = 300         # Number of registers to scan (e.g. 2000–2300)
BLOCK_SIZE = 120       # Max per Modbus read (125 is absolute max)

# === CONNECT TO MODBUS ===
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity='E',        # Fuji uses No parity (y04 = 0)
    stopbits=1,
    timeout=1
)

print("🔌 Checking Modbus connection...")

if not client.connect():
    print("❌ Connection failed. Check COM port & wiring.")
    exit()

print("✅ Connected to Modbus port successfully.")

# === TEST READ TO VERIFY COMMUNICATION ===
print("🔍 Testing communication with slave device...")

try:
    test = client.read_holding_registers(address=0, count=10, device_id=SLAVE_ID)
    if test.isError():
        print("❌ Test read failed. Try adjusting SLAVE_ID, baudrate, or parity.")
        client.close()
        exit()
    else:
        print(f"✅ Test read OK. Sample data: {test.registers}\n")
except Exception as e:
    print(f"⚠️ Communication error: {e}")
    client.close()
    exit()

print(f"Starting full scan of {NUM_REGS} registers from address {START_ADDR}...\n")

# === MAIN LOOP ===
while True:
    try:
        # 1️⃣ Get live readings from VFD display (manual input)
        temp_live = float(input("Enter current Temperature (°C) from VFD: "))
        rh_live = float(input("Enter current Humidity (%RH) from VFD: "))

        # 2️⃣ Read registers in safe chunks
        data = []
        remaining = NUM_REGS
        addr = START_ADDR

        while remaining > 0:
            count = min(remaining, BLOCK_SIZE)
            result = client.read_holding_registers(address=addr, count=count, device_id=SLAVE_ID)
            if result.isError():
                print(f"❌ Modbus read error at {addr}")
                break
            data.extend(result.registers)
            addr += count
            remaining -= count

        if not data:
            print("⚠️ No data read. Check address range or VFD mapping.")
            continue

        # 3️⃣ Try to identify possible matching registers
        print("\n🔍 Checking for registers matching given values...")
        found = []
        for i, raw in enumerate(data):
            addr = START_ADDR + i

            # Example scaling guesses (depends on your VFD)
            value_60 = (raw / 1000 - 4) * 60 / 16
            value_100 = (raw / 1000 - 4) * 100 / 16

            if abs(value_60 - temp_live) <= 0.5:
                found.append((addr, raw, round(value_60, 2), "Temp (0–60°C scale)"))
            if abs(value_100 - rh_live) <= 0.5:
                found.append((addr, raw, round(value_100, 2), "Humidity (0–100% scale)"))

        if found:
            print("\n✅ Possible matching registers:")
            for addr, raw, val, typ in found:
                print(f"  → Reg {addr}: raw={raw} ≈ {val} ({typ})")
        else:
            print("\n⚠️ No close matches found. Try again or change range.")

        print("\n----------------------------------------------\n")
        time.sleep(1)

    except KeyboardInterrupt:
        print("\n🔚 Exiting...")
        break
    except Exception as e:
        print(f"⚠️ Error: {e}")

client.close()
