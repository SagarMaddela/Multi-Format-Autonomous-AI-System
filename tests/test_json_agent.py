import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from json_agent.agent import detect_json_anomaly
import json

if __name__ == "__main__":
    with open("samples/webhook1.json") as f:
        data = json.load(f)

    result = detect_json_anomaly(data)
    print("Anomaly Detection Result:")
    print(json.dumps(result, indent=2))
