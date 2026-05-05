import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

ORACLE_CONN = "oracle+oracledb://aakash:admin@DESKTOP-PIHJ28H.bbrouter:1521/?service_name=XEPDB1"

st.title("📊 ETL Job Monitor")

engine = create_engine(ORACLE_CONN)

def load_logs():
    query = """
        SELECT log_id, subcr_id, run_type, status,
               rows_processed, start_time, end_time, error_message
        FROM subcr_evnt_log
        ORDER BY log_id DESC
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

logs = load_logs()
st.dataframe(logs)
