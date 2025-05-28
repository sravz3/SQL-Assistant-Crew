import sqlite3
import pandas as pd

DB_PATH = "data/sample_db.sqlite"

def setup_sample_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create example tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            product_id INTEGER,
            product_name TEXT,
            revenue REAL,
            date TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER,
            name TEXT,
            email TEXT,
            signup_date TEXT
        );
    """)

    # Populate with mock data
    cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?);", [
        (1, 'Widget A', 1000, '2024-04-03'),
        (2, 'Widget B', 1500, '2024-04-12'),
        (3, 'Widget C', 1200, '2024-04-15'),
        (4, 'Widget D', 1800, '2024-04-20'),
        (5, 'Widget E', 1700, '2024-04-28'),
        (1, 'Widget A', 900,  '2024-04-30')
    ])

    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?);", [
        (1, 'Alice', 'alice@example.com', '2023-10-01'),
        (2, 'Bob', 'bob@example.com', '2023-11-15'),
        (3, 'Charlie', 'charlie@example.com', '2024-01-10')
    ])

    conn.commit()
    conn.close()

def run_query(query):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.head().to_string(index=False)
    except Exception as e:
        return f"Query failed: {e}"

def get_db_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    schema = ""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table_name, in tables:
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        create_stmt = cursor.fetchone()[0]
        schema += create_stmt + ";\n\n"
    conn.close()
    return schema

if __name__ == "__main__":
    setup_sample_db()
    print("Sample database created.")
