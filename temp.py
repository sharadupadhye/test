from pymodbus.client import ModbusSerialClient

# === USER SETTINGS ===
PORT = "COM4"          # Change as needed
BAUDRATE = 9600
SLAVE_ID = 9           # Your Fuji VFD ID

# === CONNECT ===
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity='E',
    stopbits=1,
    timeout=1
)

print("🔌 Checking Modbus connection...")

if not client.connect():
    print("❌ Connection failed. Check COM port & wiring.")
    exit()

print("✅ Connected successfully.\n")
print("🔍 Probing common Fuji register ranges...\n")

# === TEST ADDRESS BLOCKS ===
ranges = [
    (0, 50),
    (500, 50),
    (1000, 50),
    (1500, 50),
    (1800, 50),
    (2000, 50),
    (2100, 50),
    (2200, 50),
    (3000, 50)
]

for start, count in ranges:
    try:
        res = client.read_holding_registers(address=start, count=count, device_id=SLAVE_ID)
        if res.isError():
            print(f"❌ Addr {start}-{start+count-1}: No response / invalid")
        else:
            print(f"✅ Addr {start}-{start+count-1}: OK ({len(res.registers)} registers read)")
            print(f"   Sample: {res.registers[:10]}")
    except Exception as e:
        print(f"⚠️ Addr {start}-{start+count-1}: Exception {e}")

client.close()
print("\n🔚 Scan complete. Note which address ranges show 'OK' — those contain your live data.")
