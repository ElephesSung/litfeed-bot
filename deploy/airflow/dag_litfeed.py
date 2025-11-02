
from datetime import datetime, timedelta
from pendulum import timezone
from airflow import DAG
from airflow.operators.bash import BashOperator

TZ = timezone("Europe/London")
REPO = "/path/to/litfeed-bot"  # <-- change this

with DAG(
    dag_id="litfeed_every_3_days",
    start_date=datetime(2025, 11, 1, 9, 0, tzinfo=TZ),
    schedule=timedelta(days=3),
    catchup=False,
    tags=["literature","gemini","mattermost"],
    max_active_runs=1,
) as dag:
    run_bot = BashOperator(
        task_id="run_litfeed",
        bash_command=(
            f"cd {REPO} && "
            f"export GOOGLE_API_KEY=$GOOGLE_API_KEY && "
            f"export MM_WEBHOOK_URL=$MM_WEBHOOK_URL && "
            f"python main.py >> run.log 2>&1"
        ),
        retries=1,
        retry_delay=timedelta(minutes=5),
    )
