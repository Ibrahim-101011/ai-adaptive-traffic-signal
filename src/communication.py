import time
import serial

class SerialInterface:
    def __init__(self, port: str = "COM3", baud_rate: int = 115200, timeout: float = 1.0, enabled: bool = False):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.enabled = enabled
        self.ser = None
        self.is_connected = False

        if self.enabled:
            self.connect()
        else:
            print("[Serial] Hardware communication disabled in config. Running in MOCK SERIAL mode.")

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(2.0)  # Allow ESP32 bootloader / auto-reset to settle
            self.is_connected = True
            print(f"[Serial] Connected to physical ESP32 on {self.port} at {self.baud_rate} baud.")
        except Exception as e:
            print(f"[Serial] Hardware port '{self.port}' unavailable ({e}). Running in MOCK SERIAL mode.")
            self.ser = None
            self.is_connected = False

    def send_command(self, cmd_token: str):
        """
        Transmits framed protocol token, e.g., '<R1_G>' or '<ALL_RED>'
        """
        packet = f"<{cmd_token}>\n".encode("utf-8")
        if self.is_connected and self.ser:
            try:
                self.ser.write(packet)
                self.ser.flush()
            except Exception as e:
                print(f"[Serial Write Error] {e}. Dropping to mock fallback.")
                self.is_connected = False
        else:
            # Mock mode: display framed token in terminal
            print(f"  [MOCK UART TX] --> <{cmd_token}>")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.is_connected = False
            print("[Serial] Hardware port closed cleanly.")