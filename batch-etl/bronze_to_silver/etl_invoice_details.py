from core.utils import write_delta
from pyspark.sql import functions as F, types as T
import os

BRONZE = f"s3a://{os.getenv('BRONZE_BUCKET','bronze')}/topics/ptk_erp.public.invoice_items/partition=0/*.json"
SILVER = f"s3a://{os.getenv('SILVER_BUCKET','silver')}/invoice_details/"

def run(spark):
    df = spark.read.json(BRONZE)
    df_after = df.selectExpr(
        "after.invoice_item_id as invoice_item_id",
        "after.invoice_id as invoice_id",
        "after.product_id as product_id",
        "after.quantity as quantity",
        "after.unit_price as unit_price",
        "after.sale_price as sale_price",
        "after.line_total as line_total"
    )
    df_clean = (
        df_after
        .withColumn("invoice_item_id", F.col("invoice_item_id").cast("long"))
        .withColumn("invoice_id", F.col("invoice_id").cast("string"))
        .withColumn("product_id", F.col("product_id").cast("string"))
        .withColumn("quantity", F.col("quantity").cast("int"))
        .withColumn("unit_price", F.col("unit_price").cast(T.DecimalType(18, 2)))
        .withColumn("sale_price", F.col("sale_price").cast(T.DecimalType(18, 2)))
        .withColumn("line_total", F.col("line_total").cast(T.DecimalType(18, 2)))
        .withColumn("etl_loaded_at", F.current_timestamp())
    )
    df_clean = df_clean.filter(
        (F.col("invoice_id").isNotNull())
        & (F.col("product_id").isNotNull())
        & (F.col("quantity") > 0)
        & (F.col("unit_price") >= 0)
    )
    write_delta(
        df_clean,
        SILVER,
        mode="append"
    )
