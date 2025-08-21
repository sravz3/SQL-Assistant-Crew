# 📘 SQL Assistant Crew

**SQL Assistant Crew** is a Streamlit-powered, CrewAI-orchestrated multi-agent assistant that allows users to interact with a **SQLite** database using natural language. With a modular agent architecture for generation, review, and compliance checking, users can safely and intuitively run SQL queries—no manual SQL required. Checkout the blog for more details (https://towardsdatascience.com/a-multi-agent-sql-assistant-you-can-trust-with-human-in-loop-checkpoint-llm-cost-control/)

---

## 🧠 How It Works

This app uses a **CrewAI-based agent system** to process each user query through a collaborative pipeline:

1. **🗣 Natural Language Input (User)**  
   Users type their question in everyday language using the Streamlit interface.

2. **🤖 SQL Generation Agent**  
   Converts the user prompt into an SQL query using RAG-enhanced schema context and user intent.

3. **🔍 Query Review Agent**  
   Refines and optimizes the SQL query for correctness and performance using the full database schema.

4. **🔐 Compliance Agent**  
   Validates the SQL for data safety, PII access, and policy violations.

5. **⚙️ Query Execution**  
   Runs the approved SQL query against the SQLite database and returns results to the user.

---

## ✅ Features

- 💬 **Natural language SQL querying** - Ask questions in plain English
- 🧠 **RAG-powered schema retrieval** - Smart schema selection reduces token usage by 60-80%
- 🤖 **Multi-agent system** powered by CrewAI
- 🖥️ **Streamlit-based UI** for accessibility and ease of use
- 🗃️ **Comprehensive ecommerce database** with 20+ tables and sample data
- 🔄 **One-click schema refresh** support
- 🔐 **Built-in query safety checks** and compliance validation
- 📊 **Clean result display** with cost tracking
- 💰 **LLM cost transparency** - track your OpenAI usage

---

## 🧠 RAG-Powered Schema Intelligence

The system includes a **custom keyword-based RAG implementation** for smart schema handling:

- **Smart Table Selection**: Automatically identifies relevant tables based on your query
- **Token Optimization**: Reduces schema tokens by 60-80% compared to sending full schema
- **Custom Implementation**: Built from scratch using simple keyword matching (no external RAG libraries)
- **Fallback Safety**: Automatically uses full schema when RAG retrieval fails
- **Cost Savings**: Significantly reduces OpenAI API costs through efficient token usage

### RAG Benefits:
- 📉 **60-80% token reduction** for schema context
- ⚡ **25% faster** query generation
- 💰 **Lower costs** - ~$0.002 savings per query
- 🎯 **Better accuracy** with focused context

---

## 🛠 Tech Stack

| Component         | Technology          |
|-------------------|---------------------|
| Frontend UI       | Streamlit 1.48.1    |
| Database Engine   | SQLite              |
| Agent Framework   | CrewAI 0.130.0      |
| LLMs              | OpenAI GPT-4o-mini  |
| RAG System        | Custom keyword-based |
| Python Version    | 3.9+ (3.11 recommended) |
| Data Processing   | Pandas, NumPy       |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+ (Python 3.11 recommended)
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/sql-assistant-crew.git
cd sql-assistant-crew

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Initialize the ecommerce database
python -c "from utils.db_simulator import setup_ecommerce_db; setup_ecommerce_db(); print('✅ Database created')"

# Run the application
streamlit run app.py
