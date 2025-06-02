import sqlite3
import pandas as pd

DB_PATH = "data/sample_db.sqlite"

def setup_sample_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop tables if they exist (for repeatability in dev)
    cursor.execute("DROP TABLE IF EXISTS order_items;")
    cursor.execute("DROP TABLE IF EXISTS orders;")
    cursor.execute("DROP TABLE IF EXISTS products;")
    cursor.execute("DROP TABLE IF EXISTS customers;")
    cursor.execute("DROP TABLE IF EXISTS employees;")
    cursor.execute("DROP TABLE IF EXISTS departments;")

    # Create richer example tables
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            price REAL
        );
    """)
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            country TEXT,
            signup_date TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            total_amount REAL,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
        );
    """)
    cursor.execute("""
        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY(order_id) REFERENCES orders(order_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        );
    """)
    cursor.execute("""
        CREATE TABLE employees (
            employee_id INTEGER PRIMARY KEY,
            name TEXT,
            department_id INTEGER,
            hire_date TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE departments (
            department_id INTEGER PRIMARY KEY,
            department_name TEXT
        );
    """)

    # Populate with mock data
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?);", [
        (1, 'Widget A', 'Widgets', 25.0),
        (2, 'Widget B', 'Widgets', 30.0),
        (3, 'Gadget X', 'Gadgets', 45.0),
        (4, 'Gadget Y', 'Gadgets', 50.0),
        (5, 'Thingamajig', 'Tools', 15.0)
    ])
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?);", [
        (1, 'Alice', 'alice@example.com', 'USA', '2023-10-01'),
        (2, 'Bob', 'bob@example.com', 'Canada', '2023-11-15'),
        (3, 'Charlie', 'charlie@example.com', 'USA', '2024-01-10'),
        (4, 'Diana', 'diana@example.com', 'UK', '2024-02-20')
    ])
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?);", [
        (1, 1, '2024-04-03', 100.0),
        (2, 2, '2024-04-12', 150.0),
        (3, 1, '2024-04-15', 120.0),
        (4, 3, '2024-04-20', 180.0),
        (5, 4, '2024-04-28', 170.0)
    ])
    cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?);", [
        (1, 1, 1, 2, 25.0),
        (2, 1, 2, 1, 30.0),
        (3, 2, 3, 2, 45.0),
        (4, 3, 4, 1, 50.0),
        (5, 4, 5, 3, 15.0),
        (6, 5, 1, 1, 25.0)
    ])
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?);", [
        (1, 'Eve', 1, '2022-01-15'),
        (2, 'Frank', 2, '2021-07-23'),
        (3, 'Grace', 1, '2023-03-10')
    ])
    cursor.executemany("INSERT INTO departments VALUES (?, ?);", [
        (1, 'Sales'),
        (2, 'Engineering'),
        (3, 'HR')
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

def get_structured_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    lines = ["Available tables and columns:"]
    for table_name, in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        lines.append(f"- {table_name}: {', '.join(columns)}")
    conn.close()
    return '\n'.join(lines)

if __name__ == "__main__":
    setup_sample_db()
    print("Sample database created.")
