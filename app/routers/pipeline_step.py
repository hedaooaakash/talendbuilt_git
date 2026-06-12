from fastapi import APIRouter

from app.database.oracle import get_connection
from app.models.pipeline_step import PipelineStepCreate

router = APIRouter(
    prefix="/pipeline-steps",
    tags=["Pipeline Steps"]
)

@router.get("/{pipeline_id}")
def get_pipeline_steps(pipeline_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ID,
            STEP_ORDER,
            STEP_TYPE,
            CONFIG_JSON
        FROM PIPELINE_STEPS
        WHERE PIPELINE_ID = :1
        ORDER BY STEP_ORDER
    """,
    [pipeline_id])

    result = []

    for row in cursor.fetchall():

        config_json = row[3]

        if config_json:
            config_json = config_json.read()

        result.append({
            "id": row[0],
            "step_order": row[1],
            "step_type": row[2],
            "config_json": config_json
        })

    cursor.close()
    conn.close()

    return result