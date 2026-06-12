from app.database.oracle import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE EMPLOYEE (
    ID NUMBER GENERATED ALWAYS AS IDENTITY,
    EMP_NAME VARCHAR2(100),
    DEPARTMENT VARCHAR2(100),
    SALARY NUMBER,
    PRIMARY KEY(ID)
)
""")

cursor.execute("""
INSERT INTO EMPLOYEE
(EMP_NAME, DEPARTMENT, SALARY)
VALUES
('John', 'IT', 400)
""")

cursor.execute("""
INSERT INTO EMPLOYEE
(EMP_NAME, DEPARTMENT, SALARY)
VALUES
('Mike', 'IT', 300)
""")

cursor.execute("""
INSERT INTO EMPLOYEE
(EMP_NAME, DEPARTMENT, SALARY)
VALUES
('David', 'HR', 450)
""")

cursor.execute("""
INSERT INTO EMPLOYEE
(EMP_NAME, DEPARTMENT, SALARY)
VALUES
('Sara', 'HR', 700)
""")

cursor.execute("""
INSERT INTO EMPLOYEE
(EMP_NAME, DEPARTMENT, SALARY)
VALUES
('Tom', 'FINANCE', 200)
""")

conn.commit()

print("EMPLOYEE table created and sample data loaded")

cursor.close()
conn.close()