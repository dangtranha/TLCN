from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(seconds=10),
    "start_date": datetime(2024, 1, 1),
}

with DAG(
    dag_id="ETL_process",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description="Silver to Gold ETL Process and Gold to Postgres Sync",
) as dag:

    ETL_process = BashOperator(
        task_id="Bronze_to_Silver",
        bash_command="""docker exec spark-master /opt/spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        --packages io.delta:delta-core_2.12:2.4.0,org.apache.hadoop:hadoop-aws:3.3.2 \
        --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
        --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog \
        /opt/spark/work-dir/batch-etl/main.py""",
    )

    Dimensions = BashOperator(
        task_id="Silver_to_Gold_Dimensions",
        bash_command="""
            docker exec spark-master bash -c '
            export PYTHONPATH=/opt/spark/work-dir/batch-etl && 
            /opt/spark/bin/spark-submit \
                --master spark://spark-master:7077 \
                --packages io.delta:delta-core_2.12:2.4.0,org.apache.hadoop:hadoop-aws:3.3.4 \
                --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
                --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" \
                /opt/spark/work-dir/batch-etl/silver_to_gold/etl_dimensions.py
            '
        """,
    )


    Date_Dimension = BashOperator(
        task_id="Silver_to_Gold_Date_Dimension",
        bash_command="""docker exec spark-master bash -c '
            export PYTHONPATH=/opt/spark/work-dir/batch-etl && 
            /opt/spark/bin/spark-submit \
                --master spark://spark-master:7077 \
                --packages io.delta:delta-core_2.12:2.4.0,org.apache.hadoop:hadoop-aws:3.3.4 \
                --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
                --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" \
                /opt/spark/work-dir/batch-etl/silver_to_gold/etl_date_dim.py
            '
        """,
    )


    Facts = BashOperator(
        task_id="Silver_to_Gold_Facts",
        bash_command="""docker exec spark-master bash -c '
            export PYTHONPATH=/opt/spark/work-dir/batch-etl && 
            /opt/spark/bin/spark-submit \
                --master spark://spark-master:7077 \
                --packages io.delta:delta-core_2.12:2.4.0,org.apache.hadoop:hadoop-aws:3.3.4 \
                --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
                --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" \
                /opt/spark/work-dir/batch-etl/silver_to_gold/etl_facts.py
            '
        """,
    )
    Serving  = BashOperator(
        task_id="Sync_Gold_to_Postgres_erp_serving",
        bash_command="""docker exec spark-master bash -c '
            export PYTHONPATH=/opt/spark/work-dir/batch-etl && 
            /opt/spark/bin/spark-submit \
                --master spark://spark-master:7077 \
                --packages io.delta:delta-core_2.12:2.4.0,org.apache.hadoop:hadoop-aws:3.3.4,org.postgresql:postgresql:42.7.1 \
                --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
                --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog \
                /opt/spark/work-dir/batch-etl/gold_to_serving/sync_postgres.py
            '
        """,
    )
    

    ETL_process >> Dimensions  >> Date_Dimension >> Facts >> Serving