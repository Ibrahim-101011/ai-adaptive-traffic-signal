import sys
import os

# Add src/ to path so imports work cleanly
sys.path.insert(0, os.path.abspath("src"))

from density import TrafficDensityEstimator

def test_density_classification_thresholds():
    estimator = TrafficDensityEstimator(low_max=3, medium_max=8)
    assert estimator.estimate_density(2) == "LOW"
    assert estimator.estimate_density(3) == "LOW"
    assert estimator.estimate_density(5) == "MEDIUM"
    assert estimator.estimate_density(8) == "MEDIUM"
    assert estimator.estimate_density(9) == "HIGH"

def test_priority_score_weighted_calculation():
    estimator = TrafficDensityEstimator()
    # 2 cars (2.0) + 2 motorcycles (1.0) + 1 bus (2.5) + 1 truck (2.5) = 8.0
    breakdown = {"cars": 2, "motorcycles": 2, "buses": 1, "trucks": 1}
    assert estimator.compute_priority_score(breakdown) == 8.0