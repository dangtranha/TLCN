-- =============================================
-- 1. TẠO BẢNG CHÍNH (DDL)
-- =============================================
CREATE TABLE branches (
    branch_id VARCHAR(50) PRIMARY KEY,
    branch_name TEXT,
    branch_type VARCHAR(20),
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

CREATE TABLE products (
    product_type TEXT,
    category_3_level TEXT,
    product_id VARCHAR(50) PRIMARY KEY,
    barcode TEXT,
    product_name TEXT,
    brand TEXT,
    sale_price NUMERIC(15,2),
    cost_price NUMERIC(15,2),
    stock_quantity NUMERIC(15,2),
    reserved_quantity NUMERIC(15,2),
    estimated_oos_date TEXT, -- không phải date trong sample
    min_stock_threshold NUMERIC(15,2),
    max_stock_threshold NUMERIC(15,2),
    unit_of_measure TEXT,
    base_unit_code TEXT,
    conversion_rate NUMERIC(15,2),
    attributes TEXT,
    related_product_code TEXT,
    image_urls TEXT,
    weight_gram NUMERIC(15,2),
    is_active INTEGER,
    is_direct_sale INTEGER,
    description TEXT,
    note_template TEXT,
    location TEXT,
    component_items TEXT,
    warranty_period TEXT,
    maintenance_cycle TEXT
);

CREATE TABLE customers (
    customer_type TEXT,
    created_branch_id VARCHAR(20),  -- chuẩn hóa đúng quy định
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name TEXT,
    phone TEXT,
    address TEXT,
    shipping_area TEXT,
    ward_commune TEXT,
    company_name TEXT,
    tax_id TEXT,
    identity_card_number TEXT,
    dob TEXT,
    gender TEXT,
    email TEXT,
    facebook_url TEXT,
    customer_group TEXT,
    note TEXT,
    created_by TEXT,
    created_at TIMESTAMP,
    last_transaction_date DATE,
    current_debt NUMERIC(18,2),
    total_sales NUMERIC(18,2),
    net_sales NUMERIC(18,2),
    status INTEGER
);

CREATE TABLE suppliers (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    area TEXT,
    ward_commune TEXT,
    total_purchased NUMERIC(18,2),
    current_liability NUMERIC(18,2),
    tax_id TEXT,
    note TEXT,
    supplier_group TEXT,
    status INTEGER,
    net_purchased NUMERIC(18,2),
    branch_id VARCHAR(20),  -- ✨ thay branch_name
    company_name TEXT,
    created_by TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE inventory_stocks (
    branch_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity_on_hand NUMERIC(15, 2),
    PRIMARY KEY (branch_id, product_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE invoices (
    invoice_id VARCHAR(50) PRIMARY KEY,
    branch_id VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    status VARCHAR(50),
    shipping_status VARCHAR(50),
    subtotal NUMERIC(18,2),
    invoice_discount NUMERIC(18,2),
    total_amount NUMERIC(18,2),
    amount_paid NUMERIC(18,2),
    salesperson_name TEXT,
    customer_id VARCHAR(50),
    note TEXT,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE invoice_items (
    invoice_item_id SERIAL PRIMARY KEY,
    invoice_id VARCHAR(50),
    product_id VARCHAR(50),
    barcode TEXT,
    product_name TEXT,
    brand TEXT,
    unit_of_measure TEXT,
    quantity NUMERIC(18,2),
    unit_price NUMERIC(18,2),
    item_discount_amount NUMERIC(18,2),
    sale_price NUMERIC(18,2),
    line_total NUMERIC(18,2),
    warranty TEXT,
    maintenance_cycle TEXT,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
);


-- =============================================
COPY branches(branch_id, branch_name, branch_type) 
FROM '/import_data/branches.csv' DELIMITER ',' CSV HEADER;

COPY products(product_type, category_3_level, product_id, barcode, product_name, brand, sale_price, cost_price, stock_quantity, reserved_quantity, estimated_oos_date, min_stock_threshold, max_stock_threshold, unit_of_measure, base_unit_code, conversion_rate, attributes, related_product_code, image_urls, weight_gram, is_active, is_direct_sale, description, note_template, location, component_items, warranty_period, maintenance_cycle) 
FROM '/import_data/processed_merged_products.csv' DELIMITER ',' CSV HEADER;

COPY inventory_stocks(branch_id, product_id, quantity_on_hand) 
FROM '/import_data/inventory_stocks.csv' DELIMITER ',' CSV HEADER;

COPY customers( created_branch_id, customer_type, customer_id, customer_name, phone, address, shipping_area, ward_commune, company_name, tax_id, identity_card_number, dob, gender, email, facebook_url, customer_group, note, created_by, created_at, last_transaction_date, current_debt, total_sales, net_sales, status ) 
FROM '/import_data/processed_merged_customers.csv' DELIMITER ',' CSV HEADER;

COPY suppliers ( branch_id, supplier_id, supplier_name, email, phone, address, area, ward_commune, total_purchased, current_liability, tax_id, note, supplier_group, status, net_purchased, company_name, created_by, created_at ) 
FROM '/import_data/processed_merged_suppliers.csv' DELIMITER ',' CSV HEADER;

COPY invoices ( invoice_id, branch_id, created_at, updated_at, status, shipping_status, subtotal, invoice_discount, total_amount, amount_paid, salesperson_name, customer_id, note )
FROM '/import_data/invoices.csv' DELIMITER ',' CSV HEADER;

COPY invoice_items ( invoice_id, product_id, barcode, product_name, brand, unit_of_measure, quantity, unit_price, item_discount_amount, sale_price, line_total, warranty, maintenance_cycle )
FROM '/import_data/invoice_items.csv' DELIMITER ',' CSV HEADER;

ALTER SYSTEM SET wal_level = 'logical';
CREATE PUBLICATION erp_debezium_pub FOR ALL TABLES;
