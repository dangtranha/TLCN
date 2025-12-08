from pyspark.sql import functions as F, Window

def dedup_latest(df, keys, order_col="etl_loaded_at"):
    from pyspark.sql import Window, functions as F
    w = Window.partitionBy(*keys).orderBy(F.col(order_col).desc())
    return df.withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1).drop("_rn")

def write_delta(df, path, partition_by=None, mode="overwrite"):
    writer = df.write.format("delta").mode(mode).option("overwriteSchema", "true")
    if partition_by:
        writer = writer.partitionBy(partition_by)
    writer.save(path)
    print(f"Written {path}")
