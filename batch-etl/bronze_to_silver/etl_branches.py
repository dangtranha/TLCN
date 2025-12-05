from core.utils import dedup_latest, write_delta
from pyspark.sql import functions as F
import os

BRONZE = f"s3a://{os.getenv('BRONZE_BUCKET','bronze')}/topics/ptk_erp.public.branches/partition=0/*.json"
SILVER = f"s3a://{os.getenv('SILVER_BUCKET','silver')}/branches/"

def run(spark):
    df = spark.read.json(BRONZE)
    df_after = df.selectExpr("after.branch_id as branch_id",
                         "after.branch_name as branch_name",
                         "after.branch_type as branch_type",
                         "after.address as address",
                         "after.status as status")
    df_clean = (
        df_after
        .withColumn("branch_id", F.col("branch_id").cast("string"))
        .withColumn("branch_name", F.trim(F.col("branch_name")))
        .withColumn("branch_type", F.trim(F.col("branch_type")))
        .withColumn("address", F.trim(F.col("address")))
        .withColumn("status", F.trim(F.col("status")))
        .withColumn("etl_loaded_at", F.current_timestamp())
    )

    df_clean = df_clean.filter(
        F.col("branch_id").isNotNull()
    )
    
    df_clean = dedup_latest(df_clean, ["branch_id"], order_col="etl_loaded_at")
    
    write_delta(
        df_clean,
        SILVER,
        mode="overwrite"
    )
