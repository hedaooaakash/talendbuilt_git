from app.database.oracle import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM EMPLOYEE
""")

for row in cursor:
    print(row)

cursor.close()
conn.close()