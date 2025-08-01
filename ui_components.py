# ui_components.py
import streamlit as st
from llm import to_sql_query, clean_text
from query_executor import execute_sql, display_sql_result
from database import show_tables_and_data, insert_data_form


def render_query_tab(schema):
    """Renders the 'Generate & Run Query' tab."""
    st.markdown("### 🤖 Ask a Question About Your Database")
    user_query = st.text_area("Describe what you want to retrieve or do with the database:", height=100)
    col1, col2 = st.columns([1, 1])
    with col1:
        generate_clicked = st.button("🧠 Generate SQL", use_container_width=True)
    with col2:
        retry_clicked = st.button("🔁 Retry (Better Prompt)", use_container_width=True)

    if generate_clicked and user_query.strip():
        raw_sql = to_sql_query(user_query, schema)
        cleaned_sql = clean_text(raw_sql)
        st.session_state["generated_sql"] = cleaned_sql
        st.session_state["previous_raw_sql"] = raw_sql

    if retry_clicked and "previous_raw_sql" in st.session_state:
        raw_sql = to_sql_query(user_query, schema, retry=True, previous_response=st.session_state["previous_raw_sql"])
        cleaned_sql = clean_text(raw_sql)
        st.session_state["generated_sql"] = cleaned_sql

    if "generated_sql" in st.session_state:
        final_sql = st.session_state["generated_sql"]
        st.markdown("### 🛠 Manual SQL Editor")
        edited_sql = st.text_area("Edit or paste SQL below:", value=final_sql, height=200)
        col_exec, _ = st.columns([1, 4])
        with col_exec:
            if st.button("▶️ Execute Edited SQL", use_container_width=True, type="primary"):
                result = execute_sql(edited_sql)
                st.markdown("### 📊 Query Result")

                # --- Enhanced Result Display ---
                if isinstance(result, list) and result:
                    # Use the function from query_executor to get the DataFrame
                    import pandas as pd
                    df = pd.DataFrame(result)
                    st.session_state["last_result_df"] = df

                    # Display in an expander for fullscreen/modal-like view
                    with st.expander("🔍 View Result Details (Fullscreen)", expanded=True):
                        # Use full width for the dataframe inside the expander
                        st.dataframe(df, use_container_width=True, hide_index=True)

                        # Optional: Show row/column count
                        st.caption(f"Showing {len(df)} rows and {len(df.columns)} columns.")
                else:
                    # Handle non-SELECT queries or empty results
                    st.info(result if isinstance(result, str) else "No results returned or query was not a SELECT.")


def render_view_tab():
    """Renders the 'View Database' tab."""
    st.header("📂 View Tables and Records")
    show_tables_and_data()


def render_insert_tab():
    """Renders the 'Insert Data' tab."""
    st.header("🆕 Insert New Data into Table")
    insert_data_form()