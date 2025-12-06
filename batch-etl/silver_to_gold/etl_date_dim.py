# batch-etl/silver_to_gold/etl_date_dim.py
from pyspark.sql import functions as F
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'batch-etl/core/gold_utlis.py')))
from core.gold_utils import get_spark_session, write_gold_delta

def create_dim_date(spark, start_date='2023-01-01', end_date='2025-12-31'):
    print(f"Generating Date Dim from {start_date} to {end_date}...")
    
    # Tạo sequence ngày
    df = spark.sql(f"SELECT sequence(to_date('{start_date}'), to_date('{end_date}'), interval 1 day) as date_range")
    df = df.withColumn("date_key", F.explode(F.col("date_range")))
    
    # Tính toán các thuộc tính
    dim_date = df.select(
        F.col("date_key"),
        F.year("date_key").alias("year"),
        F.quarter("date_key").alias("quarter"),
        F.month("date_key").alias("month"),
        F.dayofmonth("date_key").alias("day"),
        F.dayofweek("date_key").alias("day_of_week"), # 1=Sunday
        F.date_format("date_key", "E").alias("day_name_short"), # Mon, Tue
        F.date_format("date_key", "EEEE").alias("day_name_full"), # Monday
        F.date_format("date_key", "MMM").alias("month_name_short"), # Jan
        F.weekofyear("date_key").alias("week_of_year"),
        F.when((F.dayofweek("date_key") == 1) | (F.dayofweek("date_key") == 7), True).otherwise(False).alias("is_weekend")
    )
    
    write_gold_delta(dim_date, "dim_date", mode="overwrite")

if __name__ == "__main__":
    spark = get_spark_session("Gold_Date_Dim_Gen")
    create_dim_date(spark)
    spark.stop()