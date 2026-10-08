# AI-Based Adaptive Traffic Signal with Emergency Vehicle Priority

A multidisciplinary academic prototype that uses **computer vision, YOLO vehicle detection, traffic-density estimation, adaptive signal control, emergency vehicle priority, and ESP32 hardware control** for a single 4-way intersection.

> **Project scope:** One 4-way intersection prototype  
> **AI:** Pretrained YOLO + OpenCV  
> **Backend:** Python  
> **Hardware:** ESP32 + traffic LEDs  
> **Communication:** USB Serial initially  
> **Dashboard:** Streamlit  
> **Evaluation:** Fixed-time vs adaptive control

---

## 1. Project Overview

Traditional traffic signals commonly use fixed timings. However, traffic density changes continuously between roads. A road with very few vehicles may receive the same green duration as a heavily congested road.

This project demonstrates an adaptive prototype that:

1. Receives traffic video from a camera/video file.
2. Detects vehicles using a pretrained YOLO model.
3. Tracks/counts vehicles.
4. Assigns vehicles to one of four roads.
5. Estimates traffic density.
6. Selects the road that should receive priority.
7. Dynamically determines green duration.
8. Provides safe emergency-vehicle priority.
9. Sends signal commands to an ESP32.
10. Controls physical traffic-light LEDs.
11. Logs data for evaluation.
12. Compares adaptive control against fixed-time control.

### High-level pipeline

```text
Camera / Video
      ↓
YOLO Vehicle Detection
      ↓
Tracking / Counting
      ↓
Road Assignment
      ↓
Traffic Density
      ↓
Adaptive Signal Controller
      ↓
 ┌───────────────┐
 │ Normal Mode   │
 │ Emergency     │
 │ Priority      │
 └───────┬───────┘
         ↓
Python → USB Serial → ESP32
                         ↓
                   Traffic LEDs
```

---

# 2. Problem Statement

Fixed-time traffic signals do not always reflect real-time traffic conditions.

For example:

```text
Road 1 → 20 vehicles
Road 2 → 3 vehicles
Road 3 → 7 vehicles
Road 4 → 1 vehicle
```

A fixed-time controller may give every road similar green time.

An adaptive controller can instead give more priority to the road with higher traffic while still maintaining minimum service and fairness for other roads.

Emergency vehicles introduce another problem: normal signal scheduling may delay an ambulance or other emergency vehicle.

The project therefore combines:

- Computer-vision-based traffic estimation
- Adaptive signal control
- Emergency vehicle priority
- Embedded traffic-light control

---

# 3. Objectives

## Primary objectives

- Detect vehicles from traffic video.
- Count vehicles road-wise.
- Estimate traffic density.
- Select a priority road dynamically.
- Calculate green-light duration.
- Implement emergency vehicle priority.
- Safely transition between signal states.
- Control a physical traffic-light prototype using ESP32.
- Log system data.
- Compare fixed-time and adaptive performance.

## Secondary objectives

- Provide a monitoring dashboard.
- Make thresholds configurable.
- Keep the prototype low-cost.
- Keep the system modular.
- Produce measurable experimental results.
- Make the project reproducible for the MDP team.

---

# 4. Project Scope

The first version deliberately focuses on **one 4-way intersection**.

## Included

- Python application
- OpenCV
- YOLO vehicle detection
- Vehicle tracking/counting
- Four-road traffic analysis
- Density estimation
- Adaptive signal controller
- Emergency override
- ESP32 control
- USB serial communication
- CSV logging
- Streamlit dashboard
- Automated tests
- Fixed-time baseline
- Experimental evaluation

## Not required initially

- City-wide traffic coordination
- Multiple connected intersections
- Training YOLO from scratch
- Full real-world traffic deployment
- Large-scale reinforcement learning
- Cloud infrastructure
- Production-grade emergency authentication

These can be considered future work.

---

# 5. Safety and Emergency-Vehicle Framing

The system does **not** give an emergency vehicle legal permission to ignore traffic signals or traffic rules.

