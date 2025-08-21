import streamlit as st
from crew_setup import sql_generator_crew, sql_reviewer_crew, sql_compliance_crew
from utils.db_simulator import get_structured_schema, run_query
from utils.rag_manager import get_cached_rag_manager
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

# Cache the RAG manager
@st.cache_resource(show_spinner=False)
def load_rag_manager():
    """Initialize and cache the RAG manager for schema retrieval."""
    try:
        return get_cached_rag_manager(DB_PATH)
    except Exception as e:
        st.warning(f"RAG manager initialization failed: {e}")
        return None

def get_relevant_schema(user_query: str, rag_approach: str = 'keyword'):
    """Get relevant schema based on user query using specified RAG approach."""
    if rag_approach == 'no_rag':
        return load_schema()
    
    try:
        rag_manager = load_rag_manager()
        if rag_manager:
            return rag_manager.get_relevant_schema(user_query, rag_approach)
    except Exception as e:
        st.warning(f"RAG retrieval failed, using full schema: {e}")
    
    # Fallback to full schema
    return load_schema()

st.set_page_config(page_title="SQL Assistant Crew", layout="wide")

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

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════════
# 📊 CONFIGURATION SECTIONS (SIDE BY SIDE)
# ═══════════════════════════════════════════════════════════════════════════════════

# config_col1, config_col2 = st.columns(2)
config_col1, config_col2 = st.columns([3, 1])

# DATABASE SCHEMA SECTION
with config_col1:
    st.markdown("#### Database Schema")
    st.write("View and manage your database schema. Refresh if your database structure has changed.")
    
    # Always get the full schema for display
    full_schema = load_schema()
    with st.expander("📋 Show Database Schema", expanded=False):
        st.code(full_schema, language="sql")
        newline = '\n'
        table_count = len([line for line in full_schema.split(newline) if line.startswith('- ')])
        st.info(f"📈 Schema contains {table_count} tables")
    
    if st.button("🔄 Refresh Schema", use_container_width=True):
        load_schema.clear()  # Clear the cache so next call reloads from DB
        load_rag_manager.clear()  # Clear RAG cache too
        st.session_state["schema_refreshed"] = True

# RAG CONFIGURATION SECTION
with config_col2:
    st.markdown("#### RAG Configuration")
    # st.subheader("RAG Configuration")
    # st.write("Choose how to intelligently retrieve relevant schema tables for your queries.")
    
    # Get available RAG approaches
    rag_manager = load_rag_manager()
    if rag_manager:
        approaches = rag_manager.get_available_approaches()
        approach_options = {}
        for approach_id, info in approaches.items():
            approach_options[info['name']] = approach_id
        
        selected_approach_name = st.selectbox(
            "**Choose RAG Approach:**",
            options=list(approach_options.keys()),
            index=1,  # Default to Keyword RAG
            help="Select how to retrieve relevant schema tables for your queries"
        )
        
        selected_approach = approach_options[selected_approach_name]
        
        # Show approach info in a clean layout
        if selected_approach in approaches:
            info = approaches[selected_approach]
            
            # Status indicator
            if selected_approach != 'no_rag':
                st.info(f"🧠 **{info['name']}** active - {info['description']}")
            else:
                st.info(f"📋 **{info['name']}** - Using complete database schema")
    else:
        st.error("❌ RAG manager not available")
        selected_approach = 'no_rag'

# Show schema refresh success message in full width
if st.session_state.get("schema_refreshed"):
    st.success("✅ Schema refreshed from database.")
    del st.session_state["schema_refreshed"]

# ═══════════════════════════════════════════════════════════════════════════════════
# 🔬 RAG PERFORMANCE TESTING SECTION
# ═══════════════════════════════════════════════════════════════════════════════════

st.markdown("#### Want to compare RAG approaches?")
# st.write("Test and compare different RAG approaches to see which works best for your queries.")

