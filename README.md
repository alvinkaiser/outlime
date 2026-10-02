# Restaurant Agent (Phase 1 spike)

PRD v0.1 → Phase 0 discovery in `docs/discovery/` (+ `preview.html` bundle).
Phase 1 MVP loop: inquiry → quote → M-Pesa STK Push → confirmation, on WhatsApp with handoff. Web-chat fallback included.

## Run
```
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload --port 8000
```
- Swagger: http://localhost:8000/docs
- Web chat: http://localhost:8000/static/widget.html
- Health: http://localhost:8000/health

## Try (web chat or API)
1. `niaje, menu?` → grounded menu
2. `pilau x2 na soda` → quote + ask NDIO + phone
3. `NDIO 0712345678` → mock STK Push (idempotent per order)
4. `nimesalipa` (x2) → pending → confirmed + order ID
- Unknown gibberish → human handoff with context
- Complaint words → immediate handoff

## Endpoints
- `POST /conversations/message` {sender, text, phone?}
- `GET/POST /webhooks/whatsapp` (verify + incoming)
- `POST /webhooks/daraja` (callback log)
- `GET /owner/daily-summary`, `GET /owner/conversations`

## Safety (per PRD §8/§12)
- Explicit NDIO + phone before any STK Push; idempotent `stk_push(order_id)`; status verified before confirming; full audit log; per-tenant store.

## Next
Real Daraja (`DARAJA_MODE=real`), Postgres, LLM for Sheng/Swa/Eng eval, templates + admin console.
