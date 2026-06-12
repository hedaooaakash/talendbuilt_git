from app.ai.pipeline_generator import generate_pipeline

result = generate_pipeline(
    """
    Read employee data from Oracle.
    Filter salary less than 500.
    Get max salary by department.
    Load to PostgreSQL.
    """
)

print(result)