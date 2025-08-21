import streamlit as st
from crew_setup import sql_generator_crew, sql_reviewer_crew, sql_compliance_crew
from utils.db_simulator import get_structured_schema, run_query
from utils.schema_rag import get_rag_enhanced_schema, get_cached_schema_rag
import sqlparse
from utils.helper import extract_token_counts, calculate_gpt4o_mini_cost
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)
DB_PATH = "data/sample_db.sqlite"

# Cache the schema, but allow clearing it
@st.cache_data(show_spinner=False)
def load_schema():
    return get_structured_schema(DB_PATH)

# Cache the RAG system
@st.cache_resource(show_spinner=False)
def load_rag_system():
    """Initialize and cache the RAG system for schema retrieval."""
    try:
        return get_cached_schema_rag(DB_PATH)
    except Exception as e:
        st.warning(f"RAG system initialization failed: {e}")
        return None

def get_relevant_schema(user_query: str, use_rag: bool = True):
    """Get relevant schema based on user query, with RAG or full schema fallback."""
    if use_rag:
        try:
            rag_system = load_rag_system()
            if rag_system:
                return rag_system.get_relevant_schema(user_query)
        except Exception as e:
            st.warning(f"RAG retrieval failed, using full schema: {e}")
    
    # Fallback to full schema
    return load_schema()

st.title("SQL Assistant Crew")

st.markdown("""
Welcome to the SQL Assistant Crew!  
This app lets you interact with your database using natural language. Simply type your data question or request (for example, "Which brands sell the most products?"), and our multi-agent system will:
1. **Generate** a relevant SQL query for your request,
2. **Review** and optimize the query for correctness and performance,
3. **Check** the query for compliance and data safety,
4. **Execute** the query (if compliant) and display the results.

You can also refresh the database schema if your data changes.  
This tool is perfect for business users, analysts, and anyone who wants to query data without writing SQL by hand!
""")

st.write("The schema of the database is saved. If you believe the schema is incorrect, you can refresh it by clicking the button below.")

# RAG Configuration
col1, col2 = st.columns([2, 1])
with col1:
    use_rag_schema = st.checkbox(
        "🧠 Use RAG Schema (Smart Retrieval)", 
        value=True, 
        help="Use RAG to retrieve only relevant schema tables based on your query. This reduces token usage and improves efficiency."
    )
with col2:
    if st.button("Refresh Schema"):
        load_schema.clear()  # Clear the cache so next call reloads from DB
        load_rag_system.clear()  # Clear RAG cache too
        # Show success message in full width below
        st.session_state["schema_refreshed"] = True

# Show schema refresh success message in full width
if st.session_state.get("schema_refreshed"):
    st.success("✅ Schema refreshed from database.")
    # Clear the flag after showing
    del st.session_state["schema_refreshed"]

# Always get the full schema for display
full_schema = load_schema()

with st.expander("Show database schema"):
    st.code(full_schema)

# Show RAG status
if use_rag_schema:
    rag_system = load_rag_system()
    if rag_system:
        st.success("🧠 RAG system active - will retrieve relevant schema based on your query")
    else:
        st.warning("⚠️ RAG system not available - using full schema")

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
if "llm_cost" not in st.session_state:
    st.session_state["llm_cost"] = 0.0

user_prompt = st.text_input("Enter your request (e.g., 'Show me the top 5 products by total revenue for April 2024'):")

# Automatically regenerate SQL if 'Try Again' was clicked
if st.session_state.get("regenerate_sql"):
    if user_prompt.strip():
        try:
            # Get relevant schema based on RAG setting
            relevant_schema = get_relevant_schema(user_prompt, use_rag_schema)
            
            gen_output = sql_generator_crew.kickoff(inputs={"user_input": user_prompt, "db_schema": relevant_schema})
            raw_sql = gen_output.pydantic.sqlquery
            st.session_state["generated_sql"] = raw_sql
            st.session_state["awaiting_confirmation"] = True
            st.session_state["reviewed_sql"] = None
            st.session_state["compliance_report"] = None
            st.session_state["query_result"] = None
            # LLM cost tracking
            token_usage_str = str(gen_output.token_usage)
            prompt_tokens, completion_tokens = extract_token_counts(token_usage_str)
            cost = calculate_gpt4o_mini_cost(prompt_tokens, completion_tokens)
            st.session_state["llm_cost"] += cost
            st.info(f"Your LLM cost so far: ${st.session_state['llm_cost']:.6f}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt.")
    st.session_state["regenerate_sql"] = False

