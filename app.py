# app.py
import streamlit as st
from database import extract_schema
from ui_components import render_query_tab, render_view_tab, render_insert_tab
from export_utils import export_to_csv, export_to_pdf
import os

# --- Streamlit UI ---
st.set_page_config(page_title="Natural Language Database Assistant", layout="wide")
st.title("💬 Natural Language Database Assistant (MySQL + DeepSeek)")

# Load schema once at the beginning
schema = extract_schema()

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["🔍 Generate & Run Query", "📂 View Database", "🆕 Insert Data"])

with tab1:
    render_query_tab(schema)

with tab2:
    render_view_tab()

with tab3:
    render_insert_tab()

# --- Sidebar Controls (Only appear if result exists) ---
if "last_result_df" in st.session_state:
    with st.sidebar:
        st.markdown("### 🧹 Actions")
        if st.button("Clear Session", use_container_width=True):
            # Safely clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.toast("Session cleared!", icon="🧹")

        df = st.session_state.get("last_result_df", None)
        if df is not None and not df.empty:
            try:
                csv_file = export_to_csv(df)
                pdf_file = export_to_pdf(df)
                # Ensure files exist before offering download
                if os.path.exists(csv_file):
                    with open(csv_file, "rb") as f:
                        st.download_button(
                            label="📄 Export to CSV",
                            data=f.read(),
                            file_name=csv_file,
                            mime="text/csv",
                            use_container_width=True
                        )
                if os.path.exists(pdf_file):
                     with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📄 Export to PDF",
                            data=f.read(),
                            file_name=pdf_file,
                            mime="application/pdf",
                            use_container_width=True
                        )
            except Exception as e:
                st.error(f"Error preparing export files: {e}")
