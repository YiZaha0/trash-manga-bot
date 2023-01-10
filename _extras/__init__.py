import os

SUDOS = os.environ.get("SUDOS", "5304356242 5370531116 5551387300")
SUDOS = list(map(int, SUDOS.split()))
