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

To get started with the SQL Assistant Crew, follow these steps:

### 1. Install Git (if not already installed)

If you don't have Git installed, you can download it from the official website: [Git for Windows](https://git-scm.com/download/win). Follow the installation instructions.

### 2. Clone the Repository

```bash
git clone https://github.com/sravz3/SQL-Assistant-Crew
cd SQL-Assistant-Crew
```

### 2. Create and Activate a Virtual Environment (Windows)

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages using pip:

```bash
pip install streamlit crewai sqlparse python-dotenv
```

### 4. Set Up OpenAI API Key

This project uses OpenAI's GPT models. You need to provide your OpenAI API key.

Create a file named `.env` in the root directory of the project (c:/Users/UserName/Desktop/SQL-Assistant-Crew).

Add the following line to the `.env` file:

```
OPENAI_API_KEY="your_openai_api_key_here"
```

Replace `"your_openai_api_key_here"` with your actual OpenAI API key. The project uses the `python-dotenv` library to load this environment variable.

### 5. Run the Application

Once the dependencies are installed and your API key is set, you can run the Streamlit application:

```bash
streamlit run app.py
```

This will open the SQL Assistant Crew application in your web browser.
