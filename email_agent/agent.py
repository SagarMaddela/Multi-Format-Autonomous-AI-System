# # multi_agent_system/email_agent/agent.py
import os
import re
import json
import logging
from langchain.prompts import PromptTemplate
from utils.llm_utils import llm  # importing only the LLM
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

# Email classification prompt
email_prompt = PromptTemplate.from_template("""
You are a customer support email analysis agent.

Given the following email, classify:
- urgency: low / medium / high
- type: issue / request / feedback / complaint / other
- tone: polite / neutral / angry / frustrated / appreciative / sarcastic / formal / informal / other
- trigger_action: true if tone is negative AND urgency is high, otherwise false

Return response in strict JSON:
{{
  "urgency": "...",
  "type": "...",
  "tone": "...",
  "trigger_action": ...
}}

Email:
{email}
""")

def take_action(result: dict):
    """
    If trigger_action is True, escalate to CRM.
    Otherwise, return 'logged'.
    """
    if result.get("trigger_action", False):
        try:
            response = requests.post(
                "http://localhost:9000/crm/escalate",
                json=result,
                timeout=5
            )
            if response.status_code == 200:
                return "escalated"
            else:
                return f"crm_error_{response.status_code}"
        except requests.RequestException as e:
            return f"crm_unavailable: {e}"
    else:
        return "logged"
    
def analyze_email(email: str) -> dict:
    try:
        prompt = email_prompt.format(email=email[:2000])
        logger.info("Sending prompt to LLM...")

        raw_response = llm.invoke(prompt)
        logger.info(f"LLM Response: {raw_response}")

        match = re.search(r"\{.*?\}", raw_response, re.DOTALL)
        if match:
            result = json.loads(match.group())
            action = take_action(result)
            result["action"] = action
            result["agent"] = "EmailAgent"
            # Save to SharedMemory
            memory = SharedMemory()
            trace_id = memory.save_trace(result)
            result["trace_id"] = trace_id
            return result
        else:
            raise ValueError("No JSON object found in LLM response.")

    except Exception as e:
        logger.error("Failed to parse LLM output.", exc_info=True)
        return {
            "agent": "EmailAgent",
            "urgency": "unknown",
            "type": "unknown",
            "tone": "unknown",
            "trigger_action": False,
            "error": str(e)
        }
