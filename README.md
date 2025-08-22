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
- 🧠 **4 RAG approaches to choose from** - Keyword, FAISS Vector, ChromaDB Vector, or No RAG
- 🔬 **Interactive RAG performance testing** - Compare approaches with real-time metrics
- 🤖 **Multi-agent system** powered by CrewAI (Generation → Review → Compliance)
- 🗃️ **Comprehensive ecommerce database** with 20+ tables and sample data
- 🔄 **One-click schema refresh** support
- 🔐 **Built-in query safety checks** and compliance validation
- 💰 **LLM cost transparency** - track your token usage and costs

---

## 🧠 RAG-Powered Schema Intelligence

The system offers **4 different RAG approaches** to optimize schema handling for different use cases:

### 🎯 Available RAG Options:

1. **No RAG (Full Schema)** 
   - Uses complete database schema for maximum context
   - Best for: Complex queries requiring full schema awareness
   - Trade-off: Higher token usage, slower processing

2. **Keyword RAG** 
   - Custom keyword-based table selection
   - Best for: Fast processing with good accuracy
   - Benefits: 60-80% token reduction, <1ms response time

3. **FAISS Vector RAG** 
   - Advanced semantic similarity search using FAISS
   - Best for: Complex semantic queries requiring deep understanding
   - Benefits: 75%+ token reduction, superior semantic matching

4. **Chroma Vector RAG** 
   - Persistent vector database with ChromaDB
   - Best for: Production environments requiring consistent performance
   - Benefits: 75%+ token reduction, persistent storage, faster than FAISS

### 🔬 RAG Performance Testing:
- **Interactive comparison** of all RAG approaches
- **Real-time metrics** showing table count, token reduction, and response time
- **Query-specific recommendations** based on performance results

### RAG Benefits:
- 📉 **60-80% token reduction** for schema context
- ⚡ **25% faster** query generation with keyword RAG
- 🚀 **Advanced semantic matching** with vector RAG
- 💰 **Lower costs** - significant OpenAI API savings
- 🎯 **Better accuracy** with focused, relevant context

---

## 🛠 Tech Stack

| Component         | Technology          |
|-------------------|---------------------|
| Frontend UI       | Streamlit 1.48.1    |
| Database Engine   | SQLite              |
| Agent Framework   | CrewAI 0.130.0      |
| LLMs              | OpenAI GPT-4o-mini  |
| RAG Systems       | Multiple approaches: |
|                   | • Custom keyword-based |
|                   | • FAISS Vector Search |
|                   | • ChromaDB Vector DB |
| Vector Embeddings | Sentence Transformers |
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
