# batch-etl/gold_to_serving/sync_postgres.py
import sys
import os
from pyspark.sql import functions as F

# Thêm đường dẫn để import core.gold_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'batch-etl/core/gold_utlis.py')))
from core.gold_utils import get_spark_session, GOLD_PATH

# Cấu hình PostgreSQL (Dựa trên docker-compose của bạn)
DB_HOST = "postgres"
DB_PORT = "5432"
DB_NAME = "erp_db"      # <-- Sửa thành erp_db
DB_USER = "postgres"    # <-- Sửa thành postgres
DB_PASSWORD = "postgres" # <-- Sửa thành postgres

# URL kết nối JDBC
JDBC_URL = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
JDBC_PROPERTIES = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "org.postgresql.Driver"
}

def write_to_postgres(df, table_name):
    """
    Ghi DataFrame vào PostgreSQL.
    Chế độ 'overwrite' sẽ xóa bảng cũ và tạo bảng mới.
    """
    print(f"--> Syncing table '{table_name}' to PostgreSQL...")
    try:
        (df.write
            .format("jdbc")
            .option("url", JDBC_URL)
            .option("dbtable", f"public.{table_name}") # Ghi vào schema public
            .option("user", DB_USER)
            .option("password", DB_PASSWORD)
            .option("driver", "org.postgresql.Driver")
            .mode("overwrite")
            .save())
        print(f"--> [SUCCESS] Synced '{table_name}'")
    except Exception as e:
        print(f"--> [ERROR] Failed to sync '{table_name}': {str(e)}")

def run(spark):
    # Danh sách các bảng cần đồng bộ
    tables = [
        "dim_products",
        "dim_customers",
        "dim_branches",
        "dim_suppliers",
        "dim_date",
        "fact_sales",
        "fact_inventory_daily"
    ]

    for table in tables:
        # 1. Đọc dữ liệu từ MinIO (Gold Layer)
        path = f"{GOLD_PATH}/{table}"
        try:
            df = spark.read.format("delta").load(path)
            
            # 2. Ghi thẳng vào Postgres
            write_to_postgres(df, table)
            
        except Exception as e:
            print(f"Skipping {table} because data not found in Gold: {e}")

if __name__ == "__main__":
    # Khởi tạo Spark Session (Tái sử dụng config MinIO từ gold_utils)
    spark = get_spark_session("Gold_to_Postgres_Sync")
    run(spark)
    spark.stop()