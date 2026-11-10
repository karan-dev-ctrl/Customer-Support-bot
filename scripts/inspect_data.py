import duckdb

con = duckdb.connect("warehouse/chatbot.duckdb")

print(con.execute("DESCRIBE raw.bitext").df())
print()
print(con.execute(
    "SELECT intent, count(*) AS n FROM raw.bitext GROUP BY 1 ORDER BY n DESC"
).df())
print()
print(con.execute("SELECT * FROM raw.goemotions LIMIT 5").df())


print(con.execute("SELECT source_dataset, count(*) AS n FROM messages GROUP BY 1").df())
print(con.execute("SELECT * FROM messages LIMIT 3").df())