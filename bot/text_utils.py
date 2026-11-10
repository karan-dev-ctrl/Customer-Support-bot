import re

def clean(text: str) -> str:
    """Lowercase and remove {{placeholders}}."""
    return re.sub(r"\{\{.*?\}\}", " ", text.lower())

NEGATIVE = {"anger", "annoyance", "disappointment", "disapproval", "disgust",
            "embarrassment", "fear", "grief", "nervousness", "remorse", "sadness"}
POSITIVE = {"admiration", "amusement", "approval", "caring", "excitement",
            "gratitude", "joy", "love", "optimism", "pride", "relief"}

def emotion_to_sentiment(emotions: str) -> str:
    """GoEmotions has 28 labels. Group the first one into 3 sentiments."""
    first = emotions.split(",")[0]
    if first in NEGATIVE:
        return "negative"
    if first in POSITIVE:
        return "positive"
    return "neutral"