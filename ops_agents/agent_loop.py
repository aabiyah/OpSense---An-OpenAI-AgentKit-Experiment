from openai import OpenAI, RateLimitError
import json
import time

client = OpenAI()

SYSTEM_PROMPT = """
You are OPSENSE, an autonomous operations optimization agent.

Your responsibilities:
- Analyze operational data
- Detect operational drift
- Use tools if needed
- Produce a clear FINAL operational drift report

Rules:
- Use tools only if they add value
- Once tools have been used, you MUST produce a final report
- Do not ask follow-up questions
"""

FINAL_PROMPT = """
Using all information gathered so far, produce the FINAL operational drift report.

The report MUST include:
- Whether drift exists
- Key evidence
- Estimated impact
- 2–3 concrete recommendations
- Confidence level

Do not call tools. Do not continue reasoning. Final answer only.
"""

def run_agent(context, tools, tool_functions):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": context}
    ]

    tool_used = False

    # ---------- PHASE 1: TOOL-AWARE REASONING ----------
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=messages,
            tools=tools
        )
    except RateLimitError:
        print("⏳ Rate limit hit. Waiting 20 seconds...")
        time.sleep(20)
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=messages,
            tools=tools
        )

    output = response.output[0]

    # ---------- TOOL CALL ----------
    if output.type == "tool_call":
        tool_used = True
        tool_name = output.name
        arguments = json.loads(output.arguments)

        print(f"[TOOL CALL] {tool_name}({arguments})")

        result = tool_functions[tool_name](**arguments)

        messages.append({
            "role": "tool",
            "tool_name": tool_name,
            "content": json.dumps(result)
        })

    elif output.type == "message":
        # Agent decided it didn't need tools
        if output.content and output.content[0].text.strip():
            return output.content[0].text

    # ---------- PHASE 2: FORCED FINALIZATION ----------
    messages.append({"role": "user", "content": FINAL_PROMPT})

    try:
        final_response = client.responses.create(
            model="gpt-4.1-mini",
            input=messages,
            tools=[] # No tools allowed in finalization phase
        )
    except RateLimitError:
        print("⏳ Rate limit hit during finalization. Waiting 20 seconds...")
        time.sleep(20)
        final_response = client.responses.create(
            model="gpt-4.1-mini",
            input=messages,
            tools=[]
        )

    final_output = final_response.output[0]

    if final_output.type == "message" and final_output.content:
        return final_output.content[0].text

    return "Agent failed to produce a final report."
