import sqlite3

conn = sqlite3.connect("data/bot.db")
conn.row_factory = sqlite3.Row

print("\n====== LEADS REPORT ======\n")

leads = conn.execute("""
    SELECT l.id, l.problem_type, l.summary, l.created_at, 
           u.username, u.first_name
    FROM leads l
    LEFT JOIN users u ON l.user_id = u.user_id
    ORDER BY l.created_at DESC
    LIMIT 20
""").fetchall()

for lead in leads:
    print(f"ID:       {lead['id']}")
    print(f"Name:     {lead['first_name']} (@{lead['username']})")
    print(f"Topic:    {lead['problem_type']}")
    print(f"Message:  {lead['summary'][:100]}")
    print(f"Date:     {lead['created_at']}")
    print("-" * 40)

stats = conn.execute("""
    SELECT problem_type, COUNT(*) as count 
    FROM leads 
    GROUP BY problem_type 
    ORDER BY count DESC
""").fetchall()

print("\n====== TOPIC BREAKDOWN ======\n")
for s in stats:
    print(f"{s['problem_type']:20} — {s['count']} conversations")

conn.close()
