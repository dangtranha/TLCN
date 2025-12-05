from core.utils import dedup_latest, write_delta
from pyspark.sql import functions as F
import os

BRONZE = f"s3a://{os.getenv('BRONZE_BUCKET','bronze')}/topics/ptk_erp.public.customers/partition=0/*.json"
SILVER = f"s3a://{os.getenv('SILVER_BUCKET','silver')}/customers/"

def run(spark):
    df = spark.read.json(BRONZE)
    df_after = df.selectExpr(
        "after.customer_id as customer_id",
        "after.customer_name as customer_name",
        "after.phone as phone",
        "after.address as address",
        "after.customer_group as customer_group",
        "after.current_debt as current_debt",
        "after.status as status"
    )
    df_clean = (
        df_after
        .withColumn("customer_id", F.col("customer_id").cast("string"))
        .withColumn(
            "customer_name",
            F.regexp_replace(F.trim(F.col("customer_name")), r"\(.*?\)", "")
        )
        .withColumn("phone", F.regexp_replace(F.col("phone"), r"[^0-9]", ""))
        .withColumn("current_debt", F.col("current_debt").cast("decimal(18,2)"))
        .withColumn("status", F.col("status").cast("int"))
        .withColumn("etl_loaded_at", F.current_timestamp())
    )
    df_clean = df_clean.filter(
        F.col("customer_id").isNotNull()
    )
    df_clean = dedup_latest(df_clean, ["customer_id"], order_col="etl_loaded_at")
    write_delta(
        df_clean,
        SILVER,
        mode="overwrite"
    )
