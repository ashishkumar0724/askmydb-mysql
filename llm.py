# llm.py
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import streamlit as st
from config import LLM_MODEL_NAME

# --- Initialize LLM Model ---
try:
    model = OllamaLLM(model=LLM_MODEL_NAME)
except Exception as e:
    st.error(f"Error loading model '{LLM_MODEL_NAME}': {e}")
    model = None # Indicate model loading failure

# --- Prompt Templates ---
TEMPLATE = """
You are a SQL generator. When given a schema and a user question, you MUST output only the SQL statement—nothing else. No explanation, no markdown, just raw SQL.
Schema: {schema}
User question: {query}
Output (SQL only):
"""

RETRY_TEMPLATE = """
You are a SQL generator. Your previous attempt returned invalid content. Please generate only valid SQL based on the following:
Schema: {schema}
User question: {query}
Previous response: {previous}
Output (Only SQL - no extra text):
"""

# --- Function to generate SQL from Natural Language ---
def to_sql_query(query, schema, retry=False, previous_response=""):
    """Generates SQL using the LLM based on the query and schema."""
    if not model:
        return "LLM model is not available."

    if retry:
        prompt = ChatPromptTemplate.from_template(RETRY_TEMPLATE)
        chain = prompt | model
        response = chain.invoke({"query": query, "schema": schema, "previous": previous_response})
    else:
        prompt = ChatPromptTemplate.from_template(TEMPLATE)
        chain = prompt | model
        response = chain.invoke({"query": query, "schema": schema})
    return clean_text(response)

# --- Text Cleaning Function ---
def clean_text(text: str):
    """Cleans the LLM response to extract the SQL query."""
    if not isinstance(text, str):
        return ""
    text = text.strip()
    # Try to extract SQL inside ```sql ... ```
    sql_match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if sql_match:
        return sql_match.group(1).strip()
    # If not found, try to extract anything after "SQL:" or similar keywords
    fallback_match = re.split(r"(?i)sql:\s*", text, maxsplit=1)
    if len(fallback_match) > 1:
        return fallback_match[1].strip()
    # As last resort, remove any obvious non-SQL lines
    lines = [line for line in text.strip().splitlines() if not line.lower().startswith(("explanation", "note"))]
    result = "\n".join(lines).strip()
    # If still contains invalid syntax (like JSON-like structures), return empty
    if re.search(r"[{}[\]()]", result):
        return ""
    return result
