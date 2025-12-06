from core.utils import dedup_latest, write_delta
from pyspark.sql import functions as F, types as T
import os

BRONZE = f"s3a://{os.getenv('BRONZE_BUCKET','bronze')}/topics/ptk_erp.public.products/partition=0/*.json"
SILVER = f"s3a://{os.getenv('SILVER_BUCKET','silver')}/products/"

def run(spark):
    df = spark.read.json(BRONZE)
    df_after = df.selectExpr(
        "after.product_id as product_id",
        "after.product_name as product_name",
        "after.brand as brand",
        "after.sale_price as sale_price",
        "after.cost_price as cost_price",
        "after.unit_of_measure as unit_of_measure",
    )
    df_clean = (
        df_after

        .withColumn("product_id", F.col("product_id").cast("string"))
        .withColumn("sale_price", F.col("sale_price").cast(T.DecimalType(18, 2)))
        .withColumn("cost_price", F.col("cost_price").cast(T.DecimalType(18, 2)))
        .withColumn("etl_loaded_at", F.current_timestamp())
    )
    df_clean = df_clean.filter(
        (F.col("product_id").isNotNull())
        & (F.col("sale_price") >= 0)
        & (F.col("cost_price") >= 0)
    )
    df_clean = dedup_latest(df_clean, ["product_id"], order_col="etl_loaded_at")
    write_delta(
        df_clean,
        SILVER,
        mode="overwrite"
    )
