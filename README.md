# 📘 SQL Assistant Crew

**SQL Assistant Crew** is a Streamlit-powered, CrewAI-orchestrated multi-agent assistant that allows users to interact with a **SQLite** database using natural language. With a modular agent architecture for generation, review, compliance, and execution, users can safely and intuitively run SQL queries—no manual SQL required. Checkout the blog for more details (<https://towardsdatascience.com/a-multi-agent-sql-assistant-you-can-trust-with-human-in-loop-checkpoint-llm-cost-control/>)

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

| Component         | Technology              |
|-------------------|-------------------------|
| Frontend UI       | Streamlit               |
| Database Engine   | SQLite                  |
| Agent Framework   | [CrewAI](https://github.com/joaomdmoura/crewAI) |
| LLMs              | OpenAI / GPT-4 (via API) |
| Orchestration     | Python                   |
| Schema Handling   | SQLite introspection     |

---

## 🚀 Getting Started

To get started with the SQL Assistant Crew, follow the instructions below based on your experience level and operating system.

### For Novice Programmers

If you're new to development environments, follow these detailed steps.

#### Windows Installation

1. **Install Git:**
    If you don't have Git installed, download it from the official website: [Git for Windows](https://git-scm.com/download/win). Follow the installation instructions.

2. **Clone the Repository:**
    Open your command prompt (CMD) or PowerShell and run:

    ```bash
    git clone https://github.com/sravz3/SQL-Assistant-Crew
    cd SQL-Assistant-Crew
    ```

3. **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

4. **Install Dependencies:**
    Install the required Python packages:

    ```bash
    pip install streamlit crewai sqlparse python-dotenv
    ```

5. **Set Up OpenAI API Key:**
    This project uses OpenAI's GPT models. You need to provide your OpenAI API key.
    Create a file named `.env` in the root directory of the project (`c:/Users/YourUserName/Desktop/SQL-Assistant-Crew`).
    Add the following line to the `.env` file:

    ```text
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

    Replace `"your_openai_api_key_here"` with your actual OpenAI API key. The project uses the `python-dotenv` library to load this environment variable.

6. **Run the Application:**
    Once dependencies are installed and your API key is set, run the Streamlit application:

    ```bash
    streamlit run app.py
    ```

    This will open the SQL Assistant Crew application in your web browser.

#### Linux Installation

1. **Install Git (if not already installed):**
    Most Linux distributions come with Git pre-installed. If not, you can install it using your package manager:

    ```bash
    sudo apt update
    sudo apt install git  # For Debian/Ubuntu
    # Or for Fedora/RHEL: sudo dnf install git
    ```

2. **Clone the Repository:**
    Open your terminal and run:

    ```bash
    git clone https://github.com/sravz3/SQL-Assistant-Crew
    cd SQL-Assistant-Crew
    ```

3. **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4. **Install Dependencies:**
    Install the required Python packages:

    ```bash
    pip install streamlit crewai sqlparse python-dotenv
    ```

5. **Set Up OpenAI API Key:**
    This project uses OpenAI's GPT models. You need to provide your OpenAI API key.
    Create a file named `.env` in the root directory of the project (`/path/to/SQL-Assistant-Crew`).
    Add the following line to the `.env` file:

    ```text
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

    Replace `"your_openai_api_key_here"` with your actual OpenAI API key. The project uses the `python-dotenv` library to load this environment variable.

6. **Run the Application:**
    Once dependencies are installed and your API key is set, run the Streamlit application:

    ```bash
    streamlit run app.py
    ```

    This will open the SQL Assistant Crew application in your web browser.

### For Experienced Programmers

If you're familiar with Python development and virtual environments, here's a concise guide.

#### Windows & Linux Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/sravz3/SQL-Assistant-Crew
    cd SQL-Assistant-Crew
    ```

2. **Set up Virtual Environment and Install Dependencies:**

    ```bash
    # For Windows:
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt # Assuming a requirements.txt will be created or use the explicit list below
    
    # For Linux:
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt # Assuming a requirements.txt will be created or use the explicit list below
    ```

    *Note: If `requirements.txt` is not available, use `pip install streamlit crewai sqlparse python-dotenv`.*

3. **Configure OpenAI API Key:**
    Create a `.env` file in the project root and add your OpenAI API key:

    ```text
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

4. **Run the Application:**

    ```bash
    streamlit run app.py
    ```

    Access the application in your web browser.
