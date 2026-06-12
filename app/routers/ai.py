from fastapi import APIRouter

from app.models.ai import PromptRequest

from app.ai.pipeline_service import (
    create_pipeline_from_prompt
)

from app.etl.sql_service import (
    generate_sql_for_pipeline
)

from app.etl.sql_executor import (
    execute_pipeline_sql
)

router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.post("/generate-pipeline")
def generate_pipeline(
    request: PromptRequest
):

    return create_pipeline_from_prompt(
        request.prompt
    )


@router.post("/generate-sql/{pipeline_id}")
def generate_sql(
    pipeline_id: int
):

    sql = generate_sql_for_pipeline(
        pipeline_id
    )

    return {
        "pipeline_id": pipeline_id,
        "sql": sql
    }


@router.post("/execute/{pipeline_id}")
def execute_pipeline(
    pipeline_id: int
):

    rows = execute_pipeline_sql(
        pipeline_id
    )

    return {
        "pipeline_id": pipeline_id,
        "rows": rows
    }