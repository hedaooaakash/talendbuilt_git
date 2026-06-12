from app.database.oracle import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT table_name
FROM user_tables
ORDER BY table_name
""")

for row in cursor:
    print(row[0])

cursor.close()
conn.close()