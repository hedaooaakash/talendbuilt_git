import os
import time
import pandas as pd
import subprocess
from sqlalchemy import create_engine, text

# Oracle connection string
ORACLE_CONN = "oracle+oracledb://aakash:admin@DESKTOP-PIHJ28H.bbrouter:1521/?service_name=XEPDB1"
engine = create_engine(ORACLE_CONN)

# ----------------------------
# Task Flow Functions
# ----------------------------

def run_plsql(conn, block):
    try:
        conn.execute(text(block))
        return True, None
    except Exception as e:
        return False, str(e)

def run_linux(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        success = (result.returncode == 0)
        return success, {"stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except Exception as e:
        return False, {"stdout": None, "stderr": str(e)}

def execute_task(conn, task_id, task_name, flow_run_id, flow_id):
    task = conn.execute(text("""
        SELECT task_type, task_command, exec_condition
        FROM DMF_TASK_MSTR
        WHERE task_id=:tid
    """), {"tid": task_id}).fetchone()
    if not task:
        return "Failed", f"Task {task_id} not found"

    task_type, task_command, exec_condition = task
    print(f"▶️ Executing Task {task_name} ({task_type})")

    status, stdout_val, stderr_val, error_val = None, None, None, None

    # 🔎 Step 1: Evaluate EXEC_CONDITION
    if exec_condition:
    try:
        result = conn.execute(text(exec_condition)).scalar()
        normalized = str(result).strip().upper() if result else "CANCEL"
        if normalized not in ("1", "PROCEED", "TRUE"):
            status = "Cancelled"
            error_val = "Cancelled by EXEC_CONDITION"

            print(f"🛑 Logging Cancelled task {task_id} ({task_name})")

            conn.execute(text("""
                INSERT INTO DMF_TASK_LOG (
                    task_id, task_name, status, start_time, end_time,
                    error_message, stdout_message, stderr_message,
                    flow_run_id, flow_id
                )
                VALUES (:tid, :tname, :status, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
                        :c_err, NULL, NULL, :run_id, :flow_id)
            """), {
                "tid": task_id,
                "tname": task_name,
                "status": status,
                "c_err": error_val,
                "run_id": flow_run_id,
                "flow_id": flow_id
            })

            print("✅ Cancelled log inserted into DMF_TASK_LOG")
            return status, error_val
    except Exception as e:
        status = "Failed"
        error_val = f"EXEC_CONDITION evaluation failed: {e}"

    # 🔎 Step 2: Run task if not cancelled/failed
    if not status:
        if task_type.upper() == "PLSQL":
            success, msg = run_plsql(conn, task_command)
        elif task_type.upper() == "LINUX":
            success, msg = run_linux(task_command)
        else:
            success, msg = False, f"Unknown task type {task_type}"

        if isinstance(msg, dict):
            stdout_val = msg.get("stdout")
            stderr_val = msg.get("stderr")
            error_val = stderr_val if not success else None
        else:
            error_val = msg

        status = "Success" if success else "Failed"

        # Unified logging for Success/Fail
        conn.execute(text("""
            INSERT INTO DMF_TASK_LOG (
                task_id, task_name, status, start_time, end_time,
                error_message, stdout_message, stderr_message,
                flow_run_id, flow_id
            )
            VALUES (:tid, :tname, :status, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
                    :c_err, :stdout, :stderr, :run_id, :flow_id)
        """), {
            "tid": task_id,
            "tname": task_name,
            "status": status,
            "c_err": error_val,
            "stdout": stdout_val,
            "stderr": stderr_val,
            "run_id": flow_run_id,
            "flow_id": flow_id
        })

    return status, error_val or "OK"



# ----------------------------
# Flow Execution
# ----------------------------

def run_flow(conn, flow_id):
    flow_run_id = conn.execute(text("SELECT DMF_FLOW_LOG_SEQ.NEXTVAL FROM dual")).scalar()
    WF_NAME = conn.execute(text("SELECT WF_NAME FROM DMF_TASK_FLOW WHERE flow_id=:fid"),
                           {"fid": flow_id}).scalar()

    print(f"🚀 Starting flow '{WF_NAME}' (flow_id={flow_id}, run_id={flow_run_id})")

    conn.execute(text("""
        INSERT INTO DMF_FLOW_LOG (flow_run_id, flow_id, status, start_time)
        VALUES (:run_id, :fid, 'In Progress', CURRENT_TIMESTAMP)
    """), {"run_id": flow_run_id, "fid": flow_id})

    sequence_no = 1
    current = conn.execute(text("""
        SELECT task_id, task_name, on_success, on_success_name, on_fail, on_fail_name, label
        FROM DMF_TASK_FLOW_SEQUENCE
        WHERE flow_id=:fid AND sequence_no=:seq
    """), {"fid": flow_id, "seq": sequence_no}).fetchone()

    while current:
        task_id, task_name, on_success, on_success_name, on_fail, on_fail_name, label = current
        status, msg = execute_task(conn, task_id, task_name, flow_run_id, flow_id)

        if status in ("Success", "Cancelled"):
            if status == "Cancelled":
                print(f"➡️ Task cancelled, continuing to next: {on_success_name}")
            else:
                print(f"➡️ Next task (success): {on_success_name}")

            if on_success:
                current = conn.execute(text("""
                    SELECT task_id, task_name, on_success, on_success_name, on_fail, on_fail_name, label
                    FROM DMF_TASK_FLOW_SEQUENCE
                    WHERE flow_id=:fid AND task_id=:tid
                """), {"fid": flow_id, "tid": on_success}).fetchone()
            else:
                current = None

        elif status == "Failed":
            if on_fail:
                print(f"➡️ Next task (fail): {on_fail_name}")
                current = conn.execute(text("""
                    SELECT task_id, task_name, on_success, on_success_name, on_fail, on_fail_name, label
                    FROM DMF_TASK_FLOW_SEQUENCE
                    WHERE flow_id=:fid AND task_id=:tid
                """), {"fid": flow_id, "tid": on_fail}).fetchone()
            else:
                current = None

        # 🚦 Check END after navigation
        if label and label.upper() == "END":
            print(f"🏁 Flow terminated at task: {task_name} (label=END)")
            current = None

    conn.execute(text("""
        UPDATE DMF_FLOW_LOG
        SET status='Completed', end_time=CURRENT_TIMESTAMP
        WHERE flow_run_id=:run_id
    """), {"run_id": flow_run_id})

    print(f"🏁 Flow '{WF_NAME}' (flow_id={flow_id}, run_id={flow_run_id}) has ended.")


def run_flow_by_name(conn, wf_name):
    flow_id = conn.execute(text("""
        SELECT flow_id FROM DMF_TASK_FLOW WHERE WF_NAME=:fname
    """), {"fname": wf_name}).scalar()
    if not flow_id:
        print(f"❌ Flow '{wf_name}' not found.")
        return
    run_flow(conn, flow_id)

# ----------------------------
# Flow Trigger Functions
# ----------------------------
def poll_flow_triggers(conn):
    triggers = conn.execute(text("""
        SELECT trigger_id, wf_name, fk_event_id
        FROM DMF_FLOW_TRIGGER
        WHERE status='Pending'
    """)).fetchall()

    for trigger_id, wf_name, fk_event_id in triggers:
        print(f"🚀 Trigger received for workflow: {wf_name} (event {fk_event_id})")
        try:
            run_flow_by_name(conn, wf_name)
            conn.execute(text("""
                UPDATE DMF_FLOW_TRIGGER
                SET status='Completed', trigger_time=CURRENT_TIMESTAMP
                WHERE trigger_id=:tid
            """), {"tid": trigger_id})
        except Exception as e:
            conn.execute(text("""
                UPDATE DMF_FLOW_TRIGGER
                SET status='Failed', trigger_time=CURRENT_TIMESTAMP
                WHERE trigger_id=:tid
            """), {"tid": trigger_id})
            print(f"❌ Workflow {wf_name} failed for event {fk_event_id}: {e}")



# ----------------------------
# File Event Functions
# ----------------------------

def poll_file_events(conn):
    jobs = conn.execute(text("""
        SELECT id, file_name, file_location, target_table, on_demand_run_ind,
               use_explicit_header, file_headers
        FROM file_evnt_subcr
        WHERE status='Ready' OR on_demand_run_ind='Y'
        FOR UPDATE SKIP LOCKED
    """)).fetchall()

    for job_id, file_name, file_location, target_table, on_demand, use_explicit, file_headers in jobs:
        print(f"📂 Processing file event {file_name} -> {target_table}")

        # 🔎 Step 1: Check EM_ACTN for workflow mapping
        actn = conn.execute(text("""
            SELECT wf_name, exec_condition, status, description
            FROM EM_ACTN
            WHERE fk_event_id=:eid
        """), {"eid": job_id}).fetchone()

        if actn:
            wf_name, exec_condition, status, description = actn
            proceed = True
            if exec_condition:
                try:
                    result = conn.execute(text(exec_condition)).scalar()
                    proceed = (str(result).upper() == "PROCEED")
                except Exception as e:
                    print(f"❌ Condition evaluation failed: {e}")
                    proceed = False

            if proceed:
                print(f"🚀 Inserting trigger for workflow {wf_name} (event {job_id})")
                conn.execute(text("""
                    INSERT INTO DMF_FLOW_TRIGGER (wf_name, fk_event_id, run_type, status)
                    VALUES (:wf, :eid, 'FILE_DRIVEN', 'Pending')
                """), {"wf": wf_name, "eid": job_id})
                conn.execute(text("""
                    UPDATE file_evnt_subcr
                    SET status='Triggered', on_demand_run_ind='N'
                    WHERE id=:sid
                """), {"sid": job_id})
                continue
            else:
                print(f"⏭️ Workflow {wf_name} skipped for event {job_id}")
                continue

        # 🔎 Step 2: No workflow configured → fallback to direct file load
        try:
            conn.execute(text("UPDATE file_evnt_subcr SET status='Processing' WHERE id=:sid"), {"sid": job_id})
            file_path = os.path.join(file_location, file_name)

            run_type = "On-Demand" if on_demand == 'Y' else "Scheduled"
            conn.execute(text("""
                INSERT INTO subcr_evnt_log (subcr_id, run_type, status, start_time, filename, file_location)
                VALUES (:sid, :rtype, 'In Progress', CURRENT_TIMESTAMP, :fname, :floc)
            """), {"sid": job_id, "rtype": run_type, "fname": file_name, "floc": file_location})

            if use_explicit and use_explicit.upper() == 'Y' and file_headers:
                header_list = [h.strip() for h in file_headers.split(",")]
                df = pd.read_csv(file_path, delimiter="|", header=None, skiprows=1)

                if len(header_list) <= df.shape[1]:
                    df = df.iloc[:, :len(header_list)]
                    df.columns = header_list
                else:
                    df = df.iloc[:, :df.shape[1]]
                    df.columns = header_list[:df.shape[1]]
                    for extra_col in header_list[df.shape[1]:]:
                        df[extra_col] = None

                print(f"🔖 Using explicit headers: {header_list}")
            else:
                df = pd.read_csv(file_path, delimiter="|")
                print("📑 Using file’s own header row")

            exists = conn.execute(text("SELECT COUNT(*) FROM all_tables WHERE table_name = :tname"), {"tname": target_table.upper()}).scalar()
            if exists == 0:
                cols = ", ".join([f"{col} VARCHAR2(255)" for col in df.columns])
                create_sql = f"CREATE TABLE {target_table} ({cols})"
                conn.execute(text(create_sql))
                print(f"🆕 Created table {target_table}")
            else:
                existing_cols = [r[0] for r in conn.execute(text("SELECT column_name FROM all_tab_columns WHERE table_name=:tname"), {"tname": target_table.upper()}).fetchall()]
                for col in df.columns:
                    if col.upper() not in existing_cols:
                        alter_sql = f"ALTER TABLE {target_table} ADD ({col} VARCHAR2(255))"
                        conn.execute(text(alter_sql))
                        print(f"➕ Added new column {col} to {target_table}")

            columns = list(df.columns)
            cols = ",".join(columns)
            placeholders = ",".join([f":c{i}" for i in range(1, len(columns)+1)])
            insert_sql = f"INSERT INTO {target_table} ({cols}) VALUES ({placeholders})"
            for row in df.to_dict(orient="records"):
                params = {f"c{i+1}": row[col] for i, col in enumerate(columns)}
                conn.execute(text(insert_sql), params)

            conn.execute(text("UPDATE file_evnt_subcr SET status='Completed', on_demand_run_ind='N' WHERE id=:sid"), {"sid": job_id})
            conn.execute(text("""
                UPDATE subcr_evnt_log
                SET status='Success', end_time=CURRENT_TIMESTAMP, rows_processed=:c_rows, error_message=NULL
                WHERE subcr_id=:sid AND status='In Progress'
            """), {"c_rows": len(df), "sid": job_id})

            print(f"✅ File {file_name} loaded successfully")

        except Exception as e:
            conn.execute(text("UPDATE file_evnt_subcr SET status='Failed', on_demand_run_ind='N' WHERE id=:sid"), {"sid": job_id})
            conn.execute(text("""
                UPDATE subcr_evnt_log
                SET status='Failed', end_time=CURRENT_TIMESTAMP, error_message=:c_err
                WHERE subcr_id=:sid AND status='In Progress'
            """), {"c_err": str(e), "sid": job_id})
            print(f"❌ File {file_name} failed: {e}")

# ----------------------------
# Unified Polling Loop
# ----------------------------
def poll_and_run():
    while True:
        with engine.begin() as conn:
            poll_flow_triggers(conn)
            poll_file_events(conn)
        time.sleep(10)


if __name__ == "__main__":
    print("🕒 Unified Scheduler started. Polling every 10 seconds...")
    poll_and_run()