# fake_crm.py
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/crm/escalate")
async def escalate_issue(req: Request):
    body = await req.json()
    print("[CRM] Escalation received:", body)
    return {"status": "received"}


