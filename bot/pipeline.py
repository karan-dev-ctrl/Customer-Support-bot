import uuid

from bot.predict import respond
from bot.logger import log_interaction


def handle_message(message: str, session_id: str) -> dict:
    result = respond(message)
    try:
        log_interaction(session_id, message, result)
    except Exception as e:                # never let logging break the chat
        print(f"logging failed: {e}")
    return result


if __name__ == "__main__":
    session = str(uuid.uuid4())
    print("Type a message (empty line to quit)")
    while (msg := input("> ").strip()):
        out = handle_message(msg, session)
        print(f"  [{out['route']}] {out['intent']} ({out['intent_conf']}) | "
              f"{out['sentiment']} ({out['sentiment_conf']})")
        print(out["reply"])