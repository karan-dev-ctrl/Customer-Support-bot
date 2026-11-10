import duckdb
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

from bot.text_utils import clean, emotion_to_sentiment

con = duckdb.connect("warehouse/chatbot.duckdb", read_only=True)

def build_model():
    return Pipeline([
        ("tfidf", TfidfVectorizer(preprocessor=clean, ngram_range=(1, 2),
                                  min_df=2, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])

def train_and_save(X, y, name):
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    model = build_model().fit(X_tr, y_tr)
    print(f"\n=== {name} ===")
    print(classification_report(y_te, model.predict(X_te)))
    joblib.dump(model, f"models/{name}.joblib")
    return model

# Intent (Bitext + out-of-scope examples from GoEmotions)
d = con.execute("SELECT text, intent FROM messages WHERE source_dataset='bitext'").df()
g = con.execute("SELECT text, emotions FROM messages WHERE source_dataset='goemotions'").df()
oos = g[["text"]].sample(2000, random_state=42).assign(intent="out_of_scope")
d = pd.concat([d, oos], ignore_index=True)
intent_model = train_and_save(d["text"], d["intent"], "intent")

# Sentiment (GoEmotions)
g["sentiment"] = g["emotions"].apply(emotion_to_sentiment)
sent_model = train_and_save(g["text"], g["sentiment"], "sentiment")

# Try your own messages
tests = ["where is my package", "i want my money back",
         "this is ridiculous, nobody answers me", "how do i reset my password",
         "thanks, you were really helpful"]
print("\nIntent: ", list(intent_model.predict(tests)))
print("Sentiment:", list(sent_model.predict(tests)))