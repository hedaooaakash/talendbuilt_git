from app.database.oracle import get_connection

PIPELINE_ID = 5

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT
    STEP_ORDER,
    STEP_TYPE,
    CONFIG_JSON
FROM PIPELINE_STEPS
WHERE PIPELINE_ID = :1
ORDER BY STEP_ORDER
""",
[PIPELINE_ID])

for row in cursor:

    config = row[2]

    if config:
        config = config.read()

    print(
        f"Step {row[0]} | "
        f"{row[1]} | "
        f"{config}"
    )

cursor.close()
conn.close()