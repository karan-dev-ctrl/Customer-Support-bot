import duckdb

con = duckdb.connect("warehouse/chatbot.duckdb", read_only=True)

print("Routes:")
print(con.execute(
    "SELECT route, count(*) AS n FROM logs.conversations GROUP BY 1 ORDER BY n DESC").df())

print("\nTop intents handled:")
print(con.execute("""
    SELECT intent, count(*) AS n, round(avg(intent_conf), 2) AS avg_conf
    FROM logs.conversations WHERE route = 'intent'
    GROUP BY 1 ORDER BY n DESC""").df())

print("\nEscalation rate (%):")
print(con.execute("""
    SELECT round(100.0 * count(*) FILTER (WHERE route = 'escalate') / count(*), 1) AS pct
    FROM logs.conversations""").df())

print("\nLatest 10:")
print(con.execute(
    "SELECT ts, message, route, intent FROM logs.conversations ORDER BY ts DESC LIMIT 10").df())