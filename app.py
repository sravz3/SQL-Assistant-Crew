import streamlit as st
from crew_setup import sql_generator_crew, sql_reviewer_crew, sql_compliance_crew
from utils.db_simulator import get_db_schema, run_query

DB_PATH = "data/sample_db.sqlite"

# Cache the schema, but allow clearing it
@st.cache_data(show_spinner=False)
def load_schema():
    return get_db_schema(DB_PATH)

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

st.write("Enter your request in natural language and let the crew generate, review, and check compliance for the SQL query.")

user_prompt = st.text_input("Enter your request (e.g., 'Show me the top 5 products by total revenue for April 2024'):")

if st.button("Generate SQL"):
    if user_prompt.strip():
        try:
            # Step 1: Generate SQL
            gen_output = sql_generator_crew.kickoff(inputs={"user_input": user_prompt, "db_schema": db_schema})
            raw_sql = gen_output.pydantic.sqlquery

            # Step 2: Review SQL
            review_output = sql_reviewer_crew.kickoff(inputs={"sql_query": raw_sql})
            reviewed_sql = review_output.pydantic.reviewed_sqlquery

            # Step 3: Compliance Check
            compliance_output = sql_compliance_crew.kickoff(inputs={"reviewed_sqlquery": reviewed_sql})
            compliance_report = compliance_output.pydantic.report

            st.subheader("Generated SQL")
            st.code(raw_sql, language="sql")

            st.subheader("Reviewed SQL")
            st.code(reviewed_sql, language="sql")

            st.subheader("Compliance Report")
            # Remove duplicate header if present
            lines = compliance_report.splitlines()
            if lines and lines[0].strip().lower().startswith("# compliance report"):
                compliance_report = "\n".join(lines[1:]).lstrip()
            st.markdown(compliance_report)

            # Only execute if compliant
            if "compliant" in compliance_report.lower():
                st.success("Query is compliant. Executing the query...")
                result = run_query(reviewed_sql)
                st.subheader("Query Result")
                st.code(result)
            else:
                st.error("Query is NOT compliant. Querying is not possible.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt.") 