The prototype demonstrates coordinated signal control:

```text
Emergency detected
       ↓
Safely terminate current phase
       ↓
Conflicting directions → RED
       ↓
Emergency direction → GREEN
       ↓
Emergency vehicle passes
       ↓
Emergency phase ends
       ↓
Adaptive control resumes
```

A real-world system would require reliable emergency identification, authenticated communication, regulatory approval, fail-safe design, and extensive safety validation.

---

# 6. System Architecture

```text
                       ┌────────────────────┐
                       │ Camera / Traffic   │
                       │ Video              │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │ YOLO Detector      │
                       │ Car / Bike / Bus   │
                       │ Truck              │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │ Tracking + IDs     │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │ Road Assignment    │
                       │ R1 / R2 / R3 / R4  │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │ Density Engine     │
                       │ LOW / MED / HIGH   │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │ Adaptive Signal    │
                       │ Controller         │
                       └─────────┬──────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
             Normal Operation          Emergency Mode
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                       ┌────────────────────┐
                       │ Python → ESP32     │
                       │ USB Serial         │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │ Traffic LEDs       │
                       │ R1 R2 R3 R4        │
                       └────────────────────┘
```

---

# 7. Technology Stack

| Component | Technology |
|---|---|
| Main language | Python |
| Computer vision | OpenCV |
| Object detection | Ultralytics YOLO |
| Numerical processing | NumPy |
| Data processing | Pandas |
| Visualization | Matplotlib |
| Dashboard | Streamlit |
| Hardware | ESP32 |
| Embedded code | Arduino C++ |
| Communication | USB Serial |
| Storage | CSV / JSON |
| Testing | pytest |
| Version control | Git / GitHub |

---

# 8. Why YOLO?

YOLO means **You Only Look Once**.

It is used for object detection and provides information such as:

- Bounding boxes
- Object classes
- Confidence scores

For this prototype, relevant classes include:

- Car
- Motorcycle
- Bus
- Truck

The initial implementation uses a **pretrained YOLO model**.

## Why pretrained?

Training a detection model from scratch would require:

- A large labelled dataset
- Data annotation
- Training infrastructure
- GPU computation
- Hyperparameter tuning

The main goal of the first prototype is to build and validate the complete traffic-control pipeline.

---

# 9. Vehicle Detection

For each video frame:

```text
Frame
 ↓
YOLO
 ↓
Detected objects
 ↓
Filter vehicle classes
 ↓
Confidence threshold
 ↓
Bounding boxes
 ↓
Vehicle centers
```

Example:

```text
Car         → Road 1
Car         → Road 1
Bus         → Road 3
Motorcycle  → Road 2
Car         → Road 1
```

Result:

```text
Road 1 = 3
Road 2 = 1
Road 3 = 1
Road 4 = 0
```

---

# 10. Vehicle Tracking and Counting

Detecting the same vehicle on every frame must not result in repeated counting.

Example:

```text
Frame 1 → Car ID 17
Frame 2 → Car ID 17
Frame 3 → Car ID 17
Frame 4 → Car ID 17
```

This represents one tracked vehicle.

Tracking helps maintain object IDs and reduce duplicate counting.

Possible issues include:

- Occlusion
- Missed detections
- Vehicles entering/leaving regions
- Poor camera angles
- False detections
- ID switches

These limitations should be considered during testing.

---

# 11. Four-Way Intersection

The prototype represents four roads:

```text
                 ROAD 1
                   ↓
                   │
                   │
ROAD 4 ────────────┼──────────── ROAD 2
                   │
                   │
                   ↑
                 ROAD 3
```

Each road has a configurable region.

Detected vehicle positions are used to determine which road they belong to.

The exact coordinates are stored in configuration rather than hard-coded throughout the program.

---

# 12. Traffic Density

The first version uses vehicle count as a simple density indicator.

Example:

```text
0–4 vehicles    → LOW
5–9 vehicles    → MEDIUM
10+ vehicles    → HIGH
```

