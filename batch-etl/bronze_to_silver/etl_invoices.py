from core.utils import dedup_latest, write_delta
from pyspark.sql import functions as F, types as T
import os

BRONZE = f"s3a://{os.getenv('BRONZE_BUCKET','bronze')}/topics/ptk_erp.public.invoices/partition=0/*.json"
SILVER = f"s3a://{os.getenv('SILVER_BUCKET','silver')}/invoices/"

def run(spark):
    df = spark.read.json(BRONZE)
    df_after = df.selectExpr(
        "after.invoice_id as invoice_id",
        "after.created_at as created_at",
        "after.status as status",
        "after.subtotal as subtotal",
        "after.invoice_discount as invoice_discount",
        "after.total_amount as total_amount",
        "after.salesperson_name as salesperson_name",
        "after.customer_id as customer_id",
        "after.branch_id as branch_id"
    )
    df_clean = (
        df_after
        .withColumn("invoice_id", F.col("invoice_id").cast("string"))
        .withColumn("customer_id", F.col("customer_id").cast("string"))
        .withColumn("branch_id", F.col("branch_id").cast("string"))
        .withColumn("subtotal", F.col("subtotal").cast(T.DecimalType(18, 2)))
        .withColumn("invoice_discount", F.col("invoice_discount").cast(T.DecimalType(18, 2)))
        .withColumn("total_amount", F.col("total_amount").cast(T.DecimalType(18, 2)))
        .withColumn("created_at", (F.col("created_at") / 1000000).cast("timestamp"))
        .withColumn("invoice_date", F.to_date("created_at"))
        .withColumn("etl_loaded_at", F.current_timestamp())
    )

    df_clean = df_clean.filter(
        (F.col("invoice_id").isNotNull())
        & (F.col("total_amount") >= 0)
    )
    df_clean = dedup_latest(df_clean, ["invoice_id"], order_col="created_at")
    write_delta(
        df_clean,
        SILVER,
        mode="overwrite",
        partition_by="invoice_date"
    )
