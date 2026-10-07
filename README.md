<div align="center">

# 🚦 AI-Based Adaptive Traffic Signal with Emergency Vehicle Priority
### A Multidisciplinary Engineering Prototype for Dynamic Intersection Management

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF?style=for-the-badge&logo=yolo&logoColor=black)](https://github.com/ultralytics/ultralytics)
[![ESP32](https://img.shields.io/badge/Hardware-ESP32%20DevKit-E7352C?style=for-the-badge&logo=espressif&logoColor=white)](https://www.espressif.com/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<p align="center">
  <b>Computer Vision • Object Tracking • Rule-Based Adaptive FSM • Hardware-in-the-Loop Preemption</b>
</p>

[Explore Architecture](#-system-architecture) •
[Hardware Setup](#-hardware-integration--wiring) •
[Installation](#-quick-start-windows) •
[MDP Documentation](#-mdp-review-documentation)

</div>

---

## 📌 Executive Summary

Traditional fixed-time traffic control systems operate on static, pre-programmed timing splits irrespective of real-time demand. This causes unnecessary idling on empty roads, increases carbon emissions, and delays critical emergency response vehicles.

This project delivers a **runnable, hardware-in-the-loop (HIL) prototype** of an **intelligent four-way intersection controller**. By combining real-time edge computer vision (`YOLOv8n` + spatial tracking) with a deterministic, starvation-free **Finite State Machine (FSM)**, the system dynamically scales green allocations based on actual vehicle density and provides zero-latency, safety-interlocked emergency vehicle preemption reflected on physical ESP32-driven LED traffic heads.

---

## 🚀 Key Features

* **Real-Time Multi-Class Vehicle Detection:** Detects cars, motorcycles, buses, and trucks using `YOLOv8n` optimized for low-latency CPU inference.
* **Spatial Road Tracking & Deduplication:** Associates detections with persistent IDs across frames, isolating vehicles into four configurable quadrant polygons (`North`, `East`, `South`, `West`).
* **Weighted Traffic Density Scoring:** Converts raw vehicle counts into Passenger Car Equivalents (PCE) to weight heavy vehicles (buses/trucks) higher than light vehicles (motorcycles).
* **Deterministic Adaptive FSM Controller:** Calculates dynamic green intervals ($T_{\text{min}} \le T_{\text{green}} \le T_{\text{max}}$) with embedded anti-starvation mechanics.
* **Safe Emergency Vehicle Preemption:** Implements non-instantaneous preemption that safely forces clearance intervals (`Yellow` $\rightarrow$ `All-Red`) prior to routing priority greens.
* **Bi-Directional Serial Framing:** Transmits ASCII framed tokens (`<R1_G>`, `<ALL_RED>`) over USB Serial with hardware watchdog timeouts.
* **Live Telemetry Dashboard:** Streamlit-powered dashboard streaming real-time queue lengths, historical throughput, and phase distributions.

---

## 📐 System Architecture
