/*
 * 4-Way Traffic Signal Controller Firmware for ESP32
 * Baud Rate: 115200
 * Framed ASCII Commands: <R1_G>, <R1_Y>, <ALL_RED>, <R2_G>, etc.
 */

// Road 1 (North)
const int R1_RED = 15;
const int R1_YEL = 2;
const int R1_GRN = 4;

// Road 2 (East)
const int R2_RED = 16;
const int R2_YEL = 17;
const int R2_GRN = 5;

// Road 3 (South)
const int R3_RED = 18;
const int R3_YEL = 19;
const int R3_GRN = 21;

// Road 4 (West)
const int R4_RED = 22;
const int R4_YEL = 23;
const int R4_GRN = 25;

const int ALL_LEDS[] = {
  R1_RED, R1_YEL, R1_GRN,
  R2_RED, R2_YEL, R2_GRN,
  R3_RED, R3_YEL, R3_GRN,
  R4_RED, R4_YEL, R4_GRN
};

unsigned long lastCommandTime = 0;
const unsigned long TIMEOUT_MS = 6000; // 6-second failsafe watchdog
String rxBuffer = "";

void setAllRed() {
  for (int i = 0; i < 12; i++) {
    digitalWrite(ALL_LEDS[i], LOW);
  }
  digitalWrite(R1_RED, HIGH);
  digitalWrite(R2_RED, HIGH);
  digitalWrite(R3_RED, HIGH);
  digitalWrite(R4_RED, HIGH);
}

void setRoadState(int activeRoad, String aspect) {
  // Clear all lights first
  for (int i = 0; i < 12; i++) {
    digitalWrite(ALL_LEDS[i], LOW);
  }

  // Inactive approaches default to RED
  if (activeRoad != 1) digitalWrite(R1_RED, HIGH);
  if (activeRoad != 2) digitalWrite(R2_RED, HIGH);
  if (activeRoad != 3) digitalWrite(R3_RED, HIGH);
  if (activeRoad != 4) digitalWrite(R4_RED, HIGH);

  // Set active approach state
  if (activeRoad == 1) {
    if (aspect == "G") digitalWrite(R1_GRN, HIGH);
    else if (aspect == "Y") digitalWrite(R1_YEL, HIGH);
    else digitalWrite(R1_RED, HIGH);
  } else if (activeRoad == 2) {
    if (aspect == "G") digitalWrite(R2_GRN, HIGH);
    else if (aspect == "Y") digitalWrite(R2_YEL, HIGH);
    else digitalWrite(R2_RED, HIGH);
  } else if (activeRoad == 3) {
    if (aspect == "G") digitalWrite(R3_GRN, HIGH);
    else if (aspect == "Y") digitalWrite(R3_YEL, HIGH);
    else digitalWrite(R3_RED, HIGH);
  } else if (activeRoad == 4) {
    if (aspect == "G") digitalWrite(R4_GRN, HIGH);
    else if (aspect == "Y") digitalWrite(R4_YEL, HIGH);
    else digitalWrite(R4_RED, HIGH);
  }
}

void executeCommand(String cmd) {
  lastCommandTime = millis();
  cmd.trim();

  if (cmd == "ALL_RED") {
    setAllRed();
  } else if (cmd == "R1_G") { setRoadState(1, "G"); }
  else if (cmd == "R1_Y") { setRoadState(1, "Y"); }
  else if (cmd == "R2_G") { setRoadState(2, "G"); }
  else if (cmd == "R2_Y") { setRoadState(2, "Y"); }
  else if (cmd == "R3_G") { setRoadState(3, "G"); }
  else if (cmd == "R3_Y") { setRoadState(3, "Y"); }
  else if (cmd == "R4_G") { setRoadState(4, "G"); }
  else if (cmd == "R4_Y") { setRoadState(4, "Y"); }
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 12; i++) {
    pinMode(ALL_LEDS[i], OUTPUT);
  }
  setAllRed();
  lastCommandTime = millis();
}

void loop() {
  // Watchdog: If no packet received from host for 6 seconds, revert to ALL_RED
  if (millis() - lastCommandTime > TIMEOUT_MS) {
    setAllRed();
  }

  // Frame parser for '<...>' tokens
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '<') {
      rxBuffer = "";
    } else if (c == '>') {
      executeCommand(rxBuffer);
      rxBuffer = "";
    } else if (c != '\n' && c != '\r') {
      rxBuffer += c;
    }
  }
}