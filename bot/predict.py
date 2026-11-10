import json
import random
import re
from pathlib import Path

import joblib

MODELS = Path(__file__).resolve().parent.parent / "models"
intent_model = joblib.load(MODELS / "intent.joblib")
sent_model = joblib.load(MODELS / "sentiment.joblib")
RESPONSES = json.load(open(MODELS / "responses.json", encoding="utf-8"))

INTENT_THRESHOLD = 0.30     # below this, the bot admits it is unsure; tune it!
SENTIMENT_THRESHOLD = 0.50
ESCALATE_INTENTS = {"complaint", "contact_human_agent", "contact_customer_service"}

THANKS = re.compile(r"\b(thanks|thank you|thx)\b", re.I)
GREETING = re.compile(r"^\s*(hi|hello|hey)\b", re.I)


def analyze(message: str) -> dict:
    """Predict what the customer wants and how they feel."""
    ip = intent_model.predict_proba([message])[0]
    sp = sent_model.predict_proba([message])[0]
    i, j = ip.argmax(), sp.argmax()
    return {
        "intent": str(intent_model.classes_[i]),
        "intent_conf": round(float(ip[i]), 3),
        "sentiment": str(sent_model.classes_[j]),
        "sentiment_conf": round(float(sp[j]), 3),
    }


def fill_placeholders(text: str) -> str:
    # In a real system these would be filled from an orders table in the warehouse.
    return re.sub(r"\{\{(.*?)\}\}", lambda m: f"[{m.group(1).lower()}]", text)


def respond(message: str) -> dict:
    a = analyze(message)
    upset = a["sentiment"] == "negative" and a["sentiment_conf"] >= SENTIMENT_THRESHOLD

    if THANKS.search(message):
        route, reply = "smalltalk", "You're welcome! Is there anything else I can help with?"
    elif GREETING.search(message):
        route, reply = "smalltalk", "Hello! How can I help you today?"
    elif a["intent"] == "out_of_scope" or a["intent_conf"] < INTENT_THRESHOLD:
        if upset:
            route = "escalate"
            reply = ("I'm really sorry about this experience. I couldn't tell exactly "
                     "what you need, so I'm passing you to a human agent who can help.")
        else:
            route = "fallback"
            reply = ("I'm not sure I understood that. Could you rephrase, "
                     "or would you like me to connect you with a human agent?")
    else:
        route = "intent"
        reply = fill_placeholders(random.choice(RESPONSES[a["intent"]]))
        if upset:
            reply = "I'm sorry for the trouble. " + reply
        if upset or a["intent"] in ESCALATE_INTENTS:
            reply += " If you'd like, I can connect you with a human agent."

    return {**a, "route": route, "reply": reply}


if __name__ == "__main__":
    print("Type a message (empty line to quit)")
    while (msg := input("> ").strip()):
        out = respond(msg)
        print(f"  [{out['route']}] intent={out['intent']} ({out['intent_conf']}) "
              f"sentiment={out['sentiment']} ({out['sentiment_conf']})")
        print(out["reply"])