if rag_manager:
    enable_comparison = st.checkbox("Enable RAG Performance Comparison", help="Compare all RAG approaches for your test query")
    
    if enable_comparison:
        test_query = st.text_input(
            "**Test Query:**", 
            placeholder="e.g., Show me total sales by brand",
            help="Enter a query to test different RAG approaches"
        )
        
        if test_query.strip():
            with st.spinner("🔄 Comparing RAG approaches..."):
                comparison = rag_manager.compare_approaches(test_query, max_tables=5)
                
                st.write("**📊 RAG Performance Comparison**")
                
                # Create comparison table
                comparison_data = []
                for approach_id, result in comparison.items():
                    if result['success']:
                        comparison_data.append({
                            'Approach': approaches[approach_id]['name'],
                            'Tables': result['table_count'],
                            'Token Reduction': f"{result['token_reduction']:.1f}%",
                            'Response Time': f"{result['response_time']*1000:.1f}ms",
                            'Schema Length': result['schema_length']
                        })
                
                if comparison_data:
                    import pandas as pd
                    df = pd.DataFrame(comparison_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Show best approach
                    best_approach = max(comparison.items(), key=lambda x: x[1]['token_reduction'] if x[1]['success'] else 0)
                    if best_approach[1]['success']:
                        st.success(f"🏆 **Best Token Reduction:** {approaches[best_approach[0]]['name']} ({best_approach[1]['token_reduction']:.1f}%)")
else:
    st.warning("⚠️ RAG manager not available - performance comparison disabled")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════════
# 💬 QUERY INTERFACE SECTION
# ═══════════════════════════════════════════════════════════════════════════════════

st.markdown("### 💬 Natural Language Query Interface")

st.write("Enter your request in natural language and let our multi-agent system generate, review, check compliance and execute the SQL query.")

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

user_prompt = st.text_input(
    "**Your Query:**",
    placeholder="e.g., 'Show me the top 5 products by total revenue for April 2024'",
    help="Enter your data question in natural language"
)

# Automatically regenerate SQL if 'Try Again' was clicked
if st.session_state.get("regenerate_sql"):
    if user_prompt.strip():
        try:
            # Get relevant schema based on selected RAG approach
            relevant_schema = get_relevant_schema(user_prompt, selected_approach)
            
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
            # Get relevant schema based on selected RAG approach
            relevant_schema = get_relevant_schema(user_prompt, selected_approach)
            
            # Show which schema is being used
            if selected_approach != 'no_rag':
                with st.expander(f"📊 {approaches[selected_approach]['name']} Retrieved Schema"):
                    st.code(relevant_schema)
                    
                    # Show performance metrics if available
                    if rag_manager:
                        try:
                            comparison = rag_manager.compare_approaches(user_prompt, max_tables=5)
                            if selected_approach in comparison and comparison[selected_approach]['success']:
                                metrics = comparison[selected_approach]
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Tables Selected", metrics['table_count'])
                                with col2:
                                    st.metric("Token Reduction", f"{metrics['token_reduction']:.1f}%")
                                with col3:
                                    st.metric("Response Time", f"{metrics['response_time']*1000:.1f}ms")
                        except Exception as e:
                            st.info("ℹ️ Relevant tables retrieved based on your query")
            
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
    st.divider()
    
    # ═══════════════════════════════════════════════════════════════════════════════════
    # 📝 RESULTS SECTION
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    st.subheader("📝 Query Results")
    st.write("**🔧 Generated SQL**")
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
    st.write("**🔍 Reviewed SQL**")
    formatted_sql = sqlparse.format(st.session_state["reviewed_sql"], reindent=True, keyword_case='upper')
    st.code(formatted_sql, language="sql")
    
    st.write("**🔐 Compliance Report**")
    st.markdown(st.session_state["compliance_report"])
    
    if st.session_state.get("query_result"):
        st.write("**📊 Query Result**")
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

