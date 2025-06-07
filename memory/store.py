# multi_agent_system/memory/store.py

import redis
import json
import uuid
import os
from datetime import datetime

# Load Redis config from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Initialize Redis connection
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

class SharedMemory:
    def __init__(self):
        self.prefix = "agent_trace:"

    def save_trace(self, data: dict) -> str:
        trace_id = str(uuid.uuid4())
        data["trace_id"] = trace_id
        data["logged_at"] = datetime.utcnow().isoformat()

        key = self.prefix + trace_id
        r.set(key, json.dumps(data))
        return trace_id

    def get_trace(self, trace_id: str):
        key = self.prefix + trace_id
        value = r.get(key)
        return json.loads(value) if value else None

    def list_all_traces(self):
        keys = r.keys(self.prefix + "*")
        return [json.loads(r.get(k)) for k in keys]
    

