from app.database.oracle import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT
    ID,
    PIPELINE_ID,
    STATUS,
    MESSAGE
FROM JOB_EXECUTIONS
ORDER BY ID
""")

for row in cursor:
    print(row)

cursor.close()
conn.close()