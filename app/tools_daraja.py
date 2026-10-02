"""Mock Daraja STK Push with idempotency. Real mode placeholder for Phase 1 pilot."""
from . import store

_poll_counts: dict[str, int] = {}


def stk_push(order_id: str, phone: str, amount: int) -> dict:
    # Idempotent: same order_id returns same checkout
    existing = store.db["payments"].get(order_id)
    if existing:
        return existing
    checkout_id = f"CHK-{order_id}"
    rec = {"order_id": order_id, "checkout_id": checkout_id, "phone": phone, "amount": amount, "status": "pending", "polls": 0}
    store.db["payments"][order_id] = rec
    _poll_counts[order_id] = 0
    return rec


def query_status(order_id: str) -> dict:
    rec = store.db["payments"].get(order_id)
    if not rec:
        return {"order_id": order_id, "status": "not_found"}
    # Mock: succeed after 2 polls to simulate user entering PIN
    rec["polls"] += 1
    if rec["polls"] >= 2:
        rec["status"] = "success"
    return rec


def reset_mock():
    _poll_counts.clear()
