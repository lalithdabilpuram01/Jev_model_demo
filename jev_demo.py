"""Demo: test TypeSafe's Jev (System One) model with its three primitives.

Setup:
    pip install -r requirements.txt
    cp .env.example .env   # then put your key in .env

Run:
    python jev_demo.py
"""

import os
import statistics
import sys
import time

from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

load_dotenv()  # picks up TYPESAFE_API_KEY from .env if present

# A few support tickets to run through the model.
TICKETS = [
    {
        "subject": "Duplicate charge",
        "text": "I was charged twice for order A-104. Please refund the duplicate.",
    },
    {
        "subject": "App crashes on login",
        "text": "This is the THIRD time I'm writing. Your app crashes every time I log in. "
        "Fix it today or I'm cancelling!",
    },
    {
        "subject": "Enterprise pricing",
        "text": "Hi, could you send me pricing for 50 seats? No rush.",
    },
]

QUESTIONS = {
    "department": Choice(
        instructions="Which team should handle this ticket",
        criteria={
            "billing": "Payment, charges, refunds or subscription issues",
            "technical": "Bugs, crashes or integration problems",
            "sales": "Pricing, quotes or new account questions",
        },
    ),
    "frustration": Score(
        instructions="How frustrated the customer appears",
        criteria=[
            "Calm, just stating facts",
            "Frustrated but civil",
            "Very angry, strong language",
        ],
    ),
    "refund_requested": Noul(instructions="The customer is explicitly asking for a refund"),
    "urgent": Noul(instructions="The message conveys urgency or time-sensitivity"),
}


def show_answer(name, answer):
    """Print whichever fields the answer carries (choice / score / noul + confidence)."""
    parts = []
    for field in ("choice", "score", "noul", "confidence"):
        value = getattr(answer, field, None)
        if value is not None:
            parts.append(f"{field}={value:.3f}" if isinstance(value, float) else f"{field}={value}")
    print(f"  {name:<17} {', '.join(parts) or answer}")


def main():
    if not os.environ.get("TYPESAFE_API_KEY"):
        sys.exit("Set TYPESAFE_API_KEY first (get one at https://console.typesafe.ai).")

    client = TypeSafeClient()  # reads TYPESAFE_API_KEY, defaults to jev-latest

    # Warm-up call so connection setup (DNS/TLS) doesn't skew the first timing.
    client.system_one(state={"ticket": TICKETS[0]}, questions=QUESTIONS)

    latencies_ms = []
    for ticket in TICKETS:
        start = time.perf_counter()
        response = client.system_one(state={"ticket": ticket}, questions=QUESTIONS)
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies_ms.append(elapsed_ms)

        per_decision_ms = elapsed_ms / len(QUESTIONS)
        print(
            f"\n[{ticket['subject']}]  {elapsed_ms:.0f} ms for {len(QUESTIONS)} decisions "
            f"({per_decision_ms:.1f} ms/decision)"
        )
        for name, answer in response.answers.items():
            show_answer(name, answer)

        usage = getattr(response, "usage", None)
        if usage is not None:
            print(f"  usage: {usage}")

        # Confidence-gated routing: only auto-route when Jev is sure.
        dept = response.answers["department"]
        if getattr(dept, "confidence", 0) >= 0.8:
            print(f"  -> auto-route to {dept.choice}")
        else:
            print("  -> low confidence, send to a human")

    total_decisions = len(latencies_ms) * len(QUESTIONS)
    total_s = sum(latencies_ms) / 1000
    print("\nDecision speed (client-side round trip, includes network):")
    print(f"  calls:         {len(latencies_ms)}")
    print(f"  min / max:     {min(latencies_ms):.0f} / {max(latencies_ms):.0f} ms")
    print(f"  mean / median: {statistics.mean(latencies_ms):.0f} / {statistics.median(latencies_ms):.0f} ms")
    print(f"  throughput:    {total_decisions / total_s:.1f} decisions/s ({total_decisions} decisions)")


if __name__ == "__main__":
    main()
