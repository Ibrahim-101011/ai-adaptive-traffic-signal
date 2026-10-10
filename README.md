<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>README - AI-Adaptive Traffic Signal System</title>
</head>
<body>

  <h1>🚦 AI-Based Adaptive Traffic Signal Control &amp; Digital Twin System</h1>

  <p>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python 3.10+"></a>
    <a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-4.x-green.svg" alt="OpenCV 4.x"></a>
    <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Dashboard-Streamlit-red.svg" alt="Streamlit"></a>
    <a href="https://espressif.com/"><img src="https://img.shields.io/badge/Hardware-ESP32%20Serial-orange.svg" alt="ESP32 Serial"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  </p>

  <p>A multidisciplinary engineering prototype combining <strong>Computer Vision</strong>, a <strong>Digital Twin Simulation Stream</strong>, an <strong>Adaptive Finite State Machine (FSM) Signal Controller</strong>, <strong>Emergency Vehicle Preemption</strong>, and an <strong>Interactive Operations Command Center Dashboard</strong> for an optimized 4-way intersection.</p>

  <blockquote>
    <p>
      <strong>Scope:</strong> Single 4-way intersection prototype<br>
      <strong>Simulation Engine:</strong> Procedural Digital Twin with vectorized NumPy alpha blending (60+ FPS)<br>
      <strong>Computer Vision:</strong> Ground-truth synthetic tracking / Pretrained Ultralytics YOLOv8<br>
      <strong>Controller:</strong> Rule-based FSM with PCU density estimation &amp; anti-starvation fair round-robin<br>
      <strong>Embedded Hardware:</strong> ESP32 Microcontroller + 12-channel LED traffic array<br>
      <strong>Dashboard:</strong> Dark-themed Streamlit Live Telemetry Command Center<br>
      <strong>Baseline Benchmark:</strong> Fixed-time vs. Adaptive control performance evaluation
    </p>
  </blockquote>

  <hr>

  <h2>Table of Contents</h2>
  <ol>
    <li><a href="#overview">Project Overview</a></li>
    <li><a href="#problem-statement">Problem Statement</a></li>
    <li><a href="#system-architecture">System Architecture</a></li>
    <li><a href="#tech-stack">Hardware &amp; Software Stack</a></li>
    <li><a href="#simulation-mechanics">Digital Twin &amp; Simulation Mechanics</a></li>
    <li><a href="#pcu-density">Traffic Density &amp; PCU Formulation</a></li>
    <li><a href="#controller-logic">Adaptive Signal Controller Logic</a></li>
    <li><a href="#emergency-priority">Emergency Vehicle Priority</a></li>
    <li><a href="#esp32-integration">ESP32 Embedded Integration</a></li>
    <li><a href="#repo-structure">Repository Structure</a></li>
    <li><a href="#installation">Installation &amp; Setup</a></li>
    <li><a href="#running">Running the System</a></li>
    <li><a href="#controls">Interactive Controls</a></li>
    <li><a href="#dashboard">Streamlit Operations Dashboard</a></li>
    <li><a href="#evaluation">Evaluation Metrics &amp; Comparative Testing</a></li>
    <li><a href="#roles">Academic &amp; Team Roles (MDP)</a></li>
    <li><a href="#roadmap">Limitations &amp; Future Roadmap</a></li>
    <li><a href="#license">License</a></li>
  </ol>

  <hr>

  <h2 id="overview">1. Project Overview</h2>
  <p>Traditional traffic lights operate on rigid, fixed-time schedules regardless of instantaneous flow, resulting in empty green phases and heavy congestion buildup on opposing lanes.</p>
  <p>This project delivers an end-to-end intelligent traffic system that:</p>
  <ol>
    <li>Simulates realistic intersection physics and vehicle flows in a real-time <strong>Digital Twin</strong> (or ingests live RTSP camera feeds).</li>
    <li>Tracks vehicles across designated road approach polygons.</li>
    <li>Computes Passenger Car Unit (PCU) weighted density dynamically.</li>
    <li>Computes dynamic green times bounded by safety limits.</li>
    <li>Prevents lane starvation using historical fairness counters.</li>
    <li>Provides fail-safe emergency preemption (e.g., ambulances).</li>
    <li>Transmits signal phase states over USB Serial to an ESP32 controlling physical signal LEDs.</li>
    <li>Logs real-time metrics to disk and visualizes live intersection dynamics on a Streamlit dashboard.</li>
  </ol>

  <pre><code>Synthetic SimStream / RTSP Video Feed
                ↓
    Vehicle Tracking &amp; Detection
                ↓
   Road Region Polygon Assignment
                ↓
     PCU Density Calculation
                ↓
  FSM Adaptive Controller (Normal vs. Emergency)
                ↓
   ┌────────────────────────┬────────────────────────┐
   ▼                        ▼                        ▼
