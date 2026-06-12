from app.etl.sql_service import (
    generate_sql_for_pipeline
)

sql = generate_sql_for_pipeline(5)

print(sql)