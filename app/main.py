"""FastAPI MVP: WhatsApp webhook + web-chat + Daraja callback + owner APIs."""
from fastapi import FastAPI, Query, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import agent, config, store

app = FastAPI(title="AI Agents KE - Restaurant MVP", version="0.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatIn(BaseModel):
    sender: str = "demo-user"
    text: str
    phone: str | None = None
    tenant: str = config.TENANT


@app.get("/health")
def health():
    return {"ok": True, "tenant": config.TENANT, "daraja_mode": config.DARAJA_MODE}


@app.post("/conversations/message")
def chat(inp: ChatIn):
    res = agent.handle_message(inp.tenant, inp.sender, inp.text, inp.phone)
    return res


# WhatsApp Cloud API webhook
@app.get("/webhooks/whatsapp")
def wa_verify(
    hub_mode: str = Query("", alias="hub.mode"),
    hub_challenge: str = Query("", alias="hub.challenge"),
    hub_verify_token: str = Query("", alias="hub.verify_token"),
):
    if hub_verify_token == config.VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge or "ok")
    return PlainTextResponse("forbidden", status_code=403)


@app.post("/webhooks/whatsapp")
async def wa_incoming(req: Request):
    try:
        body = await req.json()
    except Exception:
        return {"ok": True}
    # Minimal parse of Cloud API payload; fallback to raw text
    try:
        entry = body.get("entry", [{}])[0]
        change = entry.get("changes", [{}])[0]
        value = change.get("value", {})
        msgs = value.get("messages", [])
        for m in msgs:
            sender = m.get("from", "wa-user")
            text = m.get("text", {}).get("body", "") if m.get("type") == "text" else ""
            if text:
                agent.handle_message(config.TENANT, sender, text)
    except Exception as e:
        store.audit(config.TENANT, "system", "wa_parse_error", str(e)[:200])
    return {"ok": True}


# Daraja callback (C2B/STK result) — logs and marks latest pending order
@app.post("/webhooks/daraja")
async def daraja_cb(req: Request):
    try:
        body = await req.json()
    except Exception:
        body = {}
    store.audit(config.TENANT, "daraja", "callback", str(body)[:500])
    return {"ok": True}


@app.get("/owner/daily-summary")
def daily_summary(tenant: str = config.TENANT):
    orders = [o for o in store.db["orders"].values() if o["tenant"] == tenant]
    confirmed = [o for o in orders if o["status"] == "confirmed"]
    revenue = sum(o["total"] for o in confirmed)
    return {
        "tenant": tenant,
        "orders_total": len(orders),
        "orders_confirmed": len(confirmed),
        "revenue_kes": revenue,
        "handoffs": len([h for h in store.db["handoffs"] if h["tenant"] == tenant]),
        "audit_events": len([a for a in store.db["audit"] if a["tenant"] == tenant]),
    }


@app.get("/owner/conversations")
def owner_convos(tenant: str = config.TENANT):
    out = []
    for (t, sender), c in store.db["conversations"].items():
        if t == tenant:
            out.append({"sender": sender, "messages": c["messages"][-20:], "order_id": c.get("order_id")})
    return {"conversations": out, "handoffs": store.db["handoffs"]}