The actual values should be configurable and tuned using project data.

### Important limitation

Vehicle count is a simplified representation of traffic density.

A more advanced system could also consider:

- Queue length
- Vehicle speed
- Road occupancy
- Arrival rate
- Lane position
- Vehicle type
- Historical traffic
- Time of day

---

# 13. Adaptive Signal Controller

The initial controller is intentionally **rule-based**.

It should:

1. Examine traffic on all roads.
2. Select a priority road.
3. Calculate green time.
4. Enforce minimum green time.
5. Enforce maximum green time.
6. Include yellow and all-red safety periods.
7. Prevent starvation of other roads.

Example:

```text
Road 1 = HIGH
Road 2 = LOW
Road 3 = MEDIUM
Road 4 = LOW
```

The controller should normally prioritize Road 1.

Conceptually:

```text
LOW     → shorter green
MEDIUM  → medium green
HIGH    → longer green
```

Do not describe the simple rule-based controller itself as machine learning.

---

# 14. Green-Time Calculation

Green duration should be bounded.

Example:

```text
Minimum green = 10 seconds
Maximum green = 40 seconds
```

A simplified controller may use traffic count to calculate a value between those limits.

The exact formula should remain configurable and should be validated experimentally.

---

# 15. Fairness and Starvation Prevention

An adaptive system must not allow one road to dominate indefinitely.

Example:

```text
Road 1 = HIGH continuously
Road 2 = MEDIUM
Road 3 = LOW
Road 4 = LOW
```

Without fairness, Road 1 could repeatedly win.

The controller should therefore consider:

- Time since a road was last served
- Maximum waiting time
- Minimum service requirements

This provides basic starvation prevention.

---

# 16. Emergency Vehicle Priority

Emergency mode temporarily overrides normal adaptive operation.

Example:

```text
Emergency detected on Road 3
          ↓
Normal scheduling paused
          ↓
Current phase safely terminated
          ↓
Conflicting roads → RED
          ↓
Road 3 → GREEN
          ↓
Emergency vehicle passes
          ↓
Emergency mode ends
          ↓
Adaptive control resumes
```

A safe transition should include appropriate yellow/all-red periods where required.

---

# 17. Emergency Detection

The initial prototype can use a software emergency input or demonstration trigger.

Possible approaches:

- Manual emergency trigger
- Camera-based emergency-vehicle detection
- Dedicated emergency communication
- Future authenticated transmitter

A simple prototype trigger should not be presented as a production-grade emergency authentication system.

---

# 18. ESP32 Role

The laptop performs computationally heavy tasks:

```text
YOLO
OpenCV
Tracking
Vehicle counting
Density calculation
Adaptive decisions
```

The ESP32 performs low-level control:

```text
Receive commands
Maintain signal state
Control LEDs
```

This separation keeps the embedded system lightweight.

---

# 19. Why ESP32?

ESP32 provides:

- Multiple GPIO pins
- Low cost
- Easy embedded development
- USB serial communication
- Wi-Fi/Bluetooth for future expansion

An Arduino Uno could also control LEDs, but ESP32 provides more flexibility for future connectivity.

---

# 20. Communication

Initial communication:

```text
Python
   │
   │ USB Serial
   ▼
 ESP32
   │
   ▼
Traffic LEDs
```

Example commands:

```text
ROAD1_GREEN
ROAD2_GREEN
ROAD3_GREEN
ROAD4_GREEN
ALL_RED
EMERGENCY_ROAD3
```

Wi-Fi/MQTT can be considered later if required.

---

# 21. Project Folder Structure

```text
ai-adaptive-traffic-signal/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── config/
│   └── config.yaml
│
├── src/
│   ├── main.py
│   ├── detector.py
│   ├── tracker.py
│   ├── road_regions.py
│   ├── counter.py
│   ├── density.py
│   ├── signal_controller.py
│   ├── emergency.py
│   ├── communication.py
│   ├── data_logger.py
│   └── visualization.py
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── results/
│
├── models/
│
├── videos/
│
├── tests/
│   ├── test_density.py
│   └── test_controller.py
│
├── esp32/
│   └── traffic_controller/
│       └── traffic_controller.ino
│
└── docs/
    ├── architecture.md
    ├── testing.md
    └── deployment.md
```

