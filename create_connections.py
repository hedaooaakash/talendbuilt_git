from app.database.oracle import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE CONNECTIONS (
    ID NUMBER GENERATED ALWAYS AS IDENTITY,
    NAME VARCHAR2(100) NOT NULL,
    TYPE VARCHAR2(50) NOT NULL,
    HOST VARCHAR2(255),
    PORT NUMBER,
    USERNAME VARCHAR2(255),
    PASSWORD VARCHAR2(255),
    DATABASE_NAME VARCHAR2(255),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(ID)
)
""")

conn.commit()

print("CONNECTIONS table created successfully")

cursor.close()
conn.close()