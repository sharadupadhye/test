from pymodbus.client import ModbusSerialClient

# ---------------------- CONFIGURATION ----------------------
PORT = "COM4"
BAUDRATE = 9600
PARITY = "E"          # Even parity
STOPBITS = 1
TIMEOUT = 1

# List of all Modbus device IDs to scan
DEVICE_IDS = [2, 4, 7, 9]     # change as per your slaves

# Register addresses from documentation (1-based)
TEMP_REG = 2098
RH_REG   = 2103

# Scaling factors (based on your calibration)
TEMP_SCALE = 0.001755
RH_SCALE   = 0.00504
# ------------------------------------------------------------


client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity=PARITY,
    stopbits=STOPBITS,
    timeout=TIMEOUT
)

if not client.connect():
    print("❌ Connection failed. Check port and wiring.")
    raise SystemExit(1)

try:
    print("\n📡 Reading data from Modbus devices...\n")

    for device_id in DEVICE_IDS:
        print(f"--- 🧭 Device ID: {device_id} ---")

        try:
            # pymodbus uses zero-based addressing
            temp_rr = client.read_holding_registers(
                address=TEMP_REG - 1, count=1, device_id=device_id
            )
            rh_rr = client.read_holding_registers(
                address=RH_REG - 1, count=1, device_id=device_id
            )

            if temp_rr.isError() or rh_rr.isError():
                print(f"  ❌ Read error on device {device_id}")
                continue

            raw_temp = temp_rr.registers[0]
            raw_rh = rh_rr.registers[0]

            temperature = raw_temp * TEMP_SCALE
            humidity = raw_rh * RH_SCALE

            print(f"  🌡️  Temperature: {temperature:.2f} °C")
            print(f"  💧 Humidity:    {humidity:.2f} %RH")
            print(f"  🔢 Raw Temp={raw_temp}, Raw RH={raw_rh}\n")

        except Exception as e:
            print(f"  ⚠️ Error reading device {device_id}: {e}\n")

finally:
    client.close()
    print("🔌 Connection closed.")
