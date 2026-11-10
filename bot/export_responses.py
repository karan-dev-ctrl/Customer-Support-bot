import json
import duckdb

con = duckdb.connect("warehouse/chatbot.duckdb", read_only=True)
df = con.execute(
    "SELECT intent, reference_response FROM messages WHERE source_dataset = 'bitext'"
).df()

def sample_replies(s):
    short = s[(s.str.len() < 350) & ~s.str.contains("[", regex=False)]
    pool = short if len(short) >= 5 else s
    return list(pool.sample(min(len(pool), 20), random_state=42))

responses = df.groupby("intent")["reference_response"].apply(sample_replies).to_dict()
with open("models/responses.json", "w", encoding="utf-8") as f:
    json.dump(responses, f, ensure_ascii=False)
print({k: len(v) for k, v in list(responses.items())[:3]}, "...")