OpenCV Display         Streamlit TOC        ESP32 Serial Bus
(HUD Diagnostics)      (Live Telemetry)     (Traffic LEDs)</code></pre>

  <hr>

  <h2 id="problem-statement">2. Problem Statement</h2>
  <p>Fixed-time controllers assign static cycle splits regardless of actual queue demands.</p>
  <p>Consider a scenario:</p>
  <ul>
    <li><strong>Road 1 (North):</strong> 22 vehicles (Heavy queue)</li>
    <li><strong>Road 2 (East):</strong> 2 vehicles (Sparse)</li>
    <li><strong>Road 3 (South):</strong> 8 vehicles (Moderate)</li>
    <li><strong>Road 4 (West):</strong> 0 vehicles (Completely empty)</li>
  </ul>
  <p>Under a fixed-time schedule, Road 4 still receives a full green interval, forcing Road 1 to sit idle. In contrast, this adaptive system detects empty queues, truncates green cycles immediately, allocates extended green windows to Road 1, and clears waiting emergency units without manual intervention.</p>

  <hr>

  <h2 id="system-architecture">3. System Architecture</h2>
  <pre><code>       ┌────────────────────────┐         ┌────────────────────────┐
       │ Synthetic SimStream    │   OR    │ Live RTSP / Video Feed │
       │ (Ground-Truth BBoxes)  │         │ (YOLOv8 + ByteTrack)   │
       └───────────┬────────────┘         └───────────┬────────────┘
                   │                                  │
                   └─────────────────┬────────────────┘
                                     ▼
                       ┌───────────────────────────┐
                       │ Road Region Polygon Masks │
                       │   (North, East, South, W) │
                       └─────────────┬─────────────┘
                                     ▼
                       ┌───────────────────────────┐
                       │ Class-Weighted PCU Engine │
                       └─────────────┬─────────────┘
                                     ▼
                       ┌───────────────────────────┐
                       │  Adaptive FSM Controller  │
                       │ ┌───────────────────────┐ │
                       │ │ Normal Adaptive Mode  │ │
                       │ │ Fixed Round-Robin     │ │
                       │ │ Emergency Preemption  │ │
                       │ └───────────────────────┘ │
                       └─────────────┬─────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
