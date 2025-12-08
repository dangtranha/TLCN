from core.utils import dedup_latest, write_delta
from pyspark.sql import functions as F, types as T
import os

BRONZE = f"s3a://{os.getenv('BRONZE_BUCKET','bronze')}/topics/ptk_erp.public.suppliers/partition=0/*.json"
SILVER = f"s3a://{os.getenv('SILVER_BUCKET','silver')}/suppliers/"

def run_etl(spark):
    df = spark.read.json(BRONZE)
    df_after = df.selectExpr(
        "after.supplier_id as supplier_id",
        "after.supplier_name as supplier_name",
        "after.phone as phone",
        "after.address as address",
        "after.tax_id as tax_id",
        "after.current_liability as current_liability",
        "after.status as status"
    )
    df_clean = (
        df_after
        .withColumn("supplier_id", F.col("supplier_id").cast("string"))
        .withColumn("current_liability", F.col("current_liability").cast(T.DecimalType(18, 2)))
        .withColumn("etl_loaded_at", F.current_timestamp())
    )

    df_clean = df_clean.filter(
        (F.col("supplier_id").isNotNull())
        & (F.col("current_liability") >= 0)
    )
    df_clean = dedup_latest(df_clean, ["supplier_id"], order_col="etl_loaded_at")

    write_delta(
        df_clean,
        SILVER,
        mode="overwrite"
    )
