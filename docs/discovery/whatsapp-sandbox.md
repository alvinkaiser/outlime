# WhatsApp Sandbox Setup (No production access yet)

PRD constraints: WhatsApp first, web-chat fallback; follow messaging policies (§12 risk).

## Sandbox path (Meta WhatsApp Cloud API)
1. Create Meta App -> Add WhatsApp product -> use test number (provided by Meta, free-form within 24h window).
2. Configure webhook for Phase 1 Python service:
   - `GET /webhooks/whatsapp` (verify: hub.mode, hub.verify_token, hub.challenge)
   - `POST /webhooks/whatsapp` (messages, statuses)
   - Keep `VERIFY_TOKEN` in server env, never in client.
3. Test: send message from personal WhatsApp to test number, observe webhook payload, reply via API.
4. Document payload samples for agent core.

## Production onboarding (to research in discovery)
- Business verification, display name approval
- Direct Cloud API vs BSP (cost, support, templates)
- Template approval for proactive messages (order confirm, delivery update, payment follow-up)
- Opt-in/opt-out handling, 24h service window rules
- Per-message pricing estimate for pilot

## Fallback
- Web-chat widget -> same `POST /conversations/message` internal API, so MVP demo works without WhatsApp approval.
- Instagram DMs: P1, not in sandbox phase.

## Checklist
- [ ] Sandbox test number working
- [ ] Webhook verify + receive + reply OK
- [ ] Sample payloads saved (no real PII)
- [ ] Production requirements + cost noted in decision-log
