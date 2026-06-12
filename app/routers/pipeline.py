from fastapi import APIRouter

from app.database.oracle import get_connection
from app.models.pipeline import PipelineCreate

router = APIRouter(
    prefix="/pipelines",
    tags=["Pipelines"]
)

@router.post("/")
def create_pipeline(pipeline: PipelineCreate):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO PIPELINES
        (
            NAME,
            DESCRIPTION,
            SOURCE_TYPE,
            TARGET_TYPE,
            CREATED_BY
        )
        VALUES
        (
            :1,
            :2,
            :3,
            :4,
            :5
        )
    """,
    [
        pipeline.name,
        pipeline.description,
        pipeline.source_type,
        pipeline.target_type,
        1
    ])

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Pipeline created successfully"
    }


@router.get("/")
def get_pipelines():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ID,
            NAME,
            DESCRIPTION,
            SOURCE_TYPE,
            TARGET_TYPE
        FROM PIPELINES
        ORDER BY ID
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows