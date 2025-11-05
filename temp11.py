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
TEMP_REG = 2098       # Temperature register
RH_REG   = 2103       # Humidity register
M49_REG  = 3000       # <-- replace with actual M49 address (terminal 12 voltage)
M54_REG  = 3005       # <-- replace with actual M54 address (terminal V2 voltage)

# Scaling factors
TEMP_SCALE = 0.001755   # as per calibration
RH_SCALE   = 0.00504    # as per calibration

# Voltage scaling (M49, M54): -32768 → +32767 maps to -10V → +10V
def scale_voltage(raw):
    return (raw / 32767.0) * 10.0
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
            # Read all required registers
            temp_rr = client.read_holding_registers(address=TEMP_REG - 1, count=1, device_id=device_id)
            rh_rr   = client.read_holding_registers(address=RH_REG - 1,   count=1, device_id=device_id)
            m49_rr  = client.read_holding_registers(address=M49_REG - 1,  count=1, device_id=device_id)
            m54_rr  = client.read_holding_registers(address=M54_REG - 1,  count=1, device_id=device_id)

            if any(rr.isError() for rr in [temp_rr, rh_rr, m49_rr, m54_rr]):
                print(f"  ❌ Read error on device {device_id}")
                continue

            # Raw register values
            raw_temp = temp_rr.registers[0]
            raw_rh   = rh_rr.registers[0]
            raw_m49  = m49_rr.registers[0]
            raw_m54  = m54_rr.registers[0]

            # Apply scaling
            temperature = raw_temp * TEMP_SCALE
            humidity    = raw_rh * RH_SCALE
            voltage_12  = scale_voltage(raw_m49)
            voltage_v2  = scale_voltage(raw_m54)

            # Display neatly
            print(f"  🌡️  Temperature: {temperature:.2f} °C")
            print(f"  💧 Humidity:    {humidity:.2f} %RH")
            print(f"  ⚡ M49 Terminal [12] Voltage: {voltage_12:.2f} V")
            print(f"  ⚡ M54 Terminal [V2] Voltage: {voltage_v2:.2f} V")
            print(f"  🔢 Raw -> Temp={raw_temp}, RH={raw_rh}, M49={raw_m49}, M54={raw_m54}\n")

        except Exception as e:
            print(f"  ⚠️ Error reading device {device_id}: {e}\n")

finally:
    client.close()
    print("🔌 Connection closed.")
