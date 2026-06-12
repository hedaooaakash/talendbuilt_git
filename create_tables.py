from app.database.oracle import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE users (
    id NUMBER GENERATED ALWAYS AS IDENTITY,
    email VARCHAR2(255) UNIQUE,
    password_hash VARCHAR2(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id)
)
""")

cursor.execute("""
CREATE TABLE pipelines (
    id NUMBER GENERATED ALWAYS AS IDENTITY,
    name VARCHAR2(255),
    source_type VARCHAR2(100),
    target_type VARCHAR2(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id)
)
""")

cursor.execute("""
CREATE TABLE jobs (
    id NUMBER GENERATED ALWAYS AS IDENTITY,
    pipeline_id NUMBER,
    status VARCHAR2(50),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    PRIMARY KEY(id)
)
""")

try:
    conn.commit()
    print("Tables Created Successfully")
finally:
    try:
        cursor.close()
    except:
        pass

    try:
        conn.close()
    except:
        pass