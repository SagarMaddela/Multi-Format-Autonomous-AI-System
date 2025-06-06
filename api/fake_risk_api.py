# fake_risk_api.py

from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/risk_alert")
async def risk_alert(req: Request):
    data = await req.json()
    print("[Risk Alert] Logged anomaly:", data)
    return {"status": "received"}