---

# 22. Module Responsibilities

### `src/main.py`

Main entry point.

- Parse command-line arguments
- Start simulation/video mode
- Connect system modules
- Run the processing loop

### `src/detector.py`

- Load YOLO
- Run inference
- Filter vehicle classes
- Apply confidence threshold
- Return detections

### `src/tracker.py`

- Maintain object IDs
- Track vehicles
- Reduce duplicate counting

### `src/road_regions.py`

- Define road regions
- Assign detections to Road 1–4

### `src/counter.py`

- Count vehicles
- Maintain road-wise counts

### `src/density.py`

- Convert counts to LOW/MEDIUM/HIGH
- Apply configurable thresholds

### `src/signal_controller.py`

- Select priority road
- Calculate green time
- Enforce min/max timing
- Maintain fairness
- Manage signal states

### `src/emergency.py`

- Receive emergency events
- Select emergency road
- Trigger safe override
- Return to adaptive control

### `src/communication.py`

- Open serial connection
- Send commands to ESP32
- Handle connection errors
- Support hardware-disabled operation

### `src/data_logger.py`

- Save counts
- Save density
- Save signal decisions
- Save emergency events
- Save results

### `src/visualization.py`

- Draw bounding boxes
- Display IDs
- Display counts
- Display signal status
- Display emergency status

### `dashboard/app.py`

Streamlit monitoring dashboard.

Possible sections:

- Current vehicle counts
- Density by road
- Current green road
- Green duration
- Emergency status
- Historical graphs
- Experiment results

---

# 23. Configuration

Project settings should be stored in:

```text
config/config.yaml
```

Example:

```yaml
model:
  path: models/yolo_model.pt
  confidence: 0.5

video:
  source: videos/traffic.mp4

roads:
  road1: ...
  road2: ...
  road3: ...
  road4: ...

density:
  low_max: 4
  medium_max: 9

signal:
  min_green: 10
  max_green: 40
  yellow: 3
  all_red: 1
  starvation_limit: 60

serial:
  enabled: false
  port: COM3
  baudrate: 115200

logging:
  enabled: true
  csv_path: data/results/traffic_log.csv
```

The exact values should be adjusted during testing.

---

# 24. Installation

## Clone

```bash
git clone https://github.com/<YOUR_USERNAME>/ai-adaptive-traffic-signal.git
cd ai-adaptive-traffic-signal
```

## Create virtual environment

Windows:

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

## Upgrade pip

```bash
python -m pip install --upgrade pip
```

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# 25. Running the Project

## Simulation mode

Useful when testing without a camera or ESP32:

```bash
python src/main.py --mode simulation
```

Simulation should generate traffic counts and demonstrate the adaptive decision process.

## Video mode

```bash
python src/main.py --mode video --source videos/traffic.mp4
```

The system should:

1. Read video.
2. Detect vehicles.
3. Track vehicles.
4. Assign vehicles to roads.
5. Calculate density.
6. Select a priority road.
7. Calculate green duration.
8. Display/log results.

## Webcam mode

If supported:

```bash
python src/main.py --mode video --source 0
```

---

# 26. YOLO Model Setup

Model weights should be placed in:

```text
models/
```

Do not automatically commit very large model files to GitHub.

Instead document:

- Model name
- Download source
- Expected filename
- Destination directory

The exact model version should be recorded in project documentation so that experiments are reproducible.

---

# 27. ESP32 Setup

## Hardware

Basic prototype:

- ESP32 development board
- Red LEDs
- Yellow LEDs
- Green LEDs
- Resistors
- Breadboard
- Jumper wires
- USB cable
- Optional physical intersection model

Each road can have:

