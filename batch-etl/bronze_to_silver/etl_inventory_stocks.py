from core.utils import write_delta
from pyspark.sql import functions as F
import os

BRONZE = f"s3a://{os.getenv('BRONZE_BUCKET','bronze')}/topics/ptk_erp.public.inventory_stocks/partition=0/*.json"
SILVER = f"s3a://{os.getenv('SILVER_BUCKET','silver')}/inventory_stocks/"

def run(spark):
    df = spark.read.json(BRONZE)
    df_after = df.selectExpr(
        "after.product_id as product_id",
        "after.branch_id as branch_id",
        "after.quantity_on_hand as quantity_on_hand"
    )
    df_clean = (
        df_after
        .withColumn("product_id", F.col("product_id").cast("string"))
        .withColumn("branch_id", F.col("branch_id").cast("string"))
        .withColumn("quantity_on_hand", F.col("quantity_on_hand").cast("decimal(18,3)"))
        .withColumn("snapshot_date", F.current_date())
        .withColumn("etl_loaded_at", F.current_timestamp())
    )
    df_clean = df_clean.filter(
        (F.col("product_id").isNotNull())
        & (F.col("branch_id").isNotNull())
        & (F.col("quantity_on_hand") >= 0)
    )
    write_delta(
        df_clean,
        SILVER,
        mode="append",
        partition_by="snapshot_date"
    )
