import streamlit as st
from utils.file_loader import load_file
from utils.formatter import concat_columns
from db.oracle_connector import get_engine, ensure_table, insert_data
from analysis.trends import plot_trends

st.title("AI Data Integration Tool")

file = st.file_uploader("Upload .txt or .csv file", type=["txt","csv"])
if file:
    data = load_file(file)
    st.dataframe(data)

    col1 = st.selectbox("Column 1", data.columns)
    col2 = st.selectbox("Column 2", data.columns)
    out_col = st.text_input("Output Column", value="full_name")

    if st.button("Apply Expression"):
        data = concat_columns(data, col1, col2, out_col)
        st.dataframe(data)

    # Oracle connection
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    host = st.text_input("Host", value="DESKTOP-PIHJ28H.bbrouter")
    port = st.text_input("Port", value="1521")
    service = st.text_input("Service Name", value="XEPDB1")
    table_name = st.text_input("Table Name", value="test2")

    if st.button("Push to Oracle"):
        try:
            engine = get_engine(user, password, host, port, service)
            ensure_table(engine, table_name, data)
            insert_data(engine, table_name, data)
            st.success(f"✅ Data pushed to Oracle table {table_name}")
        except Exception as e:
            st.error(f"❌ Database Error: {str(e)}")

    # Trend analysis
    trend_cols = st.multiselect("Select columns for trend analysis", data.columns)
    if trend_cols:
        plot_trends(data, trend_cols)