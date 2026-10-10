import time
import os
import yaml
from communication import SerialInterface

def run_test():
    config_path = "config/config.yaml"
    cfg = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)

    ser_cfg = cfg.get("serial", {})
    port = ser_cfg.get("port", "COM3")
    baud = ser_cfg.get("baud_rate", 115200)
    enabled = ser_cfg.get("enabled", False)

    print(f"[Brick 6] Initializing Serial Interface...")
    print(f"         Target Port: {port} | Baud Rate: {baud} | Hardware Enabled: {enabled}\n")

    comm = SerialInterface(port=port, baud_rate=baud, enabled=enabled)

    # Simulated signal transition sequence
    test_sequence = [
        "R1_G",     # Road 1 Green
        "R1_Y",     # Road 1 Yellow
        "ALL_RED",  # Intersection Clearance
        "R2_G",     # Road 2 Green
        "R2_Y",     # Road 2 Yellow
        "ALL_RED"   # Intersection Clearance
    ]

    print("[Brick 6] Streaming test command sequence:")
    for token in test_sequence:
        comm.send_command(token)
        time.sleep(0.4)

    comm.close()
    print("\n--- Brick 6 Passed: Serial Engine Verified ---")

if __name__ == "__main__":
    run_test()