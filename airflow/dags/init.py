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
    dag_id="init_project",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description="Auto create buckets on MinIO",
) as dag:

    init_minio_alias = BashOperator(
        task_id="init_minio_alias",
        bash_command=(
            "docker exec minio-mc mc alias set local http://minio:9000 "
            "minioadmin minioadmin"
        ),
    )

    create_bronze = BashOperator(
        task_id="create_bucket_bronze",
        bash_command="docker exec minio-mc mc mb local/bronze || true",
    )

    create_silver = BashOperator(
        task_id="create_bucket_silver",
        bash_command="docker exec minio-mc mc mb local/silver || true",
    )

    create_gold = BashOperator(
        task_id="create_bucket_gold",
        bash_command="docker exec minio-mc mc mb local/gold || true",
    )

    set_policy = BashOperator(
        task_id="set_bucket_access",
        bash_command=(
            "docker exec minio-mc mc anonymous set public local/bronze "
            "&& docker exec minio-mc mc anonymous set public local/silver "
            "&& docker exec minio-mc mc anonymous set public local/gold"
        ),
    )
    create_postgres_connector = BashOperator(
        task_id="create_postgres_connector",
        bash_command="""
            curl -X POST http://connect:8083/connectors \
            -H "Content-Type: application/json" \
            -d @/opt/debezium_config/connector-postgresql.json
        """
    )

    create_minio_connector = BashOperator(
        task_id="create_minio_connector",
        bash_command="""
            curl -X POST http://connect:8083/connectors \
            -H "Content-Type: application/json" \
            -d @/opt/debezium_config/connector-minio.json
        """
    )

    init_minio_alias >> [create_bronze, create_silver, create_gold] >> set_policy >> create_postgres_connector >> create_minio_connector