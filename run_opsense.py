import json
from ops_agents.agent_loop import run_agent
from tools.ops_tools import (
    load_ops_data,
    calculate_baseline,
    calculate_current,
    compute_drift
)

# Load operational data
records = load_ops_data()
baseline = calculate_baseline(records)
current = calculate_current(records)

# ---- TOOL REGISTRATION (REAL AGENTKIT) ----

tools = [
    {
        "type": "function",
        "name": "compute_drift",
        "description": "Compute execution time and cost drift percentages",
        "parameters": {
            "type": "object",
            "properties": {
                "baseline": {"type": "object"},
                "current": {"type": "object"}
            },
            "required": ["baseline", "current"]
        }
    }
]

tool_functions = {
    "compute_drift": compute_drift
}

# ---- AGENT INPUT ----

context = f"""
Operational records:
{json.dumps(records, indent=2)}

Baseline metrics:
{json.dumps(baseline, indent=2)}

Current metrics:
{json.dumps(current, indent=2)}

Analyze for operational drift, estimate impact,
and produce an optimization report.
"""

# ---- RUN AGENT ----

result = run_agent(context, tools, tool_functions)

print("\n=== OPSENSE OPERATIONAL DRIFT REPORT ===\n")
print(result)