```text
RED
YELLOW
GREEN
```

## Arduino IDE

Open:

```text
esp32/traffic_controller/traffic_controller.ino
```

Select the correct ESP32 board and COM port, then upload the firmware.

---

# 28. Hardware Signal Logic

For four roads:

```text
Road 1:
  RED
  YELLOW
  GREEN

Road 2:
  RED
  YELLOW
  GREEN

Road 3:
  RED
  YELLOW
  GREEN

Road 4:
  RED
  YELLOW
  GREEN
```

The controller must prevent conflicting directions from being green simultaneously.

---

# 29. Data Logging

Example CSV fields:

```text
timestamp
road1_count
road2_count
road3_count
road4_count
road1_density
road2_density
road3_density
road4_density
selected_road
green_duration
emergency_active
emergency_road
```

This data can be used for:

- Performance graphs
- MDP report
- Presentation
- Statistical analysis
- Fixed-time vs adaptive comparison

---

# 30. Evaluation Metrics

The project should be evaluated using measurable metrics.

## Average waiting time

```text
Average Waiting Time
=
Total Waiting Time / Number of Vehicles
```

## Queue length

Number of vehicles waiting on a road.

## Throughput

Number of vehicles successfully served during a fixed time interval.

## Emergency response time

Time between:

```text
Emergency detected
        ↓
Emergency priority safely granted
```

## Green-time utilization

How effectively each green phase is used.

---

# 31. Fixed-Time vs Adaptive Evaluation

A key experiment should compare:

```text
BASELINE
Fixed-time traffic signal

vs.

PROPOSED
Adaptive traffic signal
```

Use similar traffic input for both systems.

Record:

- Average waiting time
- Queue length
- Throughput
- Green-time utilization
- Emergency response time

Do not fabricate results.

Only report values obtained from actual experiments.

---

# 32. Suggested Experiments

## Experiment A — Balanced traffic

```text
Road 1 = 5
Road 2 = 5
Road 3 = 5
Road 4 = 5
```

Expected behavior:

- Balanced service
- No road should starve

## Experiment B — Heavy traffic

```text
Road 1 = 20
Road 2 = 3
Road 3 = 5
Road 4 = 2
```

Expected behavior:

- Road 1 receives greater priority
- Other roads eventually receive service

## Experiment C — Emergency

```text
Emergency road = Road 3
```

Expected behavior:

1. Normal operation pauses.
2. Safe transition occurs.
3. Road 3 receives priority.
4. Emergency phase ends.
5. Adaptive control resumes.

---

# 33. Testing

Run:

```bash
pytest
```

Tests should cover at least:

```text
tests/test_density.py
tests/test_controller.py
```

## Density tests

Examples:

```text
0 vehicles → LOW
5 vehicles → MEDIUM
10 vehicles → HIGH
```

The actual boundaries should match `config.yaml`.

## Controller tests

Verify:

- Green time ≥ minimum.
- Green time ≤ maximum.
- Correct priority selection.
- Starvation prevention.
- Emergency override.
- Safe signal states.
- Invalid states are rejected.

---

# 34. Error Handling

The system should provide understandable errors.

Examples:

### Missing video

Explain that the video path is invalid.

### Missing model

Explain where the model should be placed.

### ESP32 disconnected

Allow software/simulation mode if hardware is disabled.

### Serial failure

Example:

```text
Unable to open serial port.
Check the ESP32 connection and COM port.
```

### Invalid configuration

Identify the invalid parameter clearly.

---

# 35. Performance

YOLO and video processing can be computationally expensive.

Possible optimizations:

- Use a smaller YOLO model.
- Reduce input resolution.
- Process every nth frame.
- Use GPU acceleration where available.
- Avoid unnecessary image copies.
- Use efficient tracking.

The laptop handles AI processing while the ESP32 handles low-level signal control.

---

# 36. Development Strategy — Build Brick by Brick

Do not build everything at once.

## Brick 1 — Traffic Data Simulator

Create fake counts for four roads.

