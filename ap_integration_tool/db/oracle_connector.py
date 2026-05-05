from sqlalchemy import create_engine, inspect, text

def get_engine(user, password, host, port, service):
    return create_engine(f"oracle+oracledb://{user}:{password}@{host}:{port}/?service_name={service}")

def ensure_table(engine, table_name, data):
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    with engine.begin() as conn:
        if table_name in existing_tables:
            conn.execute(text(f"TRUNCATE TABLE {table_name}"))
        else:
            create_query = f"""
                CREATE TABLE {table_name} (
                    {', '.join([f"{col} VARCHAR2(255)" for col in data.columns])}
                )
            """
            conn.execute(text(create_query))

def insert_data(engine, table_name, data):
    with engine.begin() as conn:
        for _, row in data.iterrows():
            insert_query = f"""
                INSERT INTO {table_name} ({', '.join(data.columns)})
                VALUES ({', '.join([':' + col for col in data.columns])})
            """
            conn.execute(text(insert_query), {col: row[col] for col in data.columns})