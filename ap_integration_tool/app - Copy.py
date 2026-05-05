import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect, text
import matplotlib.pyplot as plt
import seaborn as sns

st.title("AI Data Integration Tool")

# File upload
file = st.file_uploader("Upload .txt or .csv file", type=["txt", "csv"])
if file:
    data = pd.read_csv(file, sep='|', engine='python')
    st.write("Data Preview:")
    st.dataframe(data)

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
                # Truncate table
                with engine.connect() as conn:
                    conn.execute(text(f"TRUNCATE TABLE {table_name}"))
                    conn.commit()
                    st.write(f"Table {table_name} truncated")
            else:
                # Create table
                with engine.connect() as conn:
                    create_query = f"""
                        CREATE TABLE {table_name} (
                            {', '.join([f"{col} VARCHAR2(255)" for col in data.columns])}
                        )
                    """
                    conn.execute(text(create_query))
                    conn.commit()
                    st.write(f"Table {table_name} created")

            # Insert data
            with engine.connect() as conn:
                for index, row in data.iterrows():
                    insert_query = f"""
                        INSERT INTO {table_name} ({', '.join(data.columns)})
                        VALUES ({', '.join([':' + col for col in data.columns])})
                    """
                    params = {col: row[col] for col in data.columns}
                    conn.execute(text(insert_query), params)
                    conn.commit()
            st.success(f"✅ Data pushed to Oracle table {table_name}")

            # Get columns
            columns = list(data.columns)

            # Select columns for trend analysis
            trend_cols = st.multiselect("Select columns for trend analysis", columns)

            # Plot trends
            if trend_cols:
                for col in trend_cols:
                    st.write(f"Trend for {col}:")
                    plt.figure(figsize=(10, 6))
                    sns.lineplot(data=data[col])
                    plt.title(f"Trend for {col}")
                    plt.xlabel("Index")
                    plt.ylabel(col)
                    st.pyplot()

            # Select columns for correlation analysis
            corr_cols = st.multiselect("Select columns for correlation analysis", columns)

            # Plot correlations
            if corr_cols:
                corr_matrix = data[corr_cols].corr()
                st.write("Correlation Matrix:")
                st.write(corr_matrix)
                plt.figure(figsize=(10, 6))
                sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", square=True)
                plt.title("Correlation Matrix")
                st.pyplot()

            # Select column for histogram
            hist_col = st.selectbox("Select column for histogram", columns)

            # Plot histogram
            if hist_col:
                st.write(f"Histogram for {hist_col}:")
                plt.figure(figsize=(10, 6))
                sns.histplot(data[hist_col], kde=True)
                plt.title(f"Histogram for {hist_col}")
                plt.xlabel(hist_col)
                plt.ylabel("Count")
                st.pyplot()

        except Exception as e:
            st.error(f"❌ Database Error: {str(e)}")