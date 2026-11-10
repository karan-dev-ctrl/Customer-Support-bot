import duckdb
import pandas as pd
from datasets import load_dataset

con = duckdb.connect("warehouse/chatbot.duckdb")
con.execute("CREATE SCHEMA IF NOT EXISTS raw")

# --- Bitext: customer messages with intents and sample replies ---
bitext = load_dataset(
    "bitext/Bitext-customer-support-llm-chatbot-training-dataset", split="train"
).to_pandas()
con.register("bitext_df", bitext)
con.execute("CREATE OR REPLACE TABLE raw.bitext AS SELECT * FROM bitext_df")

# --- GoEmotions: Reddit comments with emotion labels ---
ge = load_dataset("google-research-datasets/go_emotions", "simplified")
names = ge["train"].features["labels"].feature.names   # id -> emotion name

frames = []
for split in ["train", "validation", "test"]:
    df = ge[split].to_pandas()
    df["split"] = split
    df["emotions"] = df["labels"].apply(lambda ids: ",".join(names[i] for i in ids))
    frames.append(df[["id", "text", "emotions", "split"]])
goemotions = pd.concat(frames, ignore_index=True)
con.register("ge_df", goemotions)
con.execute("CREATE OR REPLACE TABLE raw.goemotions AS SELECT * FROM ge_df")

print(con.execute("SELECT count(*) FROM raw.bitext").fetchone())
print(con.execute("SELECT count(*) FROM raw.goemotions").fetchone())