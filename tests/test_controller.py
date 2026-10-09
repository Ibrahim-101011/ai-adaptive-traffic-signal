import sys
import os

sys.path.insert(0, os.path.abspath("src"))

from signal_controller import AdaptiveSignalController
from emergency import EmergencyManager

CONFIG = {
    "signal_timing": {
        "min_green": 10,
        "max_green": 45,
        "yellow_duration": 3,
        "all_red_duration": 2,
        "starvation_threshold": 3,
        "fixed_time_duration": 20
    }
}

def test_green_time_scaling():
    ctrl = AdaptiveSignalController(CONFIG)
    assert ctrl.calculate_green_time(1.0) == 10
    assert ctrl.calculate_green_time(2.0) == 10
    assert ctrl.calculate_green_time(20.0) == 45
    assert ctrl.calculate_green_time(11.0) == 28

def test_safe_transition_to_yellow_and_red():
    ctrl = AdaptiveSignalController(CONFIG)
    em = EmergencyManager()
    scores = {"road1": 2.0, "road2": 2.0, "road3": 2.0, "road4": 2.0}

    # Step past green duration (10s)
    status = ctrl.step(10.1, scores, em)
    assert status["state"] == "YELLOW"

    # Step past yellow duration (3s)
    status = ctrl.step(3.1, scores, em)
    assert status["state"] == "ALL_RED"

def test_emergency_preemption_lifecycle():
    ctrl = AdaptiveSignalController(CONFIG)
    em = EmergencyManager(default_duration=15)
    scores = {"road1": 0.0, "road2": 0.0, "road3": 0.0, "road4": 0.0}

    # Active road starts on road1
    assert ctrl.active_road == "road1"

    # Trigger emergency on road3
    em.trigger_emergency("road3", duration=15)
    
    # Must cycle through yellow, then all-red, before giving green to road3
    status = ctrl.step(0.1, scores, em)
    assert status["state"] == "YELLOW"

    status = ctrl.step(3.1, scores, em)
    assert status["state"] == "ALL_RED"

    status = ctrl.step(2.1, scores, em)
    assert status["state"] == "GREEN"
    assert status["active_road"] == "road3"
    assert status["mode"] == "EMERGENCY"