Goal:

```text
Road 1–4 counts
→ identify highest traffic
→ LOW/MEDIUM/HIGH
```

## Brick 2 — Traffic Data Analyzer

Use Pandas.

Goal:

- Averages
- Highest/lowest road
- Graphs

## Brick 3 — OpenCV Video Reader

Goal:

- Read video
- Display frames
- Draw road regions

## Brick 4 — YOLO Detector

Goal:

- Detect vehicles
- Draw bounding boxes
- Show confidence

## Brick 5 — Vehicle Tracking

Goal:

- Assign IDs
- Avoid duplicate counting

## Brick 6 — Four-Road Counting

Goal:

```text
R1 count
R2 count
R3 count
R4 count
```

## Brick 7 — Density Engine

```text
Count → Density
```

## Brick 8 — Adaptive Controller

```text
Density → Priority → Green duration
```

## Brick 9 — Emergency Override

```text
Emergency → Safe priority → Resume
```

## Brick 10 — ESP32 Communication

```text
Python → USB → ESP32 → LEDs
```

## Brick 11 — Full Integration

```text
Camera
→ YOLO
→ Tracking
→ Counting
→ Density
→ Controller
→ ESP32
```

## Brick 12 — Evaluation

```text
Fixed-time
vs
Adaptive
```

Collect actual measurements.

---

# 37. Recommended Learning Order

For the CSE/Data Science members:

```text
1. Python
2. Git/GitHub
3. NumPy
4. Pandas
5. Basic statistics
6. OpenCV
7. YOLO
8. Tracking/counting
9. Traffic-density estimation
10. Adaptive algorithms
11. ESP32 basics
12. Serial communication
13. Emergency logic
14. Dashboard
15. Testing
16. Experimental evaluation
17. Documentation
```

Advanced ML/optimization should come only after the rule-based system works.

---

# 38. Team Responsibilities

## CSE-DS Member 1 — Computer Vision + AI

- Python
- OpenCV
- YOLO
- Vehicle detection
- Tracking
- Counting
- Road assignment
- Density estimation

## CSE-DS Member 2 — Software + Data

- Data processing
- Adaptive algorithm support
- CSV/database
- Dashboard
- Visualization
- Experiment analysis
- Performance graphs
- Software integration

## ECM Member 1 — Embedded Hardware

- ESP32
- Arduino IDE
- LEDs
- Resistors
- Breadboard
- Traffic-light circuit
- Hardware testing

## ECM Member 2 — IoT + Integration

- Laptop–ESP32 communication
- Serial communication
- Future Wi-Fi integration
- Hardware/software integration
- Debugging

## ECE Member — Communication + Emergency

- Emergency communication concept
- Emergency detection interface
- Reliability considerations
- Communication architecture
- Emergency-priority integration

---

# 39. CSE-DS Contribution

The main CSE/Data Science contribution is:

```text
Python
  ↓
Computer Vision
  ↓
Vehicle Detection
  ↓
Vehicle Tracking
  ↓
Vehicle Counting
  ↓
Road-wise Traffic Analysis
  ↓
Density Estimation
  ↓
Adaptive Signal Decision
  ↓
Emergency Software Logic
  ↓
Data Logging
  ↓
Experimental Evaluation
```

---

# 40. Research Gap

The project should not claim that adaptive traffic signals or emergency priority are completely new.

Existing work already covers:

- Adaptive traffic control
- Computer-vision traffic monitoring
- Emergency vehicle priority
- Intelligent transportation systems

The project's practical contribution is a:

> **Low-cost integrated single-intersection prototype combining computer-vision traffic estimation, adaptive signal control, emergency priority, ESP32 hardware control, and experimental comparison with fixed-time signaling.**

The exact research gap should be refined using the team's literature review and faculty requirements.

---

# 41. Innovation

Avoid exaggerated claims.

Do not say:

```text
We invented a completely new traffic signal system.
```

Prefer:

