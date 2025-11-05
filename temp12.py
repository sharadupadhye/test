from pymodbus.client import ModbusSerialClient

PORT = "COM4"
BAUDRATE = 9600
SLAVE_ID = 9

client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity='E',        # Even parity
    stopbits=1,
    timeout=1
)

if not client.connect():
    print("❌ Connection failed.")
    raise SystemExit(1)

try:
    # pymodbus uses zero-based addressing
    temp_addr = 2098 - 1   # M49 / M54 type
    rh_addr   = 2103 - 1

    temp_rr = client.read_holding_registers(address=temp_addr, count=1, device_id=SLAVE_ID)
    rh_rr   = client.read_holding_registers(address=rh_addr,   count=1, device_id=SLAVE_ID)

    if temp_rr.isError() or rh_rr.isError():
        print("❌ Read error – check communication settings, unit id, parity, baud.")
    else:
        # Convert to signed 16-bit integer
        raw_temp = temp_rr.registers[0]
        if raw_temp > 32767:
            raw_temp -= 65536

        raw_rh = rh_rr.registers[0]
        if raw_rh > 32767:
            raw_rh -= 65536

        # Full-scale voltage interpretation (–10V to +10V)
        temp_voltage = (raw_temp / 32767) * 10
        rh_voltage   = (raw_rh   / 32767) * 10

        # Example: assuming 0–10 V corresponds to 0–60 °C and 0–100 %RH
        temperature = ((temp_voltage + 10) / 20) * 60   # shift –10→+10 to 0→20, scale to 0–60 °C
        humidity    = ((rh_voltage   + 10) / 20) * 100  # shift –10→+10 to 0→20, scale to 0–100 %RH

        print("\n✅ Scaled Sensor Values:")
        print(f"  🌡️ Temperature: {temperature:.2f} °C")
        print(f"  💧 Humidity:    {humidity:.2f} %RH")

        print("\nRaw Register Values:")
        print(f"  (pymodbus addr) {temp_addr}  → Reg 2098 (doc): {raw_temp}")
        print(f"  (pymodbus addr) {rh_addr}   → Reg 2103 (doc): {raw_rh}")
        print(f"  Voltage inputs: Temp={temp_voltage:.3f} V, RH={rh_voltage:.3f} V")

finally:
    client.close()
