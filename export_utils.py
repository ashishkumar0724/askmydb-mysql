# export_utils.py
from fpdf import FPDF
import pandas as pd
import os

# --- Define the export directory ---
EXPORT_DIR = "exports"

# --- Ensure the export directory exists ---
os.makedirs(EXPORT_DIR, exist_ok=True)


def export_to_csv(df, filename="query_result.csv"):
    """Exports a DataFrame to CSV and saves it in the 'exports' folder."""
    # Create the full path for the file
    filepath = os.path.join(EXPORT_DIR, filename)
    df.to_csv(filepath, index=False)
    return filepath  # Return the full path


def export_to_pdf(df, filename="query_result.pdf"):
    """Exports a DataFrame to PDF and saves it in the 'exports' folder."""
    # Create the full path for the file
    filepath = os.path.join(EXPORT_DIR, filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    # Add header
    pdf.cell(200, 10, txt="Query Result", ln=True, align='C')
    # Table headers
    pdf.set_font("Arial", 'B', 10)
    if not df.empty:
        col_width = pdf.w / float(len(df.columns)) - 1.5
        row_height = pdf.font_size * 1.5
        for col in df.columns:
            pdf.cell(col_width, row_height, txt=str(col), border=1, align='C')
        pdf.ln()
        # Table data
        pdf.set_font("Arial", size=10)
        for index, row in df.iterrows():
            for col in df.columns:
                pdf.cell(col_width, row_height, txt=str(row[col]), border=1, align='C')
            pdf.ln()
    pdf.output(filepath)  # Save to the full path
    return filepath  # Return the full path
