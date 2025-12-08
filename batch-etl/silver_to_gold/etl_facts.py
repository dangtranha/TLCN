# batch-etl/silver_to_gold/etl_facts.py
from pyspark.sql import functions as F
import sys
import os

# Thêm đường dẫn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'batch-etl/core/gold_utlis.py')))

from core.gold_utils import get_spark_session, SILVER_PATH, write_gold_delta

def create_fact_sales(spark):
    print("Processing Fact Sales...")
    # 1. Đọc dữ liệu Silver
    invoices_df = spark.read.format("delta").load(f"{SILVER_PATH}/invoices/")
    details_df = spark.read.format("delta").load(f"{SILVER_PATH}/invoice_details/")
    products_df = spark.read.format("delta").load(f"{SILVER_PATH}/products/")

    # 2. Join Invoices (Header) với Details
    sales_df = details_df.alias("d").join(
        invoices_df.alias("h"),
        on="invoice_id",
        how="inner"
    )

    # 3. Join với Products để lấy Cost Price (Tính giá vốn & Lợi nhuận)
    # Lưu ý: Đây là cost_price hiện tại (Simplified approach cho MVP)
    full_df = sales_df.join(
        products_df.alias("p"),
        on="product_id",
        how="left"
    )

    # 4. Chọn cột và tính toán
    fact_sales = full_df.select(
        F.col("d.invoice_item_id").alias("sales_key"),
        F.col("h.invoice_id"),
        F.col("h.invoice_date"),  # Giữ lại để partition
        F.col("h.created_at").alias("transaction_time"),
        F.col("h.customer_id").alias("customer_key"),
        F.col("h.branch_id").alias("branch_key"),
        F.col("d.product_id").alias("product_key"),
        F.col("h.salesperson_name"),
        
        # Metrics Sales
        F.col("d.quantity"),
        F.col("d.unit_price").alias("unit_list_price"),
        F.col("d.sale_price").alias("unit_actual_price"),
        F.col("d.line_total").alias("total_revenue"),
        
        # Metrics Profit
        F.col("p.cost_price").alias("unit_cost"),
        (F.col("d.quantity") * F.col("p.cost_price")).alias("total_cogs"),
        (F.col("d.line_total") - (F.col("d.quantity") * F.col("p.cost_price"))).alias("gross_profit")
    )

    # 5. Ghi ra Gold (Partition theo ngày)
    write_gold_delta(fact_sales, "fact_sales", partition_by="invoice_date", mode="overwrite")

def create_fact_inventory_snapshot(spark):
    print("Processing Fact Inventory Snapshot...")
    # 1. Đọc dữ liệu
    stocks_df = spark.read.format("delta").load(f"{SILVER_PATH}/inventory_stocks/")
    products_df = spark.read.format("delta").load(f"{SILVER_PATH}/products/")

    # 2. Join để lấy giá trị tồn kho
    df_joined = stocks_df.join(products_df, on="product_id", how="left")

    # 3. Transform
    fact_inv = df_joined.select(
        F.col("snapshot_date"),
        F.col("branch_id").alias("branch_key"),
        F.col("product_id").alias("product_key"),
        F.col("quantity_on_hand"),
        F.col("cost_price").alias("unit_cost_at_snapshot"),
        (F.col("quantity_on_hand") * F.col("cost_price")).alias("total_inventory_value")
    )

    # 4. Ghi ra Gold (Append mode vì mỗi ngày là 1 snapshot mới)
    # Lưu ý: Cần xử lý dedup nếu chạy lại trong cùng 1 ngày, ở đây dùng overwrite partition động
    write_gold_delta(
        fact_inv, 
        "fact_inventory_daily", 
        partition_by="snapshot_date", 
        mode="overwrite" 
    )
    # Mode overwrite + partitionBy sẽ chỉ overwrite partition (ngày) đó, không xóa dữ liệu ngày cũ.

if __name__ == "__main__":
    spark = get_spark_session("Gold_Facts_ETL")
    create_fact_sales(spark)
    create_fact_inventory_snapshot(spark)
    spark.stop()