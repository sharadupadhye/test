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
    temp_addr = 2098 - 1
    rh_addr   = 2103 - 1

    temp_rr = client.read_holding_registers(address=temp_addr, count=1, device_id=SLAVE_ID)
    rh_rr   = client.read_holding_registers(address=rh_addr,   count=1, device_id=SLAVE_ID)

    if temp_rr.isError() or rh_rr.isError():
        print("❌ Read error – check communication settings, unit id, parity, baud.")
    else:
        raw_temp = temp_rr.registers[0]
        raw_rh   = rh_rr.registers[0]

        # Scaling factors (based on your observed values)
        temp_scale = 0.001755
        rh_scale   = 0.00504

        temperature = raw_temp * temp_scale
        humidity = raw_rh * rh_scale

        print("\n✅ Scaled Sensor Values:")
        print(f"  Temperature: {temperature:.2f} °C")
        print(f"  Humidity:    {humidity:.2f} %RH")

        print("\nRaw Register Values:")
        print(f"  (pymodbus addr) {temp_addr}  → Reg 2098 (doc): {raw_temp}")
        print(f"  (pymodbus addr) {rh_addr}   → Reg 2103 (doc): {raw_rh}")

finally:
    client.close()
