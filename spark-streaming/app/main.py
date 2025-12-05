"""Entrypoint to run Silver and Gold streaming jobs together.

Creates a single SparkSession and starts both jobs so they run in the
same process. Config paths can be overridden with the following env vars:
  - KAFKA_CONF
  - SILVER_CONF
  - GOLD_CONF

Note: running multiple structured streaming queries from a single Spark
Session is supported; both jobs share the same JVM/process.
"""
from __future__ import annotations

import os
import signal
import sys
from pyspark.sql import SparkSession

from common import load_config
from streaming_silver import run_silver
from streaming_gold import run_gold


def create_spark_session(app_name: str = "streaming-main") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.executor.cores", "2")
        .config("spark.executor.memory", "1g")
        .config("spark.cores.max", "2")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )


def main():
    kafka_conf_path = os.environ.get("KAFKA_CONF", "/opt/config/kafka.conf")
    silver_conf_path = os.environ.get("SILVER_CONF", "/opt/config/silver.conf")
    gold_conf_path = os.environ.get("GOLD_CONF", "/opt/config/gold.conf")

    kafka_conf = load_config(kafka_conf_path) if os.path.exists(kafka_conf_path) else {}
    silver_conf = load_config(silver_conf_path)
    gold_conf = load_config(gold_conf_path)

    spark = create_spark_session()

    # Start silver and gold jobs
    print("[START] launching silver streams...")
    silver_queries = run_silver(spark, kafka_conf, silver_conf)

    print("[START] launching gold stream...")
    gold_query = run_gold(spark, silver_conf, gold_conf)

    # Ensure we stop gracefully on SIGTERM/SIGINT
    def _stop(signum, frame):
        print("[INFO] Received stop signal, stopping streams...")
        try:
            for q in list(spark.streams.active):
                q.stop()
        except Exception:
            pass
        try:
            spark.stop()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    try:
        spark.streams.awaitAnyTermination()
    except KeyboardInterrupt:
        _stop(None, None)


if __name__ == "__main__":
    main()
