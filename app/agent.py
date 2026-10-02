"""Agent core: grounded menu Q&A + order draft + confirm + STK push + handoff.

No LLM key required for MVP: keyword matching in English/Swahili/Sheng.
LLM can replace `grounded_answer` later; handoff + audit + idempotency stay.
"""
import json
import pathlib
import re

from . import config, store, tools_daraja

MENU_PATH = pathlib.Path(__file__).parent / "data" / "menu.json"
MENU = json.loads(MENU_PATH.read_text(encoding="utf-8"))

YES = {"yes", "ndio", "ndiyo", "sawa", "ok", "okay", "confirm", "lipa", "pay"}
NO = {"no", "hapana", "cancel", "ghairi"}
COMPLAINT = {"complaint", "wrong", "rude", "refund", "dirty", "late", "missing", "stolen"}
PAY_WORDS = {"lipa", "pay", "mpesa", "m-pesa", "stk", "till", "paybill"}
MENU_WORDS = {"menu", "bei", "price", "food", "chakula", "eat", "order", "agiza", "pilau", "biriani", "chapati", "soda"}


def menu_text() -> str:
    lines = [f"- {m['name']}: KES {m['price']}" for m in MENU["menu"]]
    zones = ", ".join(f"{k} (KES {v})" for k, v in MENU["delivery_zones"].items())
    return f"{MENU['restaurant']} | Hours {MENU['hours']}\n" + "\n".join(lines) + f"\nDelivery: {zones}"


def find_items(text: str) -> dict:
    t = text.lower()
    found: dict[str, int] = {}
    for m in MENU["menu"]:
        name = m["name"].lower()
        mid = m["id"]
        # match id or first word of name
        first = name.split()[0]
        if mid in t or first in t:
            qty = 1
            mm = re.search(r"(\d+)\s*(?:x)?\s*" + re.escape(mid) + r"|" + re.escape(mid) + r"\s*x\s*(\d+)", t)
            if mm:
                qty = int(mm.group(1) or mm.group(2) or 1)
            else:
                q2 = re.search(r"(\d+)\s*" + re.escape(first), t)
                if q2:
                    qty = int(q2.group(1))
            found[mid] = found.get(mid, 0) + qty
    return found


def totals(draft: dict) -> tuple[int, int, int]:
    price = {m["id"]: m["price"] for m in MENU["menu"]}
    sub = sum(price[k] * v for k, v in draft.items() if k in price)
    fee = config.DELIVERY_FEE
    return sub, fee, sub + fee


