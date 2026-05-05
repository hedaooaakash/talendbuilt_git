import streamlit as st
import pandas as pd
import time
from sqlalchemy import create_engine, inspect, text
import matplotlib.pyplot as plt
import seaborn as sns

# Import tracker functions
from tracker import init_db, log_file_upload

# Initialize DB
init_db()

st.title("AI Data Integration Tool")

# File upload
file = st.file_uploader("Upload .txt or .csv file", type=["txt", "csv"])
if file:
    # Read file
    data = pd.read_csv(file, sep='|', engine='python')
    rows = len(data)

    # Log upload to tracker
    filename = file.name
    log_file_upload(filename, "Success", rows)

    # Monitor section
    st.subheader("📊 Load Monitor")
    st.success(f"✅ File '{filename}' uploaded successfully with {rows} rows.")

    # Data preview
    st.subheader("Data Preview")
    st.dataframe(data)

    # Format Component
    st.subheader("Format Component")
    cols = list(data.columns)
    col1 = st.selectbox("Column 1", cols)
    col2 = st.selectbox("Column 2", cols)
    out_col = st.text_input("Output Column", value="full_name")
    key = st.selectbox("Key Column", cols)

    if st.button("Apply Expression"):
        data[out_col] = data[col1].astype(str) + ' ' + data[col2].astype(str)
        st.write("Updated Data:")
        st.dataframe(data)

    # Oracle Connection Details
    st.subheader("Oracle Connection Details")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    host = st.text_input("Host", value="DESKTOP-PIHJ28H.bbrouter")
    port = st.text_input("Port", value="1521")
    service = st.text_input("Service Name", value="XEPDB1")
    table_name = st.text_input("Table Name", value="test2")

    if st.button("Push to Oracle"):
        try:
            engine = create_engine(f"oracle+oracledb://{user}:{password}@{host}:{port}/?service_name={service}")
            inspector = inspect(engine)

            # Check if table exists
            existing_tables = inspector.get_table_names()
            if table_name in existing_tables:
                with engine.begin() as conn:
                    conn.execute(text(f"TRUNCATE TABLE {table_name}"))
                    st.write(f"Table {table_name} truncated")
            else:
                with engine.begin() as conn:
                    create_query = f"""
                        CREATE TABLE {table_name} (
                            {', '.join([f"{col} VARCHAR2(255)" for col in data.columns])}
                        )
                    """
                    conn.execute(text(create_query))
                    st.write(f"Table {table_name} created")

            # Insert data
            with engine.begin() as conn:
                for _, row in data.iterrows():
                    insert_query = f"""
                        INSERT INTO {table_name} ({', '.join(data.columns)})
                        VALUES ({', '.join([':' + col for col in data.columns])})
                    """
                    params = {col: row[col] for col in data.columns}
                    conn.execute(text(insert_query), params)
            st.success(f"✅ Data pushed to Oracle table {table_name}")

            # Trend analysis
            columns = list(data.columns)
            trend_cols = st.multiselect("Select columns for trend analysis", columns)
            if trend_cols:
                for col in trend_cols:
                    st.write(f"Trend for {col}:")
                    plt.figure(figsize=(10, 6))
                    sns.lineplot(x=data.index, y=data[col])
                    plt.title(f"Trend for {col}")
                    st.pyplot()

            # Correlation analysis
            corr_cols = st.multiselect("Select columns for correlation analysis", columns)
            if corr_cols:
                corr_matrix = data[corr_cols].corr()
                st.write("Correlation Matrix:")
                st.write(corr_matrix)
                plt.figure(figsize=(10, 6))
                sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", square=True)
                plt.title("Correlation Matrix")
                st.pyplot()

        except Exception as e:
            st.error(f"❌ Database Error: {str(e)}")

    # System status
    st.subheader("⚙️ System Status")
    st.write("Oracle Connection: Awaiting credentials")
    st.write(f"Rows available for push: {rows}")
