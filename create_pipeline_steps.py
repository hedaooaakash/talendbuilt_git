from app.database.oracle import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE PIPELINE_STEPS (
    ID NUMBER GENERATED ALWAYS AS IDENTITY,
    PIPELINE_ID NUMBER NOT NULL,
    STEP_ORDER NUMBER NOT NULL,
    STEP_TYPE VARCHAR2(100) NOT NULL,
    CONFIG_JSON CLOB,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(ID)
)
""")

conn.commit()

print("PIPELINE_STEPS table created successfully")

cursor.close()
conn.close()