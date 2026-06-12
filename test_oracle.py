from app.database.oracle import get_connection

conn = get_connection()

cursor = conn.cursor()

cursor.execute("SELECT SYSDATE FROM dual")

print(cursor.fetchone())

cursor.close()
conn.close()