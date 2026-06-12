from app.ai.pipeline_service import create_pipeline_from_prompt

result = create_pipeline_from_prompt(
    """
    Read employee data from Oracle.
    Filter salary less than 500.
    Get max salary by department.
    Load to PostgreSQL.
    """
)

print(result)