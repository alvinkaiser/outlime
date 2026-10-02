# Decision Log — Phase 0

## Fixed
- Vertical: Restaurants (from Open Questions)
- Stack for MVP spike: Python (FastAPI) service
- WhatsApp status: no access -> sandbox + web-chat fallback

## Proposed P0 loop (to validate)
`menu/hours/delivery Q&A (grounded in menu/FAQs) -> build order -> total + delivery fee -> explicit customer confirm (yes + phone) -> idempotent STK Push -> poll status -> on success: order ID + ETA + notify owner/kitchen; on fail/timeout: retry once then handoff with full context`

Handoff triggers: low confidence, out-of-stock, amount > threshold, complaint, payment mismatch.

## Open (from PRD §13, close in discovery)
- [ ] Backend mix: sheet vs Shopify/WooCommerce/POS?
- [ ] Pricing accepted: setup + retainer vs per-order?
- [ ] LLM/hosting for Sheng/Swa/Eng (eval on 25-30 samples)?
- [ ] Exact DPA + WhatsApp onboarding requirements?

## Exit gate to Phase 1
- [ ] 5-10 interviews filed
- [ ] As-is map + time/payment loss quantified
- [ ] ONE loop + handoff rules signed off
- [ ] 1 paying pilot identified
