import os

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "demo-verify-token")
DARAJA_MODE = os.getenv("DARAJA_MODE", "mock")
DELIVERY_FEE = int(os.getenv("DELIVERY_FEE_KES", "200"))
HANDOFF_THRESHOLD = int(os.getenv("HANDOFF_THRESHOLD_AMOUNT", "10000"))
TENANT = "demo-restaurant"
