from fastapi.testclient import TestClient
from app.main import app
from app import store

client = TestClient(app)


def setup_function(_):
    store.reset()


def test_menu_grounded():
    r = client.post("/conversations/message", json={"sender": "u1", "text": "niaje, menu?"})
    assert r.status_code == 200
    assert "Pilau" in r.json()["reply"]


def test_full_loop_order_pay_confirm():
    r1 = client.post("/conversations/message", json={"sender": "u2", "text": "pilau x2 na soda"}).json()["reply"]
    assert "pilau" in r1.lower()
    r2 = client.post("/conversations/message", json={"sender": "u2", "text": "NDIO 0712345678"})
    assert "STK Push" in r2.json()["reply"]
    order_id = r2.json()["order_id"]
    # first poll: pending
    r3 = client.post("/conversations/message", json={"sender": "u2", "text": "nimesalipa"})
    assert r3.json()["payment_status"] == "pending"
    # second poll: success
    r4 = client.post("/conversations/message", json={"sender": "u2", "text": "nimesalipa"})
    assert r4.json()["payment_status"] == "success"
    # idempotency: same order STK not duplicated
    assert store.db["orders"][order_id]["status"] == "confirmed"


def test_handoff_low_confidence():
    r = client.post("/conversations/message", json={"sender": "u3", "text": "blabla xyzzy quantum"})
    assert r.json()["handoff"] is True


def test_whatsapp_verify():
    r = client.get("/webhooks/whatsapp", params={"hub.mode": "subscribe", "hub.challenge": "abc", "hub.verify_token": "demo-verify-token"})
    assert r.text == "abc"
