import streamlit as st
from crew_setup import sql_generator_crew, sql_reviewer_crew, sql_compliance_crew
from utils.db_simulator import get_structured_schema, run_query
import sqlparse

DB_PATH = "data/sample_db.sqlite"

# Cache the schema, but allow clearing it
@st.cache_data(show_spinner=False)
def load_schema():
    return get_structured_schema(DB_PATH)

st.title("SQL Assistant Crew")

st.markdown("""
Welcome to the SQL Assistant Crew!  
This app lets you interact with your database using natural language. Simply type your data question or request (for example, "Show me the top 5 products by total revenue for April 2024"), and our multi-agent system will:
1. **Generate** a relevant SQL query for your request,
2. **Review** and optimize the query for correctness and performance,
3. **Check** the query for compliance and data safety,
4. **Execute** the query (if compliant) and display the results.

You can also refresh the database schema if your data changes.  
This tool is perfect for business users, analysts, and anyone who wants to query data without writing SQL by hand!
""")

st.write("The schema of the database is saved. If you believe the schema is incorrect, you can refresh it by clicking the button below.")
# Add a refresh button
if st.button("Refresh Schema"):
    load_schema.clear()  # Clear the cache so next call reloads from DB
    st.success("Schema refreshed from database.")

# Always get the (possibly cached) schema
db_schema = load_schema()

with st.expander("Show database schema"):
    st.code(db_schema)

st.write("Enter your request in natural language and let the crew generate, review, and check compliance for the SQL query.")

if "generated_sql" not in st.session_state:
    st.session_state["generated_sql"] = None
if "awaiting_confirmation" not in st.session_state:
    st.session_state["awaiting_confirmation"] = False
if "reviewed_sql" not in st.session_state:
    st.session_state["reviewed_sql"] = None
if "compliance_report" not in st.session_state:
    st.session_state["compliance_report"] = None
if "query_result" not in st.session_state:
    st.session_state["query_result"] = None
if "regenerate_sql" not in st.session_state:
    st.session_state["regenerate_sql"] = False

user_prompt = st.text_input("Enter your request (e.g., 'Show me the top 5 products by total revenue for April 2024'):")

# Automatically regenerate SQL if 'Try Again' was clicked
if st.session_state.get("regenerate_sql"):
    if user_prompt.strip():
        try:
            gen_output = sql_generator_crew.kickoff(inputs={"user_input": user_prompt, "db_schema": db_schema})
            raw_sql = gen_output.pydantic.sqlquery
            st.session_state["generated_sql"] = raw_sql
            st.session_state["awaiting_confirmation"] = True
            st.session_state["reviewed_sql"] = None
            st.session_state["compliance_report"] = None
            st.session_state["query_result"] = None
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt.")
    st.session_state["regenerate_sql"] = False

# Step 1: Generate SQL
if st.button("Generate SQL"):
    if user_prompt.strip():
        try:
            gen_output = sql_generator_crew.kickoff(inputs={"user_input": user_prompt, "db_schema": db_schema})
            raw_sql = gen_output.pydantic.sqlquery
            st.session_state["generated_sql"] = raw_sql
            st.session_state["awaiting_confirmation"] = True
            st.session_state["reviewed_sql"] = None
            st.session_state["compliance_report"] = None
            st.session_state["query_result"] = None
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt.")

# Only show prompt and generated SQL when awaiting confirmation
if st.session_state.get("awaiting_confirmation") and st.session_state.get("generated_sql"):
    st.subheader("Generated SQL")
    formatted_generated_sql = sqlparse.format(st.session_state["generated_sql"], reindent=True, keyword_case='upper')
    st.code(formatted_generated_sql, language="sql")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Confirm and Review"):
            try:
                # Step 2: Review SQL
                review_output = sql_reviewer_crew.kickoff(inputs={"sql_query": st.session_state["generated_sql"],"db_schema": db_schema})
                reviewed_sql = review_output.pydantic.reviewed_sqlquery
                st.session_state["reviewed_sql"] = reviewed_sql
                # Step 3: Compliance Check
                compliance_output = sql_compliance_crew.kickoff(inputs={"reviewed_sqlquery": reviewed_sql})
                compliance_report = compliance_output.pydantic.report
                # Remove duplicate header if present
                lines = compliance_report.splitlines()
                if lines and lines[0].strip().lower().startswith("# compliance report"):
                    compliance_report = "\n".join(lines[1:]).lstrip()
                st.session_state["compliance_report"] = compliance_report
                # Only execute if compliant
                if "compliant" in compliance_report.lower():
                    result = run_query(reviewed_sql)
                    st.session_state["query_result"] = result
                else:
                    st.session_state["query_result"] = None
                st.session_state["awaiting_confirmation"] = False
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")
    with col2:
        if st.button("Try Again"):
            st.session_state["generated_sql"] = None
            st.session_state["awaiting_confirmation"] = False
            st.session_state["reviewed_sql"] = None
            st.session_state["compliance_report"] = None
            st.session_state["query_result"] = None
            st.session_state["regenerate_sql"] = True
            st.rerun()
    with col3:
        if st.button("Abort"):
            st.session_state.clear()
            st.rerun()

# After review, only show reviewed SQL, compliance, and result
elif st.session_state.get("reviewed_sql"):
    st.subheader("Reviewed SQL")
    formatted_sql = sqlparse.format(st.session_state["reviewed_sql"], reindent=True, keyword_case='upper')
    st.code(formatted_sql, language="sql")
    st.subheader("Compliance Report")
    st.markdown(st.session_state["compliance_report"])
    if st.session_state.get("query_result"):
        st.subheader("Query Result")
        st.code(st.session_state["query_result"]) 