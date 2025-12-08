# batch-etl/core/gold_utils.py
import os
from pyspark.sql import SparkSession

# ... (Giữ nguyên phần khai báo biến môi trường ở trên) ...
SILVER_BUCKET = os.getenv("SILVER_BUCKET", "silver")
GOLD_BUCKET = os.getenv("GOLD_BUCKET", "gold")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

SILVER_PATH = f"s3a://{SILVER_BUCKET}"
GOLD_PATH = f"s3a://{GOLD_BUCKET}"

def get_spark_session(app_name):
    """
    Khởi tạo Spark Session với cấu hình Delta Lake và MinIO (S3A)
    """
    builder = (
        SparkSession.builder.appName(app_name)
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT)
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        
        # --- BỔ SUNG 2 DÒNG NÀY ---
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") # Quan trọng: Tắt SSL vì dùng HTTP
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        # --------------------------
        
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    )
    return builder.getOrCreate()

def write_gold_delta(df, table_name, partition_by=None, mode="overwrite"):
    # ... (Giữ nguyên hàm này) ...
    path = f"{GOLD_PATH}/{table_name}"
    writer = df.write.format("delta").mode(mode)
    
    if partition_by:
        writer = writer.partitionBy(partition_by)
        
    writer.option("mergeSchema", "true").save(path)
    print(f"--> [SUCCESS] Written {table_name} to {path}")