# Step 1: Generate SQL
if st.button("Generate SQL"):
    if user_prompt.strip():
        try:
            # Get relevant schema based on RAG setting
            relevant_schema = get_relevant_schema(user_prompt, use_rag_schema)
            
            # Show which schema is being used
            if use_rag_schema:
                with st.expander("📊 RAG Retrieved Schema"):
                    st.code(relevant_schema)
                    st.info("ℹ️ Only relevant tables retrieved based on your query")
            
            gen_output = sql_generator_crew.kickoff(inputs={"user_input": user_prompt, "db_schema": relevant_schema})
            # st.write(gen_output)  # Optionally keep for debugging
            raw_sql = gen_output.pydantic.sqlquery
            st.session_state["generated_sql"] = raw_sql
            st.session_state["awaiting_confirmation"] = True
            st.session_state["reviewed_sql"] = None
            st.session_state["compliance_report"] = None
            st.session_state["query_result"] = None
            # LLM cost tracking
            token_usage_str = str(gen_output.token_usage)
            prompt_tokens, completion_tokens = extract_token_counts(token_usage_str)
            cost = calculate_gpt4o_mini_cost(prompt_tokens, completion_tokens)
            st.session_state["llm_cost"] += cost
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt.")

# Only show prompt and generated SQL when awaiting confirmation
if st.session_state.get("awaiting_confirmation") and st.session_state.get("generated_sql"):
    st.subheader("Generated SQL")
    formatted_generated_sql = sqlparse.format(st.session_state["generated_sql"], reindent=True, keyword_case='upper')
    st.code(formatted_generated_sql, language="sql")
    # Full width cost display
    st.info(f"💰 Your LLM cost so far: ${st.session_state['llm_cost']:.6f}")
    
    # Action buttons with proper spacing
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("✅ Confirm and Review", type="secondary", use_container_width=True):
            try:
                # Step 2: Review SQL (always use full schema for comprehensive review)
                full_schema = load_schema()
                review_output = sql_reviewer_crew.kickoff(inputs={"sql_query": st.session_state["generated_sql"],"db_schema": full_schema})
                reviewed_sql = review_output.pydantic.reviewed_sqlquery
                st.session_state["reviewed_sql"] = reviewed_sql
                # LLM cost tracking for reviewer
                token_usage_str = str(review_output.token_usage)
                prompt_tokens, completion_tokens = extract_token_counts(token_usage_str)
                cost = calculate_gpt4o_mini_cost(prompt_tokens, completion_tokens)
                st.session_state["llm_cost"] += cost
                # Step 3: Compliance Check
                compliance_output = sql_compliance_crew.kickoff(inputs={"reviewed_sqlquery": reviewed_sql})
                compliance_report = compliance_output.pydantic.report
                # LLM cost tracking for compliance
                token_usage_str = str(compliance_output.token_usage)
                prompt_tokens, completion_tokens = extract_token_counts(token_usage_str)
                cost = calculate_gpt4o_mini_cost(prompt_tokens, completion_tokens)
                st.session_state["llm_cost"] += cost
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
        if st.button("🔄 Try Again", use_container_width=True):
            st.session_state["generated_sql"] = None
            st.session_state["awaiting_confirmation"] = False
            st.session_state["reviewed_sql"] = None
            st.session_state["compliance_report"] = None
            st.session_state["query_result"] = None
            st.session_state["regenerate_sql"] = True
            st.rerun()
    
    with col3:
        if st.button("❌ Abort", use_container_width=True):
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
    
    # Action buttons after results - only Start Over, no Try Again
    st.markdown("---")
    
    # Show status message first
    compliance_report = st.session_state.get("compliance_report", "").lower()
    
    # Check for actual compliance issues (not just "issues found" text)
    has_compliance_issues = (
        "issues found:" in compliance_report or 
        "violation" in compliance_report or 
        "not compliant" in compliance_report or
        "error" in compliance_report
    ) and "no issues found" not in compliance_report and "compliant" not in compliance_report
    
    # Check for query execution errors
    query_result = st.session_state.get("query_result", "")
    has_execution_error = query_result and "error" in str(query_result).lower()
    
    # Show appropriate status message first
    if has_compliance_issues:
        st.warning("⚠️ Compliance issues detected in the query. Consider using 'Start Over' to try a different approach.")
    elif has_execution_error:
        st.error("❌ Query execution failed. Use 'Start Over' to try a different query.")
    elif "compliant" in compliance_report and st.session_state.get("query_result"):
        st.success("✅ Query is compliant and executed successfully!")
    
    # Then show cost display
    st.info(f"💰 Total LLM cost: ${st.session_state['llm_cost']:.6f}")
    
    # Finally, center the Start Over button
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        # Green Start Over button, centered and full width within its column
        start_over_clicked = st.button("🔄 Start Over", 
                                     help="Clear everything and start with a new query",
                                     key="start_over_btn",
                                     type="secondary",
                                     use_container_width=True)
        
        if start_over_clicked:
            # Clear all session state to start fresh
            keys_to_clear = [
                "generated_sql", "awaiting_confirmation", "reviewed_sql", 
                "compliance_report", "query_result", "regenerate_sql"
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("✅ Ready for a new query!")
            st.rerun()

