# Workflow Template — Restaurant As-Is

Copy per business: `workflow-<business>.md`

## Actors
Customer | WhatsApp/IG | Owner/Staff | M-Pesa | Kitchen | Rider

## Happy path
1. Customer messages (e.g. "Niaje, menu leo?" / "Delivery to Kilimani how much?")
2. Owner replies with menu/prices/delivery fee/ETA
3. Customer places order (items x qty + location + phone)
4. Owner totals + delivery fee, requests M-Pesa (Till number or STK Push if available)
5. Customer pays, sends screenshot/waits
6. Owner verifies SMS/Till, confirms order + ETA
7. Kitchen prepares, rider delivers, owner confirms

## Exceptions (tally frequency)
- No reply / late reply -> lost sale
- Out of stock / price mismatch
- Payment not seen / wrong Till / partial payment
- Customer cancels / reschedules / wrong address
- Complaint / refund request

## Metrics to fill
- Median time: first reply, quote-to-order, payment-to-confirm
- Owner touches per order, hrs/day on chats
- Drop-offs: no-reply %, payment-fail %, cancel %
- After-hours load

## Synthesis (after 5-10)
- Common loop + variants
- Pain ranked by time lost + lost sales
- Proposed P0 loop + handoff triggers:
  - low confidence / out-of-stock / amount > threshold / complaint / payment mismatch -> handoff with full context
