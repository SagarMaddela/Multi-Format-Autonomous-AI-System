# multi_agent_system/router/action_router.py

import requests
from datetime import datetime
from memory.store import SharedMemory


class ActionRouter:
    def __init__(self):
        self.memory = SharedMemory()

    def route(self, agent_output: dict):
        trace_id = agent_output.get("trace_id")
        action = None
        target_url = None
        payload = agent_output

        # EMAIL → CRM Escalation
        if agent_output.get("agent") == "EmailAgent":
            tone = agent_output.get("tone")
            urgency = agent_output.get("urgency")
            if tone in ["angry", "threatening"] or urgency == "high":
                action = "escalate"
                target_url = "http://localhost:9000/crm/escalate"

        # JSON → Risk Alert (already triggered inside JSONAgent, can simulate again)
        elif agent_output.get("agent") == "JSONAgent" and agent_output.get("status") == "alert":
            action = "risk_alert"
            target_url = "http://localhost:9001/risk_alert"

        # PDF → Compliance flag
        elif agent_output.get("agent") == "PDFAgent":
            if any("invoice" in flag.get("flag", "").lower() for flag in agent_output.get("flags", [])):
                action = "invoice_flag"
                target_url = "http://localhost:9002/invoice/flag"

        # If an action is needed, simulate a REST call
        action_result = {"status": "no_action_triggered"}

        if target_url:
            try:
                response = requests.post(target_url, json=payload)
                action_result = {
                    "action_triggered": action,
                    "target_url": target_url,
                    "status_code": response.status_code,
                    "trace_id": trace_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                action_result = {
                    "action_triggered": action,
                    "target_url": target_url,
                    "error": str(e),
                    "trace_id": trace_id,
                    "timestamp": datetime.utcnow().isoformat()
                }

        # Save to memory
        self.memory.save_trace(action_result)
        return action_result