def handle_message(tenant: str, sender: str, text: str, phone: str | None = None) -> dict:
    convo = store.get_convo(tenant, sender)
    convo["messages"].append({"from": sender, "text": text})
    if phone:
        convo["phone"] = phone
    t = text.lower().strip()
    store.audit(tenant, sender, "message_in", text[:200])

    # 1. Complaint / sensitive -> immediate handoff
    if any(w in t for w in COMPLAINT):
        return do_handoff(tenant, sender, reason="complaint/sensitive", detail=text)

    # 2. Awaiting payment confirmation? Check STK status polls
    if convo.get("order_id"):
        order = store.db["orders"].get(convo["order_id"])
        if order and order["status"] in ("payment_pending",):
            pay = tools_daraja.query_status(order["order_id"])
            if pay["status"] == "success":
                order["status"] = "confirmed"
                store.audit(tenant, "agent", "payment_confirmed", order["order_id"])
                convo["order_id"] = None
                convo["order_draft"] = {}
                convo["awaiting_confirm"] = False
                reply = f"Asante! Payment confirmed ({order['order_id']}, KES {order['total']}). ETA 30-45 min. Nambari ya oda: {order['order_id']}."
                convo["messages"].append({"from": "agent", "text": reply})
                return {"reply": reply, "order_id": order["order_id"], "payment_status": "success", "handoff": False}
            else:
                # one retry then handoff if still pending and polls exhausted
                if pay["polls"] >= 4:
                    return do_handoff(tenant, sender, reason="payment_not_confirmed", detail=order["order_id"])
                reply = "Bado tunangojea M-Pesa PIN yako. Tafadhali weka PIN kwenye simu yako, kisha nijibu 'nimesalipa'."
                convo["messages"].append({"from": "agent", "text": reply})
                return {"reply": reply, "order_id": order["order_id"], "payment_status": "pending", "handoff": False}

    # 3. Awaiting explicit order confirm (yes + phone)
    if convo.get("awaiting_confirm"):
        if any(w in t for w in YES):
            m = re.search(r"254\d{9}|0[17]\d{8}", t.replace(" ", ""))
            ph = m.group(0) if m else convo.get("phone")
            if not ph:
                reply = "Sawa! Tuma namba yako ya M-Pesa (e.g. 0712... ) ili nikutumie STK Push."
                convo["messages"].append({"from": "agent", "text": reply})
                return {"reply": reply, "handoff": False}
            # normalize 07.. -> 254..
            if ph.startswith("0"):
                ph = "254" + ph[1:]
            return start_payment(tenant, sender, ph)
        if any(w in t for w in NO):
            convo["awaiting_confirm"] = False
            convo["order_draft"] = {}
            reply = "Sawa, nimeghairi. Unataka kuagiza kitu kingine? Andika 'menu' kuona vyakula."
            convo["messages"].append({"from": "agent", "text": reply})
            return {"reply": reply, "handoff": False}
        # otherwise fall through to update draft

    # 4. Order intent: accumulate items
    items = find_items(t)
    if items:
        for k, v in items.items():
            convo["order_draft"][k] = convo["order_draft"].get(k, 0) + v
        sub, fee, total = totals(convo["order_draft"])
        if total > config.HANDOFF_THRESHOLD:
            return do_handoff(tenant, sender, reason="high_value_needs_human", detail=str(total))
        # phone in same message?
        m = re.search(r"254\d{9}|0[17]\d{8}", t.replace(" ", ""))
        if m:
            convo["phone"] = m.group(0)
        desc = ", ".join(f"{k} x{v}" for k, v in convo["order_draft"].items())
        convo["awaiting_confirm"] = True
        reply = (
            f"Sawa! Oda yako: {desc}. Jumla KES {sub} + delivery KES {fee} = KES {total}.\n"
            "Kuthibitisha, jibu 'NDIO' na namba yako ya M-Pesa. Nitakutumia STK Push."
        )
        convo["messages"].append({"from": "agent", "text": reply})
        store.audit(tenant, "agent", "quote", f"{desc} total={total}")
        return {"reply": reply, "handoff": False, "draft": convo["order_draft"], "total": total}

    # 5. Menu / price / hours questions -> grounded answer
    if any(w in t for w in MENU_WORDS) or t in {"menu", "niaje", "habari", "hello", "hi", "hey", "sasa"}:
        reply = menu_text() + "\n\nKuagiza: andika e.g. 'pilau x2 na soda'. Kulipa: M-Pesa STK Push hapa chat."
        # Sheng/Swahili touch
        if any(w in t for w in {"niaje", "sasa", "poa", "fiti"}):
            reply = "Niaje! " + reply
        convo["messages"].append({"from": "agent", "text": reply})
        return {"reply": reply, "handoff": False}

    if any(w in t for w in PAY_WORDS):
        if not convo["order_draft"]:
            reply = "Sawa — kuagiza kwanza: andika e.g. 'biriani x1'. Kisha nitakutumia STK Push ya M-Pesa."
        else:
            reply = "Sawa! Jibu 'NDIO' na namba yako ya M-Pesa nitume STK Push."
            convo["awaiting_confirm"] = True
        convo["messages"].append({"from": "agent", "text": reply})
        return {"reply": reply, "handoff": False}

    # 6. Low confidence -> handoff with context
    return do_handoff(tenant, sender, reason="low_confidence", detail=text)


def start_payment(tenant: str, sender: str, phone: str) -> dict:
    convo = store.get_convo(tenant, sender)
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    sub, fee, total = totals(convo["order_draft"])
    order_id = store.new_order_id()
    order = {
        "order_id": order_id, "tenant": tenant, "sender": sender, "phone": phone,
        "items": dict(convo["order_draft"]), "subtotal": sub, "fee": fee, "total": total,
        "status": "payment_pending",
    }
    store.db["orders"][order_id] = order
    convo["order_id"] = order_id
    convo["awaiting_confirm"] = False
    store.audit(tenant, "agent", "stk_push", f"{order_id} {phone} KES {total}")
    pay = tools_daraja.stk_push(order_id, phone, total)
    reply = (
        f"Nimetuma STK Push kwa {phone} — KES {total} ({order_id}). Weka M-Pesa PIN, kisha nijibu 'nimesalipa' "
        "nikuthibitishie oda."
    )
    convo["messages"].append({"from": "agent", "text": reply})
    return {"reply": reply, "order_id": order_id, "payment_status": pay["status"], "handoff": False}


def do_handoff(tenant: str, sender: str, reason: str, detail: str = "") -> dict:
    convo = store.get_convo(tenant, sender)
    ctx = convo["messages"][-6:]
    store.db["handoffs"].append({"tenant": tenant, "sender": sender, "reason": reason, "detail": detail, "context": ctx})
    store.audit(tenant, "agent", "handoff", f"{reason}: {detail[:150]}")
    reply = (
        "Nimekuelewa — huyu anahitaji binadamu. Nimeshamjulisha muhudumu na mazungumzo yote. "
        "Atakujibu punde. Asante kwa subira! (Human notified.)"
    )
    convo["messages"].append({"from": "agent", "text": reply})
    return {"reply": reply, "handoff": True, "reason": reason}
