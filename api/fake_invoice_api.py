# fake_compliance.py
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/invoice/flag")
async def invoice(req: Request):
    data = await req.json()
    print("[Invoice Flag Triggered]", data)
    return {"status": "flagged"}
