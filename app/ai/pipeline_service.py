import json

from app.database.oracle import get_connection
from app.ai.pipeline_generator import generate_pipeline


def create_pipeline_from_prompt(prompt: str):

    generated = generate_pipeline(prompt)

    conn = get_connection()
    cursor = conn.cursor()

    # Create pipeline

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
        generated["pipeline_name"],
        prompt,
        generated["source_type"],
        generated["target_type"],
        1
    ])

    conn.commit()

    # Get pipeline id

    cursor.execute("""
        SELECT MAX(ID)
        FROM PIPELINES
    """)

    pipeline_id = cursor.fetchone()[0]

    # Create steps

    for step in generated["steps"]:

        cursor.execute("""
            INSERT INTO PIPELINE_STEPS
            (
                PIPELINE_ID,
                STEP_ORDER,
                STEP_TYPE,
                CONFIG_JSON
            )
            VALUES
            (
                :1,
                :2,
                :3,
                :4
            )
        """,
        [
            pipeline_id,
            step["step_order"],
            step["step_type"],
            json.dumps(
                step.get("config_json", {})
            )
        ])

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "pipeline_id": pipeline_id,
        "message": "AI pipeline created successfully"
    }