┌────────────────────┐   ┌──────────────────────┐   ┌────────────────────┐
│ OpenCV Heads-Up    │   │ CSV Telemetry Stream │   │ ESP32 Hardware     │
│ Diagnostic Display │   │ (Non-blocking I/O)   │   │ UART Serial Bus    │
└────────────────────┘   └──────────┬───────────┘   └──────────┬─────────┘
                                    ▼                          ▼
                         ┌──────────────────────┐   ┌────────────────────┐
                         │ Streamlit Operations │   │ Physical Solid     │
                         │ Command Center (TOC) │   │ State Signal LEDs  │
                         └──────────────────────┘   └────────────────────┘</code></pre>

  <hr>

  <h2 id="tech-stack">4. Hardware &amp; Software Stack</h2>
  <table border="1" cellpadding="8" cellspacing="0">
    <thead>
      <tr>
        <th>Layer</th>
        <th>Component / Tech</th>
        <th>Purpose</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Core Runtime</strong></td>
        <td>Python 3.10+</td>
        <td>Orchestration and pipeline execution</td>
      </tr>
      <tr>
        <td><strong>Vision &amp; UI</strong></td>
        <td>OpenCV 4.x</td>
        <td>Video processing, graphics rendering, HUD overlay</td>
      </tr>
      <tr>
        <td><strong>Detection</strong></td>
        <td>Ultralytics YOLOv8 / SimStream</td>
        <td>Real-world vehicle detection / Ground-truth simulation</td>
      </tr>
      <tr>
        <td><strong>Data Engine</strong></td>
        <td>NumPy &amp; Pandas</td>
        <td>Vectorized blitting, mathematical calculations, CSV logs</td>
      </tr>
      <tr>
        <td><strong>Dashboard</strong></td>
        <td>Streamlit + Plotly Dark</td>
        <td>Real-time web-based operations control center</td>
      </tr>
      <tr>
        <td><strong>Embedded MCU</strong></td>
        <td>ESP32 NodeMCU / DevKit v1</td>
        <td>Low-level relay and LED signal execution</td>
      </tr>
      <tr>
        <td><strong>Firmware</strong></td>
        <td>Arduino C++</td>
        <td>Microcontroller state machine and fail-safe watchdog</td>
      </tr>
      <tr>
        <td><strong>Bus Protocol</strong></td>
        <td>USB UART Serial (115200 baud)</td>
        <td>Inter-process edge communication</td>
      </tr>
      <tr>
        <td><strong>Testing</strong></td>
        <td>pytest</td>
        <td>Automated unit testing for FSM and density modules</td>
      </tr>
    </tbody>
  </table>

  <hr>

  <h2 id="simulation-mechanics">5. Digital Twin &amp; Simulation Mechanics</h2>
  <p>The digital twin (<code>src/sim_feed.py</code>) provides an 800×800 coordinate simulation environment:</p>
  <ul>
    <li><strong>Procedural Vehicle Sprites:</strong> Dynamic top-down rendering of sedans, taxis, motorcycles, city buses, and heavy trucks with rotating wheels, glass surfaces, and headlights.</li>
    <li><strong>Vectorized NumPy Blitting:</strong> Uses bounded sub-array slicing for alpha-compositing, bypassing nested Python loops to maintain consistent 60+ FPS.</li>
    <li><strong>Accurate Queue Dynamics:</strong> Vehicles calculate distance to the white stop line and decelerate smoothly to within 6–8 pixels of the line.</li>
    <li><strong>Queue Take-Off Logic:</strong> When lights turn green, cars accelerate without accordion delays.</li>
    <li><strong>3-Aspect Active Signal Heads:</strong> Physical traffic housings with LED illumination and outer glow rings reflect state transitions at each corner.</li>
  </ul>

  <hr>

  <h2 id="pcu-density">6. Traffic Density &amp; PCU Formulation</h2>
  <p>Raw vehicle counts do not accurately reflect road occupancy. A bus occupies significantly more road space and moves slower than a motorcycle.</p>
  <p>The system uses <strong>Passenger Car Unit (PCU)</strong> equivalents:</p>
  <p><code>PCU_total = Σ (N_class × W_class)</code></p>
  <table border="1" cellpadding="8" cellspacing="0">
    <thead>
      <tr>
        <th>Vehicle Class</th>
        <th>Multiplier (W)</th>
        <th>Description</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Car / Taxi</strong></td>
        <td><code>1.0</code></td>
        <td>Baseline passenger vehicle</td>
      </tr>
      <tr>
        <td><strong>Motorcycle</strong></td>
        <td><code>0.5</code></td>
        <td>Compact footprint, agile filter capacity</td>
      </tr>
      <tr>
        <td><strong>Bus</strong></td>
        <td><code>2.5</code></td>
        <td>Large footprint, slow acceleration profile</td>
      </tr>
      <tr>
        <td><strong>Truck</strong></td>
        <td><code>2.5</code></td>
        <td>Heavy cargo carrier, large stopping distance</td>
      </tr>
    </tbody>
  </table>

  <hr>

  <h2 id="controller-logic">7. Adaptive Signal Controller Logic</h2>
  <p>Implemented as a Finite State Machine (<code>src/signal_controller.py</code>) managing states: <code>GREEN</code>, <code>YELLOW</code>, and <code>ALL_RED</code>.</p>

  <h3>A. Dynamic Green Calculation</h3>
  <p><code>Duration_green = min(MaxGreen, max(MinGreen, MinGreen + (PCU × 2.0)))</code></p>
  <ul>
    <li><code>MinGreen</code>: 5 seconds (ensures pedestrian and clearing safety)</li>
    <li><code>MaxGreen</code>: 20–40 seconds (prevents cross-traffic stagnation)</li>
    <li><code>YellowDuration</code>: 2.0 seconds (clearance phase)</li>
    <li><code>AllRedDuration</code>: 1.0 second (intersection clearance before next green)</li>
  </ul>

  <h3>B. Early Cutoff (Zero-Queue Discharge)</h3>
  <p>In <code>ADAPTIVE</code> mode, if the approach's queue empties (<code>PCU &lt;= 0.0</code>), the green timer cuts off early and immediately transitions to Yellow, saving cycle time.</p>

  <h3>C. Starvation Prevention Engine</h3>
  <p>If a low-traffic lane waits through several cycles, its starvation counter increases. Once this exceeds <code>starvation_threshold</code> (default: 3), that road receives forced priority on the next cycle, ensuring fairness.</p>

  <h3>D. Deterministic Fixed Mode</h3>
  <p>When toggled to <code>FIXED</code>, the controller switches to a strict round-robin sequence (Road 1 → Road 2 → Road 3 → Road 4) running the full green duration (<code>10s</code>) without early cutoffs.</p>

  <hr>

  <h2 id="emergency-priority">8. Emergency Vehicle Priority</h2>
  <p>When an emergency vehicle (ambulance, fire truck) is flagged on any approach:</p>
  <ol>
    <li>Normal adaptive logic is immediately preempted.</li>
    <li>Conflicting movements transition safely through Yellow to All-Red.</li>
    <li>The target emergency lane receives an immediate <code>GREEN</code> phase.</li>
    <li>After clearance or manual release, the system safely transitions back to adaptive operation.</li>
  </ol>

  <pre><code>Emergency Triggered
         ↓
Current Phase Safely Terminated (Yellow Clearance)
         ↓
All Conflicting Lanes → RED
         ↓
Emergency Approach → GREEN (Preempt Phase)
         ↓
Clearance Timeout / Trigger Released
         ↓
Safe All-Red Transition
         ↓
Resume Adaptive Control</code></pre>

  <hr>

  <h2 id="esp32-integration">9. ESP32 Embedded Integration</h2>
  <p>The edge PC communicates with an ESP32 driving a physical LED model.</p>
  <pre><code>Laptop (Python) ──[USB Serial / UART @ 115200 baud]──&gt; ESP32 ──&gt; Relays / LEDs</code></pre>

  <h3>JSON Serial Command Format</h3>
  <pre><code>{"road": "road1", "state": "GREEN", "duration": 14}</code></pre>

  <h3>Pin Mapping (Example ESP32 Configuration)</h3>
  <pre><code>// Road 1 (North)
#define R1_RED    23
#define R1_YELLOW 22
#define R1_GREEN  21

// Road 2 (East)
#define R2_RED    19
#define R2_YELLOW 18
#define R2_GREEN  5

// Road 3 (South)
#define R3_RED    17
#define R3_YELLOW 16
#define R3_GREEN  4

// Road 4 (West)
#define R4_RED    0
#define R4_YELLOW 2
#define R4_GREEN  15</code></pre>

  <hr>

  <h2 id="repo-structure">10. Repository Structure</h2>
  <pre><code>ai-adaptive-traffic-signal/
├── run_system.bat                 # Master launcher script
├── requirements.txt               # Python package dependencies
├── README.md                      # Comprehensive documentation
│
├── config/                        # Intersection geometry and configuration
│   └── config.yaml
│
├── dashboard/                     # Web-based operations monitoring
│   └── app.py                     # Streamlit Traffic Operations Command Center (TOC)
│
├── data/                          # Data storage
│   └── processed/                 # Streamed operational metrics
│       └── traffic_telemetry.csv
│
├── esp32/                         # Microcontroller firmware
│   └── traffic_controller.ino     # Arduino C++ relay driver &amp; fail-safe watchdog
│
├── models/                        # Deep learning weights (for real video feeds)
│   └── yolov8n.pt
│
├── src/                           # Core application logic
│   ├── counter.py                 # Approach polygon vehicle tracking and counting
│   ├── density.py                 # PCU priority calculation engine
│   ├── emergency.py               # Emergency preemption management
│   ├── main.py                    # Pipeline orchestrator, HUD, and I/O loop
│   ├── road_regions.py            # Coordinate mapper for 4-way approach zones
│   ├── signal_controller.py       # Adaptive &amp; Fixed FSM signal state controller
│   └── sim_feed.py                # Procedural digital twin simulation engine
│
├── tests/                         # Unit tests
│   ├── test_density.py
│   └── test_controller.py
│
└── videos/                        # Recorded test footage for camera validation</code></pre>

  <hr>

  <h2 id="installation">11. Installation &amp; Setup</h2>
  <h3>Prerequisites</h3>
  <ul>
    <li>Windows 10/11, Ubuntu 22.04+, or macOS</li>
    <li>Python <code>3.10</code> or higher (verified with virtual environment)</li>
    <li>(Optional) ESP32 Dev Board + LEDs and resistors</li>
  </ul>

  <h3>Setup Instructions</h3>
  <pre><code># 1. Clone repository
