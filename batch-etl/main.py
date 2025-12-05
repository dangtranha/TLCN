from pyspark.sql import SparkSession
from bronze_to_silver import etl_branches, etl_customers, etl_inventory_stocks, etl_invoice_details, etl_invoices, etl_products, etl_suppliers

def main():
    spark = SparkSession.builder \
        .appName("Batch ETL Bronze to Silver") \
        .master("spark://spark-master:7077") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

    # Chạy lần lượt các ETL
    #etl_branches.run(spark)
    #etl_customers.run(spark)
    #etl_inventory_stocks.run(spark)
    #etl_invoice_details.run(spark)
    #etl_invoices.run(spark)
    #etl_products.run(spark)
    etl_suppliers.run_etl(spark)

    spark.stop()

if __name__ == "__main__":
    main()
