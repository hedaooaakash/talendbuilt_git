from app.database.oracle import get_connection

conn = get_connection()
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE PIPELINES
        ADD (
            DESCRIPTION VARCHAR2(500),
            CREATED_BY NUMBER
        )
    """)

    conn.commit()
    print("PIPELINES table updated successfully")

except Exception as e:
    print("Error:", e)

finally:
    cursor.close()
    conn.close()