git clone https://github.com/&lt;YOUR_USERNAME&gt;/ai-adaptive-traffic-signal.git
cd ai-adaptive-traffic-signal

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt</code></pre>

  <hr>

  <h2 id="running">12. Running the System</h2>
  <h3>One-Click Launch (Windows)</h3>
  <p>Run the master batch controller to launch both the simulation and the dashboard concurrently:</p>
  <pre><code>.\run_system.bat</code></pre>
  <p>This script handles:</p>
  <ol>
    <li>Environment validation (<code>.venv</code>).</li>
    <li>Telemetry directory initialization (<code>data/processed</code>).</li>
    <li>Spawning the <strong>Digital Twin Simulation Window</strong>.</li>
    <li>Launching the <strong>Streamlit Command Center</strong> in your default web browser.</li>
  </ol>

  <h3>Manual Execution</h3>
  <p>If launching services individually across multiple terminals:</p>
  <p><strong>Terminal 1 (Simulation Engine):</strong></p>
  <pre><code>python -u src/main.py</code></pre>
  <p><strong>Terminal 2 (Telemetry Dashboard):</strong></p>
  <pre><code>streamlit run dashboard/app.py</code></pre>

  <hr>

  <h2 id="controls">13. Interactive Controls</h2>
  <p>While focused inside the OpenCV simulation display window:</p>
  <table border="1" cellpadding="8" cellspacing="0">
    <thead>
      <tr>
        <th>Key</th>
        <th>Action</th>
        <th>Behavior</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>1</code></td>
        <td><strong>Emergency Road 1</strong></td>
        <td>Preempts cycle; grants immediate Green to North approach.</td>
      </tr>
      <tr>
        <td><code>2</code></td>
        <td><strong>Emergency Road 2</strong></td>
        <td>Preempts cycle; grants immediate Green to East approach.</td>
      </tr>
      <tr>
        <td><code>3</code></td>
        <td><strong>Emergency Road 3</strong></td>
        <td>Preempts cycle; grants immediate Green to South approach.</td>
      </tr>
      <tr>
        <td><code>4</code></td>
        <td><strong>Emergency Road 4</strong></td>
        <td>Preempts cycle; grants immediate Green to West approach.</td>
      </tr>
      <tr>
        <td><code>C</code></td>
        <td><strong>Clear Emergency</strong></td>
        <td>Clears override and returns smoothly to adaptive cycles.</td>
      </tr>
      <tr>
        <td><code>M</code></td>
        <td><strong>Toggle Mode</strong></td>
        <td>Toggles between <code>ADAPTIVE</code> (dynamic PCU) and <code>FIXED</code> (round-robin).</td>
      </tr>
      <tr>
        <td><code>Q</code> / <code>ESC</code></td>
        <td><strong>Quit</strong></td>
        <td>Cleanly terminates simulation processes and releases windows.</td>
      </tr>
    </tbody>
  </table>

  <hr>

  <h2 id="dashboard">14. Streamlit Operations Dashboard</h2>
  <p>The dashboard (<code>dashboard/app.py</code>) provides real-time visibility into intersection state:</p>
  <ul>
    <li><strong>Phase Approach Cards:</strong> Illuminated Red, Yellow, and Green bulbs with outer glows matching the OpenCV simulation.</li>
    <li><strong>KPI Metrics:</strong> Active Phase Approach, Countdown Timer, Intersection Density (PCU), and Total Queued Units.</li>
    <li><strong>PCU Congestion Timeline:</strong> Multi-approach line charts tracking historical queuing trends.</li>
    <li><strong>Current Load Distribution:</strong> Real-time donut chart displaying relative load per approach.</li>
    <li><strong>Raw Telemetry Stream:</strong> Historical event logs written to disk at 1 Hz.</li>
  </ul>

  <hr>

  <h2 id="evaluation">15. Evaluation Metrics &amp; Comparative Testing</h2>
  <p>The system evaluates traffic performance using four key metrics:</p>
  <ol>
    <li><strong>Average Delay / Wait Time:</strong> Time vehicles spend idling at red signals before clearing the intersection.</li>
    <li><strong>Queue Discharge Rate:</strong> Time required to fully clear an approach queue upon receiving green.</li>
    <li><strong>Starvation Rate:</strong> Maximum consecutive cycles an approach waits without green service.</li>
    <li><strong>Emergency Response Latency:</strong> Time elapsed from emergency flag activation to active green clearance.</li>
  </ol>

  <h3>Running Comparative Tests</h3>
  <pre><code>pytest tests/</code></pre>

  <hr>

  <h2 id="roles">16. Academic &amp; Team Roles (MDP)</h2>
  <p>This project spans multiple engineering disciplines:</p>
  <ul>
    <li><strong>Computer Science &amp; Data Science:</strong> Computer vision integration, vehicle tracking, PCU algorithms, state machine logic, Streamlit UI, and data analysis.</li>
    <li><strong>Electronics &amp; Embedded Systems:</strong> ESP32 firmware, relay drivers, breadboard LED arrays, and UART communication.</li>
    <li><strong>Communication &amp; Systems Engineering:</strong> Emergency override protocols, safety fail-safes, and system integration.</li>
  </ul>

  <hr>

  <h2 id="roadmap">17. Limitations &amp; Future Roadmap</h2>
  <h3>Current Limitations</h3>
  <ul>
    <li>Detection accuracy in real-world camera feeds is subject to lighting, weather, and camera angle variations.</li>
    <li>Physical scale is currently validated on an embedded desktop prototype.</li>
  </ul>

  <h3>Future Roadmap</h3>
  <ul>
    <li><strong>Edge Deployment:</strong> Porting deep learning inference to NVIDIA Jetson hardware with TensorRT optimization.</li>
    <li><strong>Corridor Coordination:</strong> Linking adjacent intersections using MQTT/green-wave progression algorithms.</li>
    <li><strong>V2X Communication:</strong> Integrating wireless emergency preemption via authenticated DSRC or cellular V2X protocols.</li>
  </ul>

  <hr>

  <h2 id="license">18. License</h2>
  <p>Distributed under the <strong>MIT License</strong>. See <code>LICENSE</code> for details.</p>

</body>
</html>