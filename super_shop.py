import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from fpdf import FPDF
from PIL import Image
from io import BytesIO
import datetime
import os

# ---------------- DATABASE CONNECTION ----------------
def get_connection():
    conn = sqlite3.connect("supershop.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row  # allows dict-like access
    return conn

conn = get_connection()
cursor = conn.cursor()

# ---------------- CREATE TABLES IF NOT EXISTS ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    barcode TEXT UNIQUE,
    category TEXT,
    unit TEXT,
    purchase_price REAL,
    selling_price REAL,
    stock_quantity REAL,
    minimum_stock REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers(
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees(
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    role TEXT,
    salary REAL,
    hired_date DATE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers(
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    address TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    employee_id INTEGER,
    total_amount REAL,
    payment_method TEXT,
    amount_received REAL,
    change_amount REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sale_items(
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER,
    product_id INTEGER,
    quantity REAL,
    unit_price REAL,
    total_price REAL
)
""")
conn.commit()
# ---------------- AUTO INSERT DEFAULT DATA ----------------
def seed_default_data():

    # Default Customer
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO customers (name, phone, address)
            VALUES ('Walk-in Customer', 'N/A', 'Local')
        """)

    # Default Employee
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO employees (name, role, salary, hired_date)
            VALUES ('Admin', 'Manager', 0, DATE('now'))
        """)

    conn.commit()

seed_default_data()
from fpdf import FPDF
from io import BytesIO
import os
import datetime

# ---------------- CASH MEMO FUNCTION ----------------
def generate_cash_memo_bytes(sale_id, customer_name, cart_items, total_amount, payment_method):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # -------- LOGO --------
    if os.path.exists("Sarder Super Shop logo design.png"):
        pdf.image("Sarder Super Shop logo design.png", x=10, y=8, w=30)
        pdf.ln(20)

    # -------- SHOP HEADER --------
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, "SARDER SUPER SHOP", ln=True, align='C')
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 6, "Kaligonj Bazar, Kalkini, Madaripur", ln=True, align='C')
    pdf.cell(0, 6, "Mobile: 01922388130", ln=True, align='C')
    pdf.cell(0, 6, "Email: mdarafathossen62@gmail.com", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "CASH MEMO / INVOICE", ln=True, align='C')
    pdf.ln(5)

    # -------- INVOICE INFO --------
    pdf.set_font("Arial", '', 11)
    pdf.cell(95, 6, f"Invoice No: SSS-{sale_id}")
    pdf.cell(95, 6, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(95, 6, f"Customer: {customer_name}")
    pdf.cell(95, 6, f"Payment Method: {payment_method}", ln=True)
    pdf.ln(8)

    # -------- TABLE HEADER --------
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(60, 8, "Product", 1)
    pdf.cell(25, 8, "Unit", 1, align='C')
    pdf.cell(25, 8, "Qty", 1, align='C')
    pdf.cell(30, 8, "Unit Price", 1, align='C')
    pdf.cell(30, 8, "Total", 1, align='C')
    pdf.ln()

    # -------- TABLE BODY --------
    pdf.set_font("Arial", '', 10)
    for item in cart_items:
        pdf.cell(60, 8, str(item['product']), 1)
        pdf.cell(25, 8, str(item['unit']), 1, align='C')
        pdf.cell(25, 8, f"{item['quantity']}", 1, align='C')
        pdf.cell(30, 8, f"{item['unit_price']:.2f}", 1, align='R')
        pdf.cell(30, 8, f"{item['total_price']:.2f}", 1, align='R')
        pdf.ln()

    # -------- GRAND TOTAL --------
    pdf.set_font("Arial", 'B', 13)
    pdf.cell(110, 10, "")
    pdf.cell(40, 10, "GRAND TOTAL", 1)
    pdf.cell(30, 10, f"{total_amount:.2f}", 1, align='R')
    pdf.ln(15)

    # -------- FOOTER --------
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 6, "----------------------------------------------", ln=True, align='C')
    pdf.cell(0, 6, "Thank You For Shopping With Us!", ln=True, align='C')
    pdf.cell(0, 6, "Goods once sold are not refundable without receipt.", ln=True, align='C')
    pdf.cell(0, 6, "Powered by Sarder POS System", ln=True, align='C')

    # -------- FIXED: Save PDF to BytesIO --------
    pdf_str = pdf.output(dest='S').encode('latin1')  # returns PDF as bytes
    pdf_bytes = BytesIO(pdf_str)
    pdf_bytes.seek(0)
    return pdf_bytes
# ---------------- HEADER ----------------
st.set_page_config(page_title="SARDER SUPER SHOP", layout="wide")
if os.path.exists("Sarder Super Shop logo design.png"):
    logo = Image.open("Sarder Super Shop logo design.png")
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(logo, width=150)
    with col2:
        st.title("SARDER SUPER SHOP")
        st.caption("Super Shop Management System")
else:
    st.title("SARDER SUPER SHOP")
    st.caption("Super Shop Management System")

menu = st.sidebar.selectbox("Select Module",
                            ["Products","Customers","Employees","Suppliers","Sales","Dashboard"])

# ================= PRODUCTS =================
if menu == "Products":
    st.header("Add Product")
    name = st.text_input("Product Name")
    barcode = st.text_input("Barcode (Unique for scanning)")
    category = st.selectbox("Category", ["Food","Electronics","Clothing","Stationery","Groceries","Toiletries"])
    unit = st.selectbox("Unit", ["pcs","kg", "gm","liter","ml","pack","box","cup"])
    purchase_price = st.number_input("Purchase Price", 0.0)
    selling_price = st.number_input("Selling Price", 0.0)
    stock_quantity = st.number_input("Stock Quantity", 0)
    minimum_stock = st.number_input("Minimum Stock", 0)

    if st.button("Add Product"):
        cursor.execute("SELECT * FROM products WHERE barcode=?", (barcode,))
        if cursor.fetchone():
            st.warning("This barcode already exists! Use a unique barcode.")
        elif not name or not barcode:
            st.warning("Product Name and Barcode are required!")
        else:
            cursor.execute("""
                INSERT INTO products
                (name, barcode, category, unit, purchase_price, selling_price, stock_quantity, minimum_stock)
                VALUES (?,?,?,?,?,?,?,?)
            """, (name, barcode, category, unit, purchase_price, selling_price, stock_quantity, minimum_stock))
            conn.commit()
            st.success("Product Added Successfully!")
            st.experimental_rerun()

    st.subheader("Product List")
    products_df = pd.read_sql("SELECT * FROM products ORDER BY product_id DESC", conn)
    st.dataframe(products_df)

# ================= CUSTOMERS =================
elif menu == "Customers":
    st.header("👤 Add Customer")
    name = st.text_input("Customer Name")
    phone = st.text_input("Phone")
    address = st.text_area("Address")
    if st.button("Add Customer"):
        if not name:
            st.warning("Customer name required!")
        else:
            cursor.execute("INSERT INTO customers (name, phone, address) VALUES (?,?,?)", (name, phone, address))
            conn.commit()
            st.success("Customer Added Successfully!")
            st.experimental_rerun()
    st.subheader("Customer List")
    customers_df = pd.read_sql("SELECT * FROM customers ORDER BY customer_id DESC", conn)
    st.dataframe(customers_df)

# ================= EMPLOYEES =================
elif menu == "Employees":
    st.header("👨‍💼 Add Employee")
    name = st.text_input("Employee Name")
    role = st.selectbox("Role", ["Manager", "Cashier", "Salesman"])
    salary = st.number_input("Salary", 0.0)
    hired_date = st.date_input("Hired Date")
    if st.button("Add Employee"):
        if not name:
            st.warning("Employee name required!")
        else:
            cursor.execute("INSERT INTO employees (name, role, salary, hired_date) VALUES (?,?,?,?)", (name, role, salary, hired_date))
            conn.commit()
            st.success("Employee Added Successfully!")
            st.experimental_rerun()
    st.subheader("Employee List")
    employees_df = pd.read_sql("SELECT * FROM employees ORDER BY employee_id DESC", conn)
    st.dataframe(employees_df)

# ================= SUPPLIERS =================
elif menu == "Suppliers":
    st.header("🚚 Add Supplier")
    name = st.text_input("Supplier Name")
    phone = st.text_input("Phone")
    address = st.text_area("Address")
    if st.button("Add Supplier"):
        if not name:
            st.warning("Supplier name required!")
        else:
            cursor.execute("INSERT INTO suppliers (name, phone, address) VALUES (?,?,?)", (name, phone, address))
            conn.commit()
            st.success("Supplier Added Successfully!")
            st.experimental_rerun()
    st.subheader("Supplier List")
    suppliers_df = pd.read_sql("SELECT * FROM suppliers ORDER BY supplier_id DESC", conn)
    st.dataframe(suppliers_df)

# ================= SALES / POS =================
elif menu == "Sales":
    st.header("🛒 POS Billing")

    # ---------------- LOAD DATA ----------------
    customers_df = pd.read_sql("SELECT customer_id,name FROM customers", conn)
    employees_df = pd.read_sql("SELECT employee_id,name FROM employees", conn)
    products_df = pd.read_sql("SELECT * FROM products", conn)

    # ---------------- SAFETY CHECK ----------------
    if customers_df.empty or employees_df.empty or products_df.empty:
        st.error("Database tables are empty! Please check your data.")
        st.stop()

    # ---------------- CUSTOMER / EMPLOYEE ----------------
    customer = st.selectbox("Customer", [""] + list(customers_df['name']))
    employee = st.selectbox("Employee", [""] + list(employees_df['name']))

    if customer == "" or employee == "":
        st.warning("Please select a customer and an employee to continue.")
        st.stop()

    customer_row = customers_df[customers_df['name'] == customer]
    if customer_row.empty:
        st.error("Selected customer not found in database!")
        st.stop()
    customer_id = int(customer_row['customer_id'].iloc[0])

    employee_row = employees_df[employees_df['name'] == employee]
    if employee_row.empty:
        st.error("Selected employee not found in database!")
        st.stop()
    employee_id = int(employee_row['employee_id'].iloc[0])

    # ---------------- INITIALIZE CART ----------------
    if 'cart' not in st.session_state:
        st.session_state.cart = []

    # ---------------- ADD PRODUCT ----------------
    st.subheader("➕ Add Product to Cart")

    # Split products
    groceries = products_df[products_df['category'] == 'Groceries']
    non_groceries = products_df[products_df['category'] != 'Groceries']

    selected_product = None
    selected_product_id = None

    # --- Grocery dropdown
    if not groceries.empty:
        grocery_list = [""] + list(groceries['name'].dropna().unique())
        product_name = st.selectbox("Select Grocery Product", grocery_list)

        if product_name != "":
            filtered_product = groceries[
                groceries['name'].str.strip().str.lower() == product_name.strip().lower()
            ]
            if not filtered_product.empty:
                selected_product = filtered_product.iloc[0]
                selected_product_id = int(selected_product['product_id'])
            else:
                st.error("❌ Grocery product not found!")

    # --- Non-grocery barcode scanning
    barcode = st.text_input("Scan Barcode (Non-Grocery)")
    if barcode:
        product_row = non_groceries[non_groceries['barcode'] == barcode]
        if not product_row.empty:
            selected_product = product_row.iloc[0]
            selected_product_id = int(selected_product['product_id'])
        else:
            st.error("❌ Product not found!")

    # --- Quantity input and Add to Cart ---
    if selected_product is not None:
        st.success(f"Product: {selected_product['name']}")
        st.write(f"Price: ৳{selected_product['selling_price']} per {selected_product['unit']}")

        # Quantity input
        if selected_product['unit'] in ['kg', 'gm']:
            grams = st.number_input("Quantity in grams", min_value=0.0, step=50.0)
            qty = grams / 1000
        else:
            qty = st.number_input("Quantity (pcs)", min_value=1, step=1)

        if st.button("Add Product"):

            if qty <= 0:
                st.warning("Please enter valid quantity.")
            elif qty > float(selected_product['stock_quantity']):
                st.warning("Not enough stock available!")
            else:
                # Smart cart: update quantity if already in cart
                existing = next(
                    (i for i in st.session_state.cart
                     if i['product_id'] == selected_product_id),
                    None
                )
                if existing:
                    existing['quantity'] += float(qty)
                    existing['total_price'] = existing['quantity'] * existing['unit_price']
                else:
                    st.session_state.cart.append({
                        'product_id': selected_product['product_id'],
                        'product': selected_product['name'],
                        'unit': selected_product['unit'],
                        'quantity': float(qty),
                        'unit_price': float(selected_product['selling_price']),
                        'total_price': float(qty) * float(selected_product['selling_price'])
                    })

                st.success("✅ Product Added to Cart!")

    # ---------------- SHOW CART ----------------
    if st.session_state.cart:
        st.subheader("🛒 Cart Items")
        updated_cart = []

        for idx, item in enumerate(st.session_state.cart):
            cols = st.columns([2,1,1,1,1,1])
            cols[0].write(item['product'])
            cols[1].write(item['unit'])

            if item['unit'] in ['kg','gm']:
                grams = cols[2].number_input(
                    "Grams",
                    value=float(item['quantity']) * 1000,
                    step=50.0,
                    key=f"qty_{idx}"
                )
                new_qty = grams / 1000
            else:
                new_qty = cols[2].number_input(
                    "Qty",
                    value=int(item['quantity']),
                    step=1,
                    key=f"qty_{idx}"
                )

            new_price = cols[3].number_input(
                "Price",
                value=float(item['unit_price']),
                key=f"price_{idx}"
            )

            new_total = new_qty * new_price
            cols[4].write(f"{new_total:.2f}")

            remove = cols[5].button("❌", key=f"remove_{idx}")

            if not remove and new_qty > 0:
                updated_cart.append({
                    'product_id': item['product_id'],
                    'product': item['product'],
                    'unit': item['unit'],
                    'quantity': new_qty,
                    'unit_price': new_price,
                    'total_price': new_total
                })

        st.session_state.cart = updated_cart
        total = sum(i['total_price'] for i in updated_cart)
        st.metric("Total Amount", f"{total:.2f}")

        # ---------------- PAYMENT ----------------
        payment_method = st.selectbox("Payment Method",
                                      ["Cash","Card","Bkash","Nagad","Rocket"])

        amount_received = 0.0
        change_amount = 0.0

        if payment_method == "Cash":
            amount_received = st.number_input("Amount Received", 0.0)

            if amount_received >= total:
                change_amount = amount_received - total
                st.success(f"Change: {change_amount:.2f}")
            else:
                st.warning("Insufficient cash!")
        else:
            amount_received = total
            st.info(f"Paid via {payment_method}")

        # ---------------- CANCEL ----------------
        if st.button("Cancel Sale"):
            st.session_state.cart = []
            st.success("Sale Cancelled ✅")

        # ---------------- CONFIRM ----------------
        if st.button("Confirm Sale"):

            if payment_method == "Cash" and amount_received < total:
                st.error("❌ Insufficient cash received!")
                st.stop()

            try:
                cursor.execute("""
                    INSERT INTO sales
                    (customer_id, employee_id, total_amount,
                     payment_method, amount_received, change_amount)
                    VALUES (?,?,?,?,?,?)
                """, (customer_id, employee_id, total,
                      payment_method, amount_received, change_amount))

                sale_id = cursor.lastrowid

                for item in st.session_state.cart:
                    cursor.execute("""
                        INSERT INTO sale_items
                        (sale_id, product_id, quantity, unit_price, total_price)
                        VALUES (?,?,?,?,?)
                    """, (sale_id, item['product_id'],
                          item['quantity'], item['unit_price'],
                          item['total_price']))

                    cursor.execute("""
                        UPDATE products
                        SET stock_quantity = stock_quantity - ?
                        WHERE product_id = ?
                    """, (item['quantity'], item['product_id']))

                conn.commit()

                # Generate cash memo PDF
                pdf_bytes = generate_cash_memo_bytes(
                    sale_id, customer,
                    st.session_state.cart,
                    total, payment_method
                )

                st.download_button(
                    "📥 Download Cash Memo",
                    pdf_bytes,
                    file_name=f"SSS-{sale_id}.pdf"
                )

                st.session_state.cart = []
                st.success("✅ Sale Completed Successfully!")

            except Exception as e:
                conn.rollback()
                st.error(f"❌ Error: {e}")
# ================= DASHBOARD =================
elif menu == "Dashboard":
    st.header("📊 Dashboard")

    # --- Sales & Profit by Product ---
    sales_df = pd.read_sql("""
        SELECT p.name, si.quantity, si.total_price, p.purchase_price
        FROM sale_items si
        JOIN products p ON si.product_id = p.product_id
    """, conn)

    if not sales_df.empty:
        sales_df['profit'] = sales_df['total_price'] - (sales_df['purchase_price'] * sales_df['quantity'])

        # Create two columns for metrics
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Revenue", f"{sales_df['total_price'].sum():.2f}")

        with col2:
            st.metric("Total Profit", f"{sales_df['profit'].sum():.2f}")


        # Revenue by product bar chart
        revenue_by_product = sales_df.groupby('name')['total_price'].sum().reset_index()
        fig = px.bar(
            revenue_by_product,
            x='name',
            y='total_price',
            title="Revenue by Product",
            text='total_price'
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig)

    else:
        st.info("No sales data available.")

    # --- Low Stock Alert ---
    low_stock = pd.read_sql("""
        SELECT name, stock_quantity, minimum_stock
        FROM products
        WHERE stock_quantity <= minimum_stock
        ORDER BY stock_quantity ASC
    """, conn)

    st.subheader("⚠ Low Stock Products")
    if not low_stock.empty:
        st.dataframe(low_stock)
    else:
        st.success("All products have sufficient stock.")

    # --- Daily Sales Report ---
    daily_sales = pd.read_sql("""
        SELECT DATE(created_at) AS sale_date, SUM(total_amount) AS total_sales
        FROM sales
        GROUP BY DATE(created_at)
        ORDER BY sale_date
    """, conn)

    st.subheader("📅 Daily Sales Report")
    if not daily_sales.empty:
        st.dataframe(daily_sales)

        # Line chart for daily sales
        fig2 = px.line(
            daily_sales,
            x='sale_date',
            y='total_sales',
            title="Daily Sales",
            markers=True
        )
        st.plotly_chart(fig2)
    else:
        st.info("No daily sales data available.")


cursor.close()
conn.close()










