import json
import numpy as np


def load_ops_data():
    with open("data/mock_ops_logs.json", "r") as f:
        return json.load(f)


def calculate_baseline(records):
    baseline_slice = records[:2]
    return {
        "avg_execution_time": float(np.mean([r["execution_time_sec"] for r in baseline_slice])),
        "avg_cost": float(np.mean([r["cost_usd"] for r in baseline_slice]))
    }


def calculate_current(records):
    latest = records[-1]
    return {
        "execution_time_sec": latest["execution_time_sec"],
        "cost_usd": latest["cost_usd"],
        "failures": latest["failures"],
        "maintenance": latest["maintenance"]
    }


def compute_drift(baseline, current):
    return {
        "execution_time_drift_pct": round(
            (current["execution_time_sec"] - baseline["avg_execution_time"])
            / baseline["avg_execution_time"] * 100, 2
        ),
        "cost_drift_pct": round(
            (current["cost_usd"] - baseline["avg_cost"])
            / baseline["avg_cost"] * 100, 2
        )
    }
