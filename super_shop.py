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

# ---------------- CASH MEMO FUNCTION ----------------
def generate_cash_memo_bytes(sale_id, customer_name, cart_items, total_amount, payment_method):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # -------- LOGO --------
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

    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes

# ---------------- HEADER ----------------
st.set_page_config(page_title="SARDER SUPER SHOP", layout="wide")
logo = Image.open("Sarder Super Shop logo design.png")

col1, col2 = st.columns([1,4])
with col1:
    st.image(logo, width=150)
with col2:
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
        existing_barcode = cursor.fetchall()
        if existing_barcode:
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
            st.rerun()

    st.subheader("Product List")
    products_df = pd.read_sql("SELECT * FROM products ORDER BY product_id DESC", conn)
    st.dataframe(products_df)

    st.subheader("Scan Product by Barcode")
    scan_code = st.text_input("Enter Barcode to Find Product")
    if scan_code:
        scanned_product = products_df[products_df['barcode'] == scan_code]
        if not scanned_product.empty:
            st.write("✅ Product Found:")
            st.dataframe(scanned_product)
        else:
            st.warning("Product not found!")

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
            st.rerun()
    st.subheader("Customer List")
    customers_df = pd.read_sql("SELECT customer_id, name, phone, address, created_at FROM customers ORDER BY customer_id DESC", conn)
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
            st.rerun()
    st.subheader("Employee List")
    employees_df = pd.read_sql("SELECT employee_id, name, role, salary, hired_date FROM employees ORDER BY employee_id DESC", conn)
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
            st.rerun()
    st.subheader("Supplier List")
    suppliers_df = pd.read_sql("SELECT supplier_id, name, phone, address FROM suppliers ORDER BY supplier_id DESC", conn)
    st.dataframe(suppliers_df)

# ================= SALES =================
elif menu == "Sales":
    st.header("🛒 POS Billing")

    customers = pd.read_sql("SELECT customer_id,name FROM customers", conn)
    employees = pd.read_sql("SELECT employee_id,name FROM employees", conn)
    products = pd.read_sql("SELECT * FROM products", conn)

    customer = st.selectbox("Customer", customers['name'])
    employee = st.selectbox("Employee", employees['name'])

    if 'cart' not in st.session_state:
        st.session_state.cart = []

    st.subheader("➕ Add Product to Cart")
    groceries = products[products['category'] == 'Groceries']
    others = products[products['category'] != 'Groceries']
    selected_product = None
    selected_product_id = None
    if not groceries.empty:
        product_name = st.selectbox("Select Grocery Product", groceries['name'])
        if product_name:
            selected_product = groceries[groceries['name'] == product_name].iloc[0]
            selected_product_id = int(selected_product['product_id'])
    barcode = st.text_input("Scan Barcode (Non-Grocery)")
    if barcode:
        product_row = others[others['barcode'] == barcode]
        if not product_row.empty:
            selected_product = product_row.iloc[0]
            selected_product_id = int(selected_product['product_id'])
    qty = 0.0
    if selected_product is not None:
        if selected_product['unit'] in ['kg', 'gm']:
            grams = st.number_input("Enter Quantity (grams)", min_value=0.0, step=50.0)
            qty = grams / 1000
        else:
            qty = st.number_input("Quantity (pcs)", min_value=1, step=1)

    if st.button("Add Product"):
        if selected_product is not None and qty > 0:
            existing = next((i for i in st.session_state.cart if i['product_id']==selected_product['product_id']), None)
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
            st.success("Product Added!")
            st.rerun()
        else:
            st.warning("Select product and enter valid quantity!")

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









