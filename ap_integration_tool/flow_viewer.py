import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
import time

# Oracle connection
ORACLE_CONN = "oracle+oracledb://aakash:admin@DESKTOP-PIHJ28H.bbrouter:1521/?service_name=XEPDB1"
engine = create_engine(ORACLE_CONN)

st.set_page_config(page_title="DMF Flow Monitor", layout="wide")
st.title("🧭 DMF Task Flow Monitor")

# Sidebar controls
st.sidebar.header("⚙️ Options")
selected_flow = st.sidebar.text_input("Flow Name", "DataPipeline")
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 10, 120, 30)

# Helper to load data
def load_data(flow_name):
    with engine.begin() as conn:
        df_flow = pd.read_sql("""
            SELECT f.flow_name, f.sequence_no, f.task_id, m.task_name, m.task_type,
                   f.on_success, f.on_fail
            FROM DMF_TASK_FLOW f
            JOIN DMF_TASK_MSTR m ON f.task_id = m.task_id
            WHERE f.flow_name = :fname
            ORDER BY f.sequence_no
        """, conn, params={"fname": flow_name})

        df_log = pd.read_sql("""
            SELECT task_id, status, flow_run_id, start_time, end_time
            FROM DMF_TASK_LOG
            WHERE flow_run_id = (SELECT MAX(flow_run_id) FROM DMF_TASK_LOG)
        """, conn)

    return df_flow, df_log

# Simple left-to-right layout (no pygraphviz)
def horizontal_layout(G):
    nodes = list(G.nodes())
    pos = {}
    spacing_x = 3
    spacing_y = 0
    for i, node in enumerate(nodes):
        pos[node] = (i * spacing_x, spacing_y)
    return pos

# Main loop for auto-refresh
while True:
    df_flow, df_log = load_data(selected_flow)
    df = pd.merge(df_flow, df_log, on="task_id", how="left")

    # Build graph safely
    G = nx.DiGraph()
    for _, row in df.iterrows():
        task_label = row.get("task_name", f"Task {row['task_id']}")
        color = "lightgray"
        if row.get("status") == "Success":
            color = "lightgreen"
        elif row.get("status") == "Failed":
            color = "salmon"
        elif row.get("status") == "Running":
            color = "gold"

        G.add_node(row["task_id"], label=task_label, color=color)

        if pd.notna(row["on_success"]):
            G.add_edge(row["task_id"], int(row["on_success"]), label="Success", color="green")
        if pd.notna(row["on_fail"]):
            G.add_edge(row["task_id"], int(row["on_fail"]), label="Fail", color="red")

    # Draw clean horizontal graph
    pos = horizontal_layout(G)
    plt.figure(figsize=(12, 4))
    nx.draw(
        G, pos,
        with_labels=True,
        labels={n: G.nodes[n].get("label", str(n)) for n in G.nodes},
        node_color=[G.nodes[n]["color"] for n in G.nodes],
        node_size=3000,
        font_size=10,
        font_weight="bold",
        edge_color=[G.edges[e]["color"] for e in G.edges],
        arrows=True,
        arrowstyle="-|>",
        arrowsize=15
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d["label"] for u, v, d in G.edges(data=True)})
    st.pyplot(plt)

    # Summary panel
    st.subheader("📊 Run Summary")
    total = len(df_log)
    success = (df_log["status"] == "Success").sum()
    failed = (df_log["status"] == "Failed").sum()
    running = (df_log["status"] == "Running").sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tasks", total)
    col2.metric("✅ Success", success)
    col3.metric("❌ Failed", failed)
    col4.metric("⏳ Running", running)

    # Log table
    st.subheader("📋 Latest Run Details")
    st.dataframe(df_log.sort_values("start_time", ascending=False))

    if not auto_refresh:
        break
    time.sleep(refresh_interval)
    st.rerun()
