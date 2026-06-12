from app.etl.sql_executor import (
    execute_pipeline_sql
)

# Use the pipeline ID that contains:
# EXTRACT_ORACLE
# FILTER
# AGGREGATE
# LOAD_POSTGRES

result = execute_pipeline_sql(5)

print("\nResults:\n")

for row in result:
    print(row)