```text
We developed a low-cost integrated prototype that combines
computer-vision-based traffic estimation, adaptive signal
control, emergency priority, and embedded traffic-light control.
```

---

# 42. Limitations

Current limitations include:

- Camera-dependent detection
- Lighting sensitivity
- Occlusion
- Camera-angle dependency
- False/missed detections
- Simplified traffic-density estimation
- Prototype-scale hardware
- Laptop-based AI processing
- Limited emergency-identification reliability
- Single-intersection scope

These should be openly discussed in the final report.

---

# 43. Future Scope

Possible future improvements:

### Multiple intersections

Coordinate several traffic signals.

### Edge AI

Move computer vision to an edge device.

### Authenticated emergency communication

Use reliable emergency transmitters rather than simple software triggers.

### Night/weather robustness

Improve performance during:

- Night
- Rain
- Fog
- Glare

### Traffic prediction

Predict traffic instead of reacting only to current conditions.

### ML optimization

After validating the rule-based system, investigate:

- Machine-learning-based optimization
- Reinforcement learning
- Traffic prediction models

### IoT

Connect intersections through a network and central dashboard.

### Real-world pilot

Test under controlled conditions with appropriate permissions and safety procedures.

---

# 44. MDP Review — 60 Second Explanation

> Our project is an AI-based adaptive traffic signal system for a single 4-way intersection. A camera provides traffic video, and a pretrained YOLO model detects vehicles. We track and count vehicles on each road and estimate traffic density. A rule-based adaptive controller selects the priority road and adjusts its green duration within safe limits. We also implement an emergency vehicle priority mode that safely stops conflicting traffic, gives priority to the emergency vehicle's direction, and then returns to adaptive operation. The laptop handles computer vision and decision-making, while an ESP32 controls the physical traffic LEDs. Finally, we compare the adaptive system with a fixed-time baseline using metrics such as waiting time, queue length, throughput, and emergency response time.

---

# 45. Common Guide Questions

### Why this project?

Fixed-time signals do not always respond to changing traffic conditions, and emergency vehicles can experience unnecessary delays.

### Why YOLO?

YOLO provides object detection with bounding boxes, classes, and confidence scores and is suitable for real-time computer-vision prototyping.

### Are you training YOLO?

Initially, no. A pretrained model is used.

### What is traffic density?

For this prototype, density is primarily represented using the number of detected vehicles in each road region.

### Is the adaptive algorithm AI?

The initial controller is rule-based. It should not be incorrectly described as machine learning.

### Why ESP32?

It is low-cost, has useful GPIO, supports serial communication, and provides future connectivity options.

### Why not run YOLO on ESP32?

YOLO inference is computationally demanding. The ESP32 is better suited to low-level signal control.

### How does emergency mode work?

The system safely transitions from normal operation, stops conflicting traffic, gives priority to the emergency direction, and then returns to adaptive control.

### How do you prove it works?

By comparing measured fixed-time and adaptive performance using actual experimental data.

---

# 46. GitHub Workflow

Useful commands:

```bash
git status
git add .
git commit -m "Add vehicle detection module"
git push
```

Suggested commits:

```text
Initial project structure
Add traffic simulation
Add OpenCV video reader
Add YOLO vehicle detection
Add vehicle tracking
Add road-wise counting
Add density engine
Add adaptive controller
Add emergency priority
Add ESP32 serial communication
Add dashboard
Add evaluation tests
Update documentation
```

---

# 47. Repository Information

## Recommended repository name

```text
ai-adaptive-traffic-signal
```

## Recommended description

```text
AI-based adaptive traffic signal prototype using computer vision, YOLO vehicle detection, traffic-density estimation, emergency vehicle priority, and ESP32 control.
```

## Suggested GitHub topics

```text
python
computer-vision
yolo
opencv
traffic-management
traffic-signal
artificial-intelligence
data-science
esp32
embedded-systems
```

---

# 48. `.gitignore`

Recommended entries:

