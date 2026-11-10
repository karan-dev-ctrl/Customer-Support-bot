# Customer Support Bot

A customer-support triage bot built as an end-to-end data project. It reads a customer's message, predicts **what they want** (intent) and **how they feel** (sentiment), and chooses a suitable reply. Frustrated customers are apologised to and handed to a human agent. Every conversation is logged to a data warehouse for analysis.

**Live demo:** `<paste your .streamlit.app link here>`


---

## Try it: sample questions

Type these into the chat. The sidebar option **Show model details** displays the predicted intent, sentiment and confidence for each message.

### Customer requests (the bot answers with a sample reply)

| Try this | Expected intent |
|---|---|
| `i want to cancel my order` | cancel_order |
| `how do i reset my password` | recover_password |
| `i need a refund for my broken item` | get_refund |
| `can you help me contact customer care` | contact_customer_service |
| `where is my order` | track_order |
| `how can i get an invoice` | get_invoice |
| `i want to change my shipping address` | change_shipping_address |
| `how do i create an account` | create_account |
| `what is your refund policy` | check_refund_policy |
| `i want to delete my account` | delete_account |
| `i have a problem with my payment` | payment_issue |
| `how do i subscribe to the newsletter` | newsletter_subscription |

### Message behaviour (the bot changes how it responds)

| Try this | What the bot does |
|---|---|
| `thanks, you were really helpful` | Friendly small-talk reply |
| `hello` | Greeting |
| `what is the weather on mars ?` | Says it did not understand and offers a human agent (out of scope) |
| `this is ridiculous, why is no one replying to my message ?` | Detects an upset customer and escalates to a human agent |
| `i want to cancel my order, this is so frustrating` | Answers the request, adds an apology and offers a human agent |

Results depend on the trained model, so confidence scores and replies may vary. Replies are picked at random from a set of sample replies per intent, so the same question can get different wording.

**Known limitation:** the bot has no memory between messages yet. If it asks for an order number, a follow-up such as `123456` is treated as a new message.

---

## How it works

```
Raw datasets ──> DuckDB warehouse ──> dbt cleaning ──> messages table
                                                          │
                                                          ▼
                                     train intent + sentiment models (scikit-learn)
                                                          │
customer message ──> [intent model]    ──> what they want ┐
                 ──> [sentiment model] ──> how they feel  ┴─> choose reply
                                                               │
                              reply shown in Streamlit  <──────┤
                              row logged to the warehouse <────┘
```

1. **Load:** Bitext (customer-support messages with intents and sample replies) and GoEmotions (Reddit comments with emotion labels) are loaded into a DuckDB warehouse as raw tables.
2. **Clean:** dbt turns the raw tables into one tidy `messages` table (raw → staging → mart).
3. **Train:** two TF-IDF + logistic regression models are trained.
   - **Intent:** 27 support intents plus an `out_of_scope` class, trained with non-support text from GoEmotions so the bot can recognise off-topic messages.
   - **Sentiment:** negative / neutral / positive, derived from the 28 GoEmotions emotions.
4. **Respond:** rules combine intent, sentiment and confidence to choose a route: `intent`, `smalltalk`, `fallback` or `escalate`.
5. **Log:** every message, prediction and reply is written to `logs.conversations` in the warehouse.

## Tech stack (all free)

| Layer | Tool |
|---|---|
| Language | Python |
| Warehouse | DuckDB |
| Transformations | dbt Core (`dbt-duckdb`) |
| Models | scikit-learn (TF-IDF + logistic regression) |
| Backend API | FastAPI |
| Chat interface | Streamlit |
| Hosting | Streamlit Community Cloud |
| Datasets | Bitext Customer Support, GoEmotions (via Hugging Face) |

Please check each dataset's page on Hugging Face for its licence terms.

## Results

| Model | Test accuracy | Macro F1 |
|---|---|---|
| Intent (28 classes) | 0.99 | 0.99 |
| Sentiment (3 classes) | 0.69 | 0.68 |

The intent score is very high partly because Bitext is synthetic and templated, so it overstates real-world performance. Sentiment is lower because Reddit emotions are ambiguous and the model is simple.

## Project structure

```
app.py                  Streamlit chat interface
api/main.py             FastAPI endpoint (POST /chat)
bot/
  text_utils.py         text cleaning and emotion -> sentiment mapping
  train.py              trains and saves both models
  export_responses.py   exports sample replies to models/responses.json
  predict.py            analyse() and respond() logic
  logger.py             writes conversations to the warehouse
  pipeline.py           handle_message(): respond + log
dbt_chatbot/            dbt project (staging and mart models)
scripts/                data loading, inspection and reporting scripts
models/                 trained models and sample replies
```

## Run it locally (Windows PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install duckdb pandas datasets dbt-duckdb scikit-learn streamlit fastapi uvicorn

python scripts\load_raw.py                 # download datasets into DuckDB
cd dbt_chatbot
dbt run --profiles-dir .                   # clean into the messages table
cd ..
python -m bot.train                        # train and save models
python -m bot.export_responses             # save sample replies
streamlit run app.py                       # open the chat at http://localhost:8501
```

Optional extras:
- API: `uvicorn api.main:app --reload`, then open http://127.0.0.1:8000/docs
- Conversation report: `python scripts\report.py`

## Notes on the deployed version

- Conversation logs on Streamlit Community Cloud are temporary because the server's disk resets on restart. The local warehouse is the permanent record.
- Please do not enter personal information into the public demo.

## Possible next steps

- Conversation memory (remember that the bot asked for an order number) and an `orders` table in the warehouse for real lookups.
- A "what can you do?" help rule.
- Fine-tune a pretrained transformer (for example DistilBERT) and compare it with this baseline.
- A dbt model that summarises logged conversations by day, intent and route.
