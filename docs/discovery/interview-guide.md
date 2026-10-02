# Interview Guide — Restaurants (30 min)

## Intro + consent (2 min)
- Purpose: learn how you handle customer chats, orders, and M-Pesa today, to design one helpful AI loop.
- Anonymized notes, no customer PII stored beyond masked transcripts.
- You can stop anytime. Data handling per Kenya DPA: minimal retention, tenant-isolated, consent required.
- Ask permission to keep 10 anonymized chat samples for language eval (Swahili/English/Sheng).

## Questions
1. Walk me through yesterday's orders — what % came via WhatsApp / IG / call / walk-in?
2. What are the top 5 repeated questions? (menu, price, hours, delivery fee, ETA)
3. How do you quote menu/price/delivery? Zones and fees?
4. M-Pesa step-by-step: Till or Paybill? Do you send STK Push or customer sends? Failures, duplicates, delays?
5. Missed/late replies or abandoned orders — how often? Lost sales estimate?
6. How do you handle order status, reschedules, complaints?
7. Peak + night load — who covers? Hours owner spends/day on chats?
8. Language examples: Swahili / English / Sheng mix — can you share 2-3 real phrasings?
9. What should AI *never* do without you? When must a human take over?
10. If you got a 5-line daily summary, what must be in it? (sales, payments, handoffs, stock-outs)
11. Pricing probe: one-time setup + monthly retainer vs per-confirmed-order — what would you accept?

## Capture per interview
- Business: size, branches, orders/day, channels %, backend (sheet/WooCommerce/POS/none)
- Time spent hrs/day, payment errors/mo, missed chats/mo
- Till/Paybill type, reconciliation method
- Language samples (for LLM eval set)
- Pilot willingness + price signal
- File as `interview-YYYY-MM-DD-<business>.md` (no real customer phone numbers)
