from app.database.oracle import get_connection
from app.etl.sql_service import (
    generate_sql_for_pipeline
)


def execute_pipeline_sql(
    pipeline_id: int
):

    sql = generate_sql_for_pipeline(
        pipeline_id
    )

    print("\nGenerated SQL:\n")
    print(sql)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows