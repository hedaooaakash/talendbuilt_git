from datetime import datetime

from app.database.oracle import get_connection


def run_pipeline(pipeline_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Create execution record

    cursor.execute("""
        INSERT INTO JOB_EXECUTIONS
        (
            PIPELINE_ID,
            STATUS,
            STARTED_AT
        )
        VALUES
        (
            :1,
            'RUNNING',
            :2
        )
    """,
    [
        pipeline_id,
        datetime.now()
    ])

    conn.commit()

    # Get execution id

    cursor.execute("""
        SELECT MAX(ID)
        FROM JOB_EXECUTIONS
    """)

    execution_id = cursor.fetchone()[0]

    try:

        print(
            f"\nExecuting Pipeline {pipeline_id}"
        )

        cursor.execute("""
            SELECT
                STEP_ORDER,
                STEP_TYPE,
                CONFIG_JSON
            FROM PIPELINE_STEPS
            WHERE PIPELINE_ID = :1
            ORDER BY STEP_ORDER
        """,
        [pipeline_id])

        steps = cursor.fetchall()

        for step in steps:

            step_order = step[0]
            step_type = step[1]

            print(
                f"Executing Step {step_order}: "
                f"{step_type}"
            )

        print("\nPipeline Completed")

        cursor.execute("""
            UPDATE JOB_EXECUTIONS
            SET
                STATUS='SUCCESS',
                COMPLETED_AT=:1,
                MESSAGE='Pipeline completed successfully'
            WHERE ID=:2
        """,
        [
            datetime.now(),
            execution_id
        ])

        conn.commit()

    except Exception as e:

        cursor.execute("""
            UPDATE JOB_EXECUTIONS
            SET
                STATUS='FAILED',
                COMPLETED_AT=:1,
                MESSAGE=:2
            WHERE ID=:3
        """,
        [
            datetime.now(),
            str(e),
            execution_id
        ])

        conn.commit()

        raise

    finally:

        cursor.close()
        conn.close()