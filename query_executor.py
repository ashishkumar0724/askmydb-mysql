# query_executor.py
import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st
from database import connect_to_db # Import connection function

def execute_sql(sql):
    """Executes a given SQL query."""
    conn = connect_to_db()
    if not conn:
        return "Connection failed."
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        if sql.strip().lower().startswith("select"):
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return f"Query executed successfully. Rows affected: {cursor.rowcount}"
    except Error as e:
        return f"Error executing query: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def display_sql_result(result):
    """Displays the SQL result in a Streamlit dataframe."""
    if isinstance(result, list) and result:
        df = pd.DataFrame(result)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.session_state["last_result_df"] = df
    else:
        st.info("No results returned or query was not a SELECT.")