```gitignore
.venv/
__pycache__/
*.pyc
.env
.vscode/
.idea/
*.log

data/raw/*
data/processed/*
data/results/*

videos/*
models/*
```

Large videos, datasets, generated logs, and model weights should generally not be committed directly unless there is a specific reason.

---

# 49. Reproducibility

A new team member should be able to understand:

1. What the project does.
2. Required hardware.
3. Required software.
4. Installation steps.
5. Model setup.
6. Video setup.
7. Simulation mode.
8. Video mode.
9. ESP32 setup.
10. Testing.
11. Evaluation.
12. Experiment reproduction.

Update this README whenever project setup or architecture changes.

---

# 50. Definition of Done

The first complete prototype should satisfy:

- [ ] Repository organized
- [ ] Python environment works
- [ ] Simulation works
- [ ] OpenCV video input works
- [ ] YOLO detects vehicles
- [ ] Tracking works
- [ ] Vehicles assigned to roads
- [ ] Road-wise counts produced
- [ ] Density calculated
- [ ] Adaptive controller works
- [ ] Green time respects limits
- [ ] Fairness/starvation prevention works
- [ ] Emergency override works
- [ ] Safe signal transition works
- [ ] ESP32 receives commands
- [ ] LEDs represent signal states
- [ ] Data is logged
- [ ] Dashboard works
- [ ] Tests pass
- [ ] Fixed-time baseline exists
- [ ] Adaptive comparison completed
- [ ] Experimental data recorded
- [ ] MDP documentation completed
- [ ] Final demo is reproducible

---

# 51. Final Demonstration Flow

Recommended presentation:

```text
1. Show the 4-way physical intersection
2. Start the Python application
3. Show traffic video
4. Show YOLO detections
5. Show vehicle counts
6. Show LOW/MEDIUM/HIGH density
7. Show adaptive signal decision
8. Show ESP32 LEDs changing
9. Trigger emergency event
10. Show safe emergency priority
11. End emergency phase
12. Show adaptive control resuming
13. Show logged data
14. Show fixed-time vs adaptive graphs
15. Explain limitations
16. Explain future scope
```

---

# 52. Final Architecture Summary

```text
                  AI ADAPTIVE TRAFFIC SIGNAL
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
          ▼                                       ▼
   COMPUTER VISION                         EMBEDDED CONTROL
          │                                       │
     Camera/Video                              ESP32
          │                                       │
      YOLO Detection                         Serial Commands
          │                                       │
     Tracking/Counting                       Traffic LEDs
          │
     Road Assignment
          │
    Density Estimation
          │
          ▼
   Adaptive Controller
          │
      ┌───┴────┐
      │        │
    Normal  Emergency
      │        │
      └───┬────┘
          │
          ▼
    Signal Decision
          │
          ▼
 Data Logging + Dashboard
          │
          ▼
Performance Evaluation
```

---

# 53. Expected Final Outcome

The completed prototype should demonstrate:

> **Traffic video → vehicle detection → vehicle tracking/counting → road-wise traffic density → adaptive signal decision → safe emergency override → ESP32 signal control → physical traffic LEDs → logged experimental results.**

The project should support its claims using actual measurements rather than assumptions.

---

# 54. License

Choose an appropriate open-source license before publishing.

MIT is a common option for academic software projects, but the final license should be selected according to project requirements and the licenses of third-party libraries, models, datasets, and other dependencies.

---

# 55. Acknowledgements

This is a multidisciplinary academic project involving:

- Computer Science / Data Science
- Electronics and Communication
- Electronics / Embedded Systems

All third-party libraries, pretrained models, datasets, videos, and other external resources should be credited according to their respective licenses and documentation.

---

## Project Status

**Project:** AI-Based Adaptive Traffic Signal with Emergency Vehicle Priority  
**Stage:** Prototype development  
**Scope:** Single 4-way intersection  
**Software:** Python + OpenCV + YOLO  
**Hardware:** ESP32 + traffic LEDs  
**Communication:** USB Serial  
**Evaluation:** Fixed-time vs adaptive control
