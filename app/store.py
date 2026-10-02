"""In-memory per-tenant store with audit log. Swap for Postgres in Phase 2."""
import time
import uuid

db = {
    "conversations": {},  # (tenant, sender) -> {messages: [], order_draft, awaiting_confirm, order_id}
    "orders": {},  # order_id -> order dict
    "payments": {},  # checkout_id/order_id -> payment dict
    "handoffs": [],  # list of handoff dicts
    "audit": [],  # list of {ts, tenant, actor, action, detail}
}


def audit(tenant: str, actor: str, action: str, detail: str = ""):
    db["audit"].append({"ts": time.time(), "tenant": tenant, "actor": actor, "action": action, "detail": detail})


def get_convo(tenant: str, sender: str):
    key = (tenant, sender)
    if key not in db["conversations"]:
        db["conversations"][key] = {"messages": [], "order_draft": {}, "awaiting_confirm": False, "order_id": None, "phone": None}
    return db["conversations"][key]


def new_order_id():
    return "ORD-" + uuid.uuid4().hex[:8].upper()


def reset():
    db["conversations"].clear()
    db["orders"].clear()
    db["payments"].clear()
    db["handoffs"].clear()
    db["audit"].clear()
