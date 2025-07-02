# 📘 SQL Assistant Crew

**SQL Assistant Crew** is a Streamlit-powered, CrewAI-orchestrated multi-agent assistant that allows users to interact with a **SQLite** database using natural language. With a modular agent architecture for generation, review, compliance, and execution, users can safely and intuitively run SQL queries—no manual SQL required. Checkout the blog for more details (https://towardsdatascience.com/a-multi-agent-sql-assistant-you-can-trust-with-human-in-loop-checkpoint-llm-cost-control/)

---

## 🧠 How It Works

This app uses a **CrewAI-based agent system** to process each user query through a collaborative pipeline:

1. **🗣 Natural Language Input (User)**  
   Users type their question in everyday language using the Streamlit front end.

2. **🤖 SQL Generation Agent**  
   Converts the user prompt into an SQL query using schema context and user intent.

3. **🔍 Query Review Agent**  
   Refines and optimizes the SQL query for correctness and performance.

4. **🔐 Compliance Agent**  
   Validates the SQL for data safety (e.g., prevents `DROP`, `DELETE`, `ALTER`, etc.)

5. **⚙️ Execution Agent**  
   Runs the approved SQL query against the SQLite database and returns results to the user.

6. **🔄 Schema Sync Agent**  
   Allows on-demand schema refresh so agents stay aware of the current database structure.

---

## ✅ Features

- 💬 Natural language SQL querying
- 🧠 Modular agents powered by [CrewAI](https://github.com/joaomdmoura/crewAI)
- 🖥️ Streamlit-based UI for accessibility
- 🗃️ Lightweight **SQLite** backend (ideal for local/dev environments)
- 🔄 One-click schema refresh support
- 🔐 Built-in query safety checks
- 📊 Clean result display and optional download

---

## 🛠 Tech Stack

| Component         | Technology          |
|-------------------|---------------------|
| Frontend UI       | Streamlit           |
| Database Engine   | SQLite              |
| Agent Framework   | [CrewAI](https://github.com/joaomdmoura/crewAI) |
| LLMs              | OpenAI / GPT-4 (via API) |
| Orchestration     | Python              |
| Schema Handling   | SQLite introspection |

---

## 🚀 Getting Started

```bash
git clone https://github.com/your-username/sql-assistant-crew.git
cd sql-assistant-crew
streamlit run app.py
