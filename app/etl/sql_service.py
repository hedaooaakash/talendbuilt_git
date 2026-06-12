import json

from app.database.oracle import get_connection
from app.etl.sql_generator import generate_sql


def generate_sql_for_pipeline(
    pipeline_id: int
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            STEP_TYPE,
            CONFIG_JSON
        FROM PIPELINE_STEPS
        WHERE PIPELINE_ID = :1
        ORDER BY STEP_ORDER
    """,
    [pipeline_id])

    rows = cursor.fetchall()

    steps = []

    for row in rows:

        step_type = row[0]

        config = row[1]

        if config:
            config = config.read()

        try:
            config_json = json.loads(
                config
            )
        except:
            config_json = {}

        steps.append({
            "step_type": step_type,
            "config_json": config_json
        })

    cursor.close()
    conn.close()

    sql = generate_sql(steps)

    return sql