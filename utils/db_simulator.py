import sqlite3, random, string
import pandas as pd
from datetime import datetime, timedelta, timezone

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

def setup_ecommerce_db(db_path=DB_PATH, seed=42):
    random.seed(seed)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Disable foreign keys for dropping tables
    c.execute("PRAGMA foreign_keys = OFF;")

    tables = [
        "shipment_items","shipments","payments","order_discounts","order_items","orders",
        "cart_items","carts",
        "inventory","warehouses",
        "product_images","product_variants","products","categories","brands",
        "purchase_order_items","purchase_orders","suppliers",
        "reviews",
        "addresses","customers",
        "discounts"
    ]
    for t in tables:
        c.execute(f"DROP TABLE IF EXISTS {t};")
    
    # Re-enable foreign keys for table creation and data insertion
    c.execute("PRAGMA foreign_keys = ON;")

    c.execute("""
    CREATE TABLE brands (
      brand_id INTEGER PRIMARY KEY,
      name TEXT UNIQUE NOT NULL
    );""")

    c.execute("""
    CREATE TABLE categories (
      category_id INTEGER PRIMARY KEY,
      parent_id INTEGER REFERENCES categories(category_id) ON DELETE SET NULL,
      name TEXT NOT NULL
    );""")

    c.execute("""
    CREATE TABLE products (
      product_id INTEGER PRIMARY KEY,
      brand_id INTEGER REFERENCES brands(brand_id),
      category_id INTEGER REFERENCES categories(category_id),
      sku TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      description TEXT,
      price REAL NOT NULL,
      currency TEXT NOT NULL DEFAULT 'USD',
      is_active INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL
    );""")

    c.execute("""
    CREATE TABLE product_variants (
      variant_id INTEGER PRIMARY KEY,
      product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
      sku TEXT UNIQUE NOT NULL,
      color TEXT,
      size TEXT,
      stock_qty INTEGER NOT NULL DEFAULT 0,
      price_override REAL
    );""")

    c.execute("""
    CREATE TABLE product_images (
      image_id INTEGER PRIMARY KEY,
      product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
      url TEXT NOT NULL,
      is_primary INTEGER NOT NULL DEFAULT 0
    );""")

    c.execute("""
    CREATE TABLE warehouses (
      warehouse_id INTEGER PRIMARY KEY,
      name TEXT NOT NULL
    );""")

    c.execute("""
    CREATE TABLE inventory (
      variant_id INTEGER NOT NULL REFERENCES product_variants(variant_id) ON DELETE CASCADE,
      warehouse_id INTEGER NOT NULL REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
      quantity INTEGER NOT NULL,
      PRIMARY KEY (variant_id, warehouse_id)
    );""")

    c.execute("""
    CREATE TABLE customers (
      customer_id INTEGER PRIMARY KEY,
      first_name TEXT NOT NULL,
      last_name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      country TEXT,
      created_at TEXT NOT NULL,
      is_active INTEGER NOT NULL DEFAULT 1
    );""")

    c.execute("""
    CREATE TABLE addresses (
      address_id INTEGER PRIMARY KEY,
      customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
      type TEXT NOT NULL, -- 'billing' or 'shipping'
      line1 TEXT NOT NULL,
      line2 TEXT,
      city TEXT NOT NULL,
      state TEXT,
      postal_code TEXT,
      country TEXT NOT NULL,
      is_default INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL
    );""")

    c.execute("""
    CREATE TABLE orders (
      order_id INTEGER PRIMARY KEY,
      customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
      order_number TEXT UNIQUE NOT NULL,
      status TEXT NOT NULL,
      subtotal REAL NOT NULL,
      tax REAL NOT NULL,
      shipping_fee REAL NOT NULL,
      discount_total REAL NOT NULL,
      total REAL NOT NULL,
      currency TEXT NOT NULL DEFAULT 'USD',
      billing_address_id INTEGER REFERENCES addresses(address_id),
      shipping_address_id INTEGER REFERENCES addresses(address_id),
      created_at TEXT NOT NULL
    );""")

    c.execute("""
    CREATE TABLE order_items (
      order_item_id INTEGER PRIMARY KEY,
      order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
      variant_id INTEGER REFERENCES product_variants(variant_id),
      product_name TEXT NOT NULL,
      sku TEXT NOT NULL,
      quantity INTEGER NOT NULL,
      unit_price REAL NOT NULL,
      discount REAL NOT NULL DEFAULT 0,
      tax REAL NOT NULL DEFAULT 0
    );""")

    c.execute("""
    CREATE TABLE payments (
      payment_id INTEGER PRIMARY KEY,
      order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
      method TEXT NOT NULL,
      status TEXT NOT NULL,
      amount REAL NOT NULL,
      currency TEXT NOT NULL DEFAULT 'USD',
      provider_txn_id TEXT,
      created_at TEXT NOT NULL
    );""")

    c.execute("""
    CREATE TABLE shipments (
      shipment_id INTEGER PRIMARY KEY,
      order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
      carrier TEXT NOT NULL,
      tracking_number TEXT,
      status TEXT NOT NULL,
      shipped_at TEXT,
      delivered_at TEXT,
      shipping_address_id INTEGER REFERENCES addresses(address_id)
    );""")

    c.execute("""
    CREATE TABLE shipment_items (
      shipment_item_id INTEGER PRIMARY KEY,
      shipment_id INTEGER NOT NULL REFERENCES shipments(shipment_id) ON DELETE CASCADE,
      order_item_id INTEGER NOT NULL REFERENCES order_items(order_item_id) ON DELETE CASCADE,
      quantity INTEGER NOT NULL
    );""")

    c.execute("""
    CREATE TABLE discounts (
      discount_id INTEGER PRIMARY KEY,
      code TEXT UNIQUE NOT NULL,
      type TEXT NOT NULL, -- 'percent' or 'amount'
      value REAL NOT NULL,
      starts_at TEXT,
      ends_at TEXT,
      is_active INTEGER NOT NULL DEFAULT 1
    );""")

    c.execute("""
    CREATE TABLE order_discounts (
      order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
      discount_id INTEGER NOT NULL REFERENCES discounts(discount_id) ON DELETE CASCADE,
      PRIMARY KEY (order_id, discount_id)
    );""")

    c.execute("""
    CREATE TABLE suppliers (
      supplier_id INTEGER PRIMARY KEY,
      name TEXT NOT NULL
    );""")

    c.execute("""
    CREATE TABLE purchase_orders (
      po_id INTEGER PRIMARY KEY,
      supplier_id INTEGER NOT NULL REFERENCES suppliers(supplier_id),
      status TEXT NOT NULL,
      ordered_at TEXT NOT NULL,
      received_at TEXT
    );""")

    c.execute("""
    CREATE TABLE purchase_order_items (
      po_item_id INTEGER PRIMARY KEY,
      po_id INTEGER NOT NULL REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
      variant_id INTEGER NOT NULL REFERENCES product_variants(variant_id),
      quantity INTEGER NOT NULL,
      unit_cost REAL NOT NULL
    );""")

    c.execute("""
    CREATE TABLE reviews (
      review_id INTEGER PRIMARY KEY,
      product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
      customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
      rating INTEGER NOT NULL,
      title TEXT,
      body TEXT,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL
    );""")

    brands = [("Acme"),("Globex"),("Umbrella"),("Stark"),("Wayne"),("Initech"),("Wonka"),("Soylent"),("Tyrell"),("Hooli")]
    c.executemany("INSERT INTO brands(name) VALUES (?);", [(b,) for b in brands])

    top_categories = ["Electronics","Home & Kitchen","Fashion","Sports","Beauty","Toys","Automotive","Books"]
    sub_per_top = 2
    cat_rows, cat_id = [], 1
    parent_ids = []
    for name in top_categories:
        cat_rows.append((cat_id, None, name)); parent_ids.append(cat_id); cat_id += 1
        for i in range(sub_per_top):
            cat_rows.append((cat_id, parent_ids[-1], f"{name} Sub-{i+1}")); cat_id += 1
    c.executemany("INSERT INTO categories(category_id,parent_id,name) VALUES (?,?,?);", cat_rows)

    def rand_date(days=365):
        base = datetime.now(timezone.utc)
        dt = base - timedelta(days=random.randint(0, days))
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    colors = ["Red","Blue","Green","Black","White","Gray","Yellow"]
    sizes = ["XS","S","M","L","XL","XXL"]
    def rand_sku(prefix):
        return prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    products_rows, images_rows = [], []
    P = 200
    for pid in range(1, P+1):
        brand_id = random.randint(1, len(brands))
        category_id = random.randint(1, len(cat_rows))
        name = f"Product {pid}"
        sku = rand_sku("SKU-")
        price = round(random.uniform(5, 500), 2)
        products_rows.append((pid, brand_id, category_id, sku, name, f"Description for {name}", price, "USD", 1, rand_date()))
        images_rows.append((None, pid, f"https://pics.example.com/{pid}.jpg", 1))
    c.executemany("""INSERT INTO products(product_id,brand_id,category_id,sku,name,description,price,currency,is_active,created_at)
                     VALUES (?,?,?,?,?,?,?,?,?,?);""", products_rows)
    c.executemany("INSERT INTO product_images(image_id,product_id,url,is_primary) VALUES (?,?,?,?);", images_rows)

    variants_rows = []
    vid = 1
    for pid in range(1, P+1):
        v_count = random.randint(1, 3)
        chosen_colors = random.sample(colors, k=v_count if v_count <= len(colors) else len(colors))
        for i in range(v_count):
            color = chosen_colors[i]
            size = random.choice(sizes)
            sku = rand_sku("VAR-")
            stock_qty = random.randint(0, 200)
            price_override = None if random.random() < 0.8 else round(random.uniform(5, 500), 2)
            variants_rows.append((vid, pid, sku, color, size, stock_qty, price_override))
            vid += 1
    c.executemany("""INSERT INTO product_variants(variant_id,product_id,sku,color,size,stock_qty,price_override)
                     VALUES (?,?,?,?,?,?,?);""", variants_rows)
    max_variant_id = vid - 1

    warehouses = [("West DC",),("Central DC",),("East DC",)]
    c.executemany("INSERT INTO warehouses(name) VALUES (?);", warehouses)

    inv_rows = []
    for v in range(1, max_variant_id+1):
        for w in range(1, len(warehouses)+1):
            inv_rows.append((v, w, random.randint(0, 500)))
    c.executemany("INSERT INTO inventory(variant_id,warehouse_id,quantity) VALUES (?,?,?);", inv_rows)

    first_names = ["Alice","Bob","Carol","Dave","Eve","Frank","Grace","Heidi","Ivan","Judy","Mallory","Niaj","Olivia","Peggy","Rupert","Sybil","Trent","Victor","Wendy","Yvonne","Zack"]
    last_names = ["Smith","Johnson","Williams","Brown","Jones","Miller","Davis","Garcia","Rodriguez","Wilson","Anderson","Taylor"]
    countries = ["USA","Canada","UK","Germany","France","Australia","Japan","India"]
    CUST = 200
    customers_rows = []
    for cid in range(1, CUST+1):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        email = f"{fn.lower()}.{ln.lower()}{cid}@example.com"
        customers_rows.append((cid, fn, ln, email, random.choice(countries), rand_date(800), 1))
    c.executemany("""INSERT INTO customers(customer_id,first_name,last_name,email,country,created_at,is_active)
                     VALUES (?,?,?,?,?,?,?);""", customers_rows)

    addr_rows = []
    addr_id = 1
    for cid in range(1, CUST+1):
        addr_cnt = 1 if random.random() < 0.7 else 2
        for i in range(addr_cnt):
            addr_rows.append((addr_id, cid, "billing" if i == 0 else "shipping", f"{random.randint(100,999)} Main St",
                              "" , "City"+str(random.randint(1,200)), "State"+str(random.randint(1,50)),
                              f"{random.randint(10000,99999)}", random.choice(countries), 1 if i == 0 else 0, rand_date(800)))
            addr_id += 1
    c.executemany("""INSERT INTO addresses(address_id,customer_id,type,line1,line2,city,state,postal_code,country,is_default,created_at)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?);""", addr_rows)
    max_address_id = addr_id - 1

    disc_rows = []
    for i in range(1, 11):
        code = f"SAVE{i:02d}"
        dtype = "percent" if random.random() < 0.6 else "amount"
        value = random.choice([5,10,15,20]) if dtype == "percent" else random.choice([5.0,10.0,15.0,25.0])
        disc_rows.append((i, code, dtype, float(value), rand_date(400), rand_date(100), 1))
    c.executemany("""INSERT INTO discounts(discount_id,code,type,value,starts_at,ends_at,is_active)
                     VALUES (?,?,?,?,?,?,?);""", disc_rows)

    suppliers = [("North Supply Co",),("Global Parts Ltd",),("Prime Wholesale",)]
    c.executemany("INSERT INTO suppliers(name) VALUES (?);", suppliers)

    po_rows, poi_rows = [], []
    po_id = 1
    for _ in range(30):
        supplier_id = random.randint(1, len(suppliers))
        status = random.choice(["ordered","received","cancelled"])
        ordered_at = rand_date(500)
        received_at = None if status != "received" else rand_date(300)
        po_rows.append((po_id, supplier_id, status, ordered_at, received_at))
        item_cnt = random.randint(1, 5)
        for _ in range(item_cnt):
            variant_id = random.randint(1, max_variant_id)
            qty = random.randint(10, 200)
            unit_cost = round(random.uniform(2, 200), 2)
            poi_rows.append((None, po_id, variant_id, qty, unit_cost))
        po_id += 1
    c.executemany("""INSERT INTO purchase_orders(po_id,supplier_id,status,ordered_at,received_at)
                     VALUES (?,?,?,?,?);""", po_rows)
    c.executemany("""INSERT INTO purchase_order_items(po_item_id,po_id,variant_id,quantity,unit_cost)
                     VALUES (?,?,?,?,?);""", poi_rows)

    ORD = 500
    order_rows, order_item_rows, payment_rows, shipment_rows, shipment_item_rows, order_discount_rows = [], [], [], [], [], []
    order_id = 1
    order_item_id = 1
    shipment_id = 1
    tax_rate = 0.08

    for _ in range(ORD):
        cid = random.randint(1, CUST)
        created_at = rand_date(365)
        status = random.choice(["created","paid","shipped","delivered","cancelled","refunded"])
        bill_addr = random.randint(1, max_address_id)
        ship_addr = random.randint(1, max_address_id)
        item_cnt = random.randint(1, 5)
        items = []
        subtotal = 0.0
        for _ in range(item_cnt):
            variant_id = random.randint(1, max_variant_id)
            c.execute("SELECT p.name, COALESCE(v.price_override, p.price), v.sku FROM product_variants v JOIN products p ON p.product_id=v.product_id WHERE v.variant_id=?;", (variant_id,))
            row = c.fetchone()
            pname, price, variant_sku = row[0], float(row[1]), row[2]
            qty = random.randint(1, 4)
            items.append((variant_id, pname, qty, price, variant_sku))
            subtotal += qty * price

        has_discount = random.random() < 0.25
        discount_total = 0.0
        if has_discount:
            did = random.randint(1, 10)
            c.execute("SELECT type,value FROM discounts WHERE discount_id=?;", (did,))
            dt, dv = c.fetchone()
            if dt == "percent":
                discount_total = round(subtotal * (dv / 100.0), 2)
            else:
                discount_total = float(dv)
            order_discount_rows.append((order_id, did))

        shipping_fee = round(random.uniform(0, 15), 2)
        tax = round((subtotal - discount_total) * tax_rate, 2)
        total = round(subtotal - discount_total + tax + shipping_fee, 2)
        order_number = f"ORD-{order_id:06d}"
        order_rows.append((order_id, cid, order_number, status, round(subtotal,2), tax, shipping_fee, round(discount_total,2), total, "USD", bill_addr, ship_addr, created_at))

        for variant_id, pname, qty, price, variant_sku in items:
            line_discount = 0.0
            line_tax = round((qty * price - line_discount) * tax_rate, 2)
            order_item_rows.append((order_item_id, order_id, variant_id, pname, variant_sku, qty, price, line_discount, line_tax))
            order_item_id += 1

        method = random.choice(["card","paypal","cod","wallet"])
        p_status = "paid" if status in ("paid","shipped","delivered","refunded") else "pending"
        provider_txn_id = rand_sku("TXN-") if p_status != "pending" else None
        payment_rows.append((None, order_id, method, p_status, total, "USD", provider_txn_id, created_at))

        carrier = random.choice(["UPS","FedEx","USPS","DHL"])
        s_status = random.choice(["label_created","in_transit","delivered"]) if status in ("shipped","delivered") else "label_created"
        shipped_at = created_at if s_status in ("in_transit","delivered") else None
        delivered_at = created_at if s_status == "delivered" else None
        shipment_rows.append((shipment_id, order_id, carrier, rand_sku("TRK-"), s_status, shipped_at, delivered_at, ship_addr))

        start_item_idx = len(order_item_rows) - item_cnt
        for oi in order_item_rows[start_item_idx:]:
            shipment_item_rows.append((None, shipment_id, oi[0], oi[6]))

        shipment_id += 1
        order_id += 1

    c.executemany("""INSERT INTO orders(order_id,customer_id,order_number,status,subtotal,tax,shipping_fee,discount_total,total,currency,billing_address_id,shipping_address_id,created_at)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);""", order_rows)
    c.executemany("""INSERT INTO order_items(order_item_id,order_id,variant_id,product_name,sku,quantity,unit_price,discount,tax)
                     VALUES (?,?,?,?,?,?,?,?,?);""", order_item_rows)
    if order_discount_rows:
        c.executemany("""INSERT INTO order_discounts(order_id,discount_id) VALUES (?,?);""", order_discount_rows)
    c.executemany("""INSERT INTO payments(payment_id,order_id,method,status,amount,currency,provider_txn_id,created_at)
                     VALUES (?,?,?,?,?,?,?,?);""", payment_rows)
    c.executemany("""INSERT INTO shipments(shipment_id,order_id,carrier,tracking_number,status,shipped_at,delivered_at,shipping_address_id)
                     VALUES (?,?,?,?,?,?,?,?);""", shipment_rows)
    c.executemany("""INSERT INTO shipment_items(shipment_item_id,shipment_id,order_item_id,quantity)
                     VALUES (?,?,?,?);""", shipment_item_rows)

    review_rows = []
    for _ in range(500):
        pid = random.randint(1, P)
        cid = random.randint(1, CUST)
        rating = random.randint(1, 5)
        status = random.choice(["published","pending","rejected"])
        review_rows.append((None, pid, cid, rating, f"Title {rating}", f"Body for product {pid}", status, rand_date(365)))
    c.executemany("""INSERT INTO reviews(review_id,product_id,customer_id,rating,title,body,status,created_at)
                     VALUES (?,?,?,?,?,?,?,?);""", review_rows)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_ecommerce_db()
    print("Sample database created.")
