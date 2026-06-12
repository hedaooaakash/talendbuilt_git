from app.database.oracle import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE JOB_EXECUTIONS (
    ID NUMBER GENERATED ALWAYS AS IDENTITY,
    PIPELINE_ID NUMBER,
    STATUS VARCHAR2(50),
    STARTED_AT TIMESTAMP,
    COMPLETED_AT TIMESTAMP,
    MESSAGE VARCHAR2(1000),
    PRIMARY KEY(ID)
)
""")

conn.commit()

print("JOB_EXECUTIONS table created")

cursor.close()
conn.close()