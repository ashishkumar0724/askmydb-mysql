# database.py
import mysql.connector
from mysql.connector import Error
import json
import streamlit as st
from config import DB_CONFIG

def connect_to_db():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
        else:
            st.error("Failed to establish database connection.")
            return None
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

def extract_schema():
    """Extracts the schema (tables and columns) from the database."""
    conn = connect_to_db()
    if not conn:
        return "{}"
    inspector = {}
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [table[0] for table in cursor.fetchall()]
        for table in tables:
            cursor.execute(f"DESCRIBE {table};")
            columns = cursor.fetchall()
            inspector[table] = [col[0] for col in columns]
    except Error as e:
        st.error(f"Error extracting schema: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    return json.dumps(inspector)

def show_tables_and_data():
    """Displays tables and their data in the UI."""
    conn = connect_to_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [table[0] for table in cursor.fetchall()]
        selected_table = st.selectbox("Select a table to view data:", tables)
        if selected_table:
            cursor.execute(f"SELECT * FROM {selected_table};")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            import pandas as pd
            df = pd.DataFrame(rows, columns=columns)
            st.write("Records:")
            st.dataframe(df, use_container_width=True, hide_index=True)
            if not df.empty:
                st.session_state["last_result_df"] = df
    except Error as e:
        st.error(f"Database error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def insert_data_form():
    """Provides a UI form to insert data into a selected table."""
    conn = connect_to_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [table[0] for table in cursor.fetchall()]
        selected_table = st.selectbox("Select a table to insert into:", tables)
        if selected_table:
            cursor.execute(f"DESCRIBE {selected_table};")
            columns = [col[0] for col in cursor.fetchall()]
            values = {}
            for col in columns:
                values[col] = st.text_input(f"Enter value for '{col}':")
            if st.button("Insert Record"):
                non_empty = {k: v for k, v in values.items() if v}
                if len(non_empty) == len(columns):
                    cols = ", ".join(values.keys())
                    placeholders = ", ".join(["%s"] * len(values))
                    sql = f"INSERT INTO {selected_table} ({cols}) VALUES ({placeholders});"
                    cursor.execute(sql, list(values.values()))
                    conn.commit()
                    st.success("Record inserted successfully.")
                else:
                    st.warning("Please fill all fields.")
    except Error as e:
        st.error(f"Database error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
