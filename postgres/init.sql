-- =============================================
-- 1. TẠO BẢNG CHÍNH (DDL)
-- =============================================
CREATE TABLE branches (
    branch_id VARCHAR(50) PRIMARY KEY,
    branch_name TEXT,
    branch_type VARCHAR(20),
    address TEXT,
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    brand TEXT,
    unit VARCHAR(50), 
    sale_price NUMERIC(15, 2),
    cost_price NUMERIC(15, 2),
    unit_of_measure VARCHAR(50),
    is_for_sale INTEGER
);

CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name TEXT,
    phone VARCHAR(50),
    address TEXT,
    customer_group TEXT,
    current_debt NUMERIC(15, 2),
    status INTEGER
);

CREATE TABLE suppliers (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name TEXT,
    phone VARCHAR(50),
    address TEXT,
    tax_id VARCHAR(50),
    current_liability NUMERIC(15, 2),
    status INTEGER
);

CREATE TABLE inventory_stocks (
    branch_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity_on_hand NUMERIC(15, 2),
    PRIMARY KEY (branch_id, product_id)
);

CREATE TABLE invoices (
    invoice_id VARCHAR(50) PRIMARY KEY,
    created_at TIMESTAMP,
    status VARCHAR(50),
    subtotal NUMERIC(15, 2),
    invoice_discount NUMERIC(15, 2),
    total_amount NUMERIC(15, 2),
    salesperson_name TEXT,
    customer_id VARCHAR(50),
    branch_id VARCHAR(50)
);

CREATE TABLE invoice_items (
    invoice_item_id SERIAL PRIMARY KEY,
    invoice_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity NUMERIC(15, 2),
    unit_price NUMERIC(15, 2),
    sale_price NUMERIC(15, 2),
    line_total NUMERIC(15, 2)
);

-- =============================================
-- 2. IMPORT DỮ LIỆU (Dùng Bảng Tạm cho các file lệch cột)
-- =============================================

-- 2.1 Branches (File khớp cột -> COPY trực tiếp)
COPY branches(branch_id, branch_name, branch_type) 
FROM '/data_files/branches.csv' DELIMITER ',' CSV HEADER;

-- 2.2 Products (File thừa cột -> Dùng Staging)
CREATE TEMP TABLE staging_products (
    category TEXT, product_id TEXT, barcode TEXT, product_name TEXT, brand TEXT,
    unit TEXT, sale_price NUMERIC, cost_price NUMERIC, total_stock NUMERIC,
    unit_of_measure TEXT, is_for_sale INTEGER
);
COPY staging_products FROM '/data_files/processed_merged_products.csv' DELIMITER ',' CSV HEADER;

INSERT INTO products (product_id, product_name, category, brand, unit, sale_price, cost_price, unit_of_measure, is_for_sale)
SELECT product_id, product_name, category, brand, unit, sale_price, cost_price, unit_of_measure, is_for_sale 
FROM staging_products;
DROP TABLE staging_products;

-- 2.3 Customers (File thừa cột -> Dùng Staging)
CREATE TEMP TABLE staging_customers (
    customer_id TEXT, customer_name TEXT, phone TEXT, address TEXT, company_name TEXT,
    tax_id TEXT, customer_group TEXT, note TEXT, created_at TIMESTAMP,
    current_debt NUMERIC, net_sales NUMERIC, status INTEGER
);
COPY staging_customers FROM '/data_files/processed_merged_customers.csv' DELIMITER ',' CSV HEADER;

INSERT INTO customers (customer_id, customer_name, phone, address, customer_group, current_debt, status)
SELECT customer_id, customer_name, phone, address, customer_group, current_debt, status 
FROM staging_customers;
DROP TABLE staging_customers;

-- 2.4 Suppliers (File thừa cột -> Dùng Staging)
CREATE TEMP TABLE staging_suppliers (
    supplier_id TEXT, supplier_name TEXT, phone TEXT, address TEXT,
    total_purchased NUMERIC, current_liability NUMERIC, tax_id TEXT,
    note TEXT, status INTEGER, net_purchased NUMERIC, created_at TIMESTAMP
);
COPY staging_suppliers FROM '/data_files/processed_merged_suppliers.csv' DELIMITER ',' CSV HEADER;

INSERT INTO suppliers (supplier_id, supplier_name, phone, address, tax_id, current_liability, status)
SELECT supplier_id, supplier_name, phone, address, tax_id, current_liability, status 
FROM staging_suppliers;
DROP TABLE staging_suppliers;

-- 2.5 Inventory Stocks (File khớp cột -> COPY trực tiếp)
COPY inventory_stocks(branch_id, product_id, quantity_on_hand) 
FROM '/data_files/inventory_stocks.csv' DELIMITER ',' CSV HEADER;

-- 2.6 Invoices (File gộp -> Dùng Staging & Tách)
CREATE TEMP TABLE staging_invoices (
    branch_name TEXT, invoice_id VARCHAR(50), created_at TIMESTAMP,
    customer_id VARCHAR(50), customer_name TEXT, salesperson_name TEXT,
    sales_channel TEXT, created_by TEXT, note TEXT,
    subtotal NUMERIC, invoice_discount NUMERIC, total_amount NUMERIC,
    amount_paid NUMERIC, status TEXT, product_id VARCHAR(50),
    product_name TEXT, unit_of_measure TEXT, quantity NUMERIC,
    unit_price NUMERIC, item_discount_amount NUMERIC, sale_price NUMERIC,
    line_total NUMERIC
);
COPY staging_invoices FROM '/data_files/processed_merged_invoice_details.csv' DELIMITER ',' CSV HEADER;

-- Insert vào Header
INSERT INTO invoices (invoice_id, created_at, status, subtotal, invoice_discount, total_amount, salesperson_name, customer_id, branch_id)
SELECT DISTINCT 
    t.invoice_id, t.created_at, t.status, t.subtotal, t.invoice_discount, 
    t.total_amount, t.salesperson_name, t.customer_id, b.branch_id
FROM staging_invoices t 
LEFT JOIN branches b ON t.branch_name = b.branch_name;

-- Insert vào Details
INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, sale_price, line_total)
SELECT invoice_id, product_id, quantity, unit_price, sale_price, line_total 
FROM staging_invoices;

DROP TABLE staging_invoices;
ALTER SYSTEM SET wal_level = 'logical';
CREATE PUBLICATION erp_debezium_pub FOR ALL TABLES;
