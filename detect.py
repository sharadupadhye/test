from pymodbus.client import ModbusSerialClient
from pymodbus import FramerType
import time

PORT = "COM4"  # Change to your serial port

# --- Common Fuji defaults ---
default_settings = {
    "baud": 9600,
    "parity": "E",
    "stop": 1,
    "device_ids": [1],
}

# --- Fallback scan ranges if default fails ---
baud_rates = [ 9600]
parities = ['E']
stop_bits = [1]
device_ids = range(1, 32)  # Try 1–15 if needed

print("🔍 Scanning for Fuji VFD communication parameters...\n")

found = False


def try_connection(baud, parity, stop, ids):
    """Try reading holding registers for given settings."""
    global found
    client = ModbusSerialClient(
        port=PORT,
        baudrate=baud,
        parity=parity,
        stopbits=stop,
        bytesize=8,
        framer=FramerType.RTU,
        timeout=0.2,  # Short timeout for faster fail
    )

    if not client.connect():
        return False

    for device_id in ids:
        try:
            result = client.read_holding_registers(address=1, count=1, device_id=device_id)
            if not result.isError() and getattr(result, "registers", None):
                print(f"\n✅ Communication Found!")
                print(f"   Baud Rate : {baud}")
                print(f"   Parity    : {parity}")
                print(f"   Stop Bits : {stop}")
                print(f"   Device ID : {device_id}")
                print(f"   (Matches Fuji parameters Y03–Y06)")
                found = True
                client.close()
                return True
        except Exception:
            pass
    client.close()
    return False


# --- Step 1: Try Fuji default first ---
print("⚡ Trying Fuji default settings first (9600 bps, N, 1 stop bit, ID 1)...")
if try_connection(default_settings["baud"], default_settings["parity"], default_settings["stop"], default_settings["device_ids"]):
    raise SystemExit

# --- Step 2: If not found, expand search ---
print("\n🔁 Fuji default not responding — expanding scan...\n")
for baud in baud_rates:
    for parity in parities:
        for stop in stop_bits:
            print(f"Trying baud={baud}, parity={parity}, stop={stop}", end="\r")
            if try_connection(baud, parity, stop, device_ids):
                raise SystemExit

print("\n❌ No Modbus response found. Check wiring, power, or RS485 polarity.")
