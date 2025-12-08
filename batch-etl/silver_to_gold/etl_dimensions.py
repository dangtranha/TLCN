# batch-etl/silver_to_gold/etl_dimensions.py
from pyspark.sql import functions as F
import sys
import os

# Thêm đường dẫn để import được core.gold_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'batch-etl/core/gold_utlis.py')))

from core.gold_utils import get_spark_session, SILVER_PATH, write_gold_delta

def create_dim_products(spark):
    print("Processing Dim Products...")
    df = spark.read.format("delta").load(f"{SILVER_PATH}/products/")
    
    dim_df = df.select(
        F.col("product_id").alias("product_key"),
        F.col("product_id"),
        F.col("product_name"),
        F.col("brand"),
        F.col("unit_of_measure"),
        F.col("sale_price").alias("current_list_price"),
        F.col("cost_price").alias("current_cost_price"),
        F.current_timestamp().alias("last_updated")
    )
    write_gold_delta(dim_df, "dim_products")

def create_dim_customers(spark):
    print("Processing Dim Customers...")
    df = spark.read.format("delta").load(f"{SILVER_PATH}/customers/")
    
    dim_df = df.select(
        F.col("customer_id").alias("customer_key"),
        F.col("customer_id"),
        F.col("customer_name"),
        F.col("phone"),
        F.col("address"),
        F.col("customer_group"),
        F.col("status"),
        F.current_timestamp().alias("last_updated")
    )
    write_gold_delta(dim_df, "dim_customers")

def create_dim_branches(spark):
    print("Processing Dim Branches...")
    df = spark.read.format("delta").load(f"{SILVER_PATH}/branches/")
    
    dim_df = df.select(
        F.col("branch_id").alias("branch_key"),
        F.col("branch_id"),
        F.col("branch_name"),
        F.col("branch_type"),
        F.col("status"),
        F.current_timestamp().alias("last_updated")
    )
    write_gold_delta(dim_df, "dim_branches")

def create_dim_suppliers(spark):
    print("Processing Dim Suppliers...")
    df = spark.read.format("delta").load(f"{SILVER_PATH}/suppliers/")
    
    dim_df = df.select(
        F.col("supplier_id").alias("supplier_key"),
        F.col("supplier_id"),
        F.col("supplier_name"),
        F.col("phone"),
        F.col("address"),
        F.col("tax_id"),
        F.current_timestamp().alias("last_updated")
    )
    write_gold_delta(dim_df, "dim_suppliers")

if __name__ == "__main__":
    spark = get_spark_session("Gold_Dimensions_ETL")
    
    create_dim_products(spark)
    create_dim_customers(spark)
    create_dim_branches(spark)
    create_dim_suppliers(spark)
    
    spark.stop()