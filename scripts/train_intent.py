import re
import duckdb
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# 1. Read the clean data from the warehouse
con = duckdb.connect("warehouse/chatbot.duckdb", read_only=True)
df = con.execute(
    "SELECT text, intent FROM messages WHERE source_dataset = 'bitext'"
).df()

# 2. Remove {{placeholders}} and lowercase
def clean(text):
    return re.sub(r"\{\{.*?\}\}", " ", text.lower())

# 3. Split: 80% to learn from, 20% held back to test on
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["intent"],
    test_size=0.2, random_state=42, stratify=df["intent"],
)

# 4. TF-IDF turns text into numbers; logistic regression learns from them
model = Pipeline([
    ("tfidf", TfidfVectorizer(preprocessor=clean, ngram_range=(1, 2),
                              min_df=2, sublinear_tf=True)),
    ("clf", LogisticRegression(max_iter=1000)),
])
model.fit(X_train, y_train)

# 5. Evaluate on messages the model has never seen
print(classification_report(y_test, model.predict(X_test)))