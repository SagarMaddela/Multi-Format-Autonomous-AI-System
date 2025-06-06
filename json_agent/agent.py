# # multi_agent_system/json_agent/agent.py
import os
import re
import json
import logging
from langchain.prompts import PromptTemplate
from utils.llm_utils import llm  # Import shared LLM
from memory.store import SharedMemory
import requests

os.makedirs("logs", exist_ok=True)

# Setup logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/action.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Prompt for JSON anomaly detection
json_prompt = PromptTemplate.from_template("""
You are a JSON payload anomaly detection agent.

Your task is to:
- Analyze the following JSON data
- Detect if it contains anomalies
- If yes, explain the type of anomaly and assign a confidence score (0.0 to 1.0)

Respond strictly in JSON format as:
{{
  "anomaly_detected": true/false,
  "anomaly_type": "...",
  "confidence": ...,
  "explanation": "..."
}}

JSON:
{json_data}
""")

def detect_json_anomaly(json_data: dict) -> dict:
    try:
        # Convert input to string safely and trim large payloads
        safe_json = json.dumps(json_data)[:3000]
        prompt = json_prompt.format(json_data=safe_json)

        logger.info("Sending JSON data to LLM for anomaly detection...")
        raw_response = llm.invoke(prompt)
        logger.info(f"LLM Response: {raw_response}")

        match = re.search(r"\{.*?\}", raw_response, re.DOTALL)
        if match:
            result = json.loads(match.group())

            if result.get("anomaly_detected", False):
                result["action"] = "risk_alert_triggered"
                result["status"] = "alert"
                try:
                    response = requests.post("http://localhost:9001/risk_alert", json=result, timeout=5)
                    if response.status_code != 200:
                        result["action"] = f"risk_alert_failed_status_{response.status_code}"
                except Exception as e:
                    result["action"] = "risk_alert_failed"
                    result["error"] = str(e)

            # Save result to SharedMemory
            memory = SharedMemory()
            trace_id = memory.save_trace(result)
            result["trace_id"] = trace_id
            result["agent"] = "JSONAgent"

            return result
        else:
            raise ValueError("No valid JSON in LLM response.")

    except Exception as e:
        logger.error("Anomaly detection failed.", exc_info=True)
        return {
            "anomaly_detected": False,
            "anomaly_type": "unknown",
            "confidence": 0.0,
            "explanation": "Parsing error or LLM failure.",
            "error": str(e),
            "action": "risk_alert_failed"
        }

