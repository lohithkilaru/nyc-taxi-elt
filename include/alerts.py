"""Failure to complete run triggers an alert"""

import logging 
import os 

import requests

log = logging.getLogger(__name__)

def notify_failure(context: dict) -> None
    """Called by airflow when a task fails at all retries"""
    ti = context.get("task_instance")
    dag_id = getattr(ti, "dag_id", "unknown_dag")
    task_id = getattr(ti, "task_id", "unknown_task")
    run_id = getattr(ti, "run_id", "unknown_run")
    error = context.get("exception")

    message = (
        f":red_circle: Airflow task failed\n"
        f"DAG ID: {dag_id}\n"
        f"Task ID: {task_id}\n"
        f"Run ID: {run_id}\n"
        f"Error: {error}\n"
    )
    
    log.error(message)


    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook_url:
        try:
            requests.post(webhook_url, json={"text": message}, timeout=10)
        except requests.RequestException as err:
            log.error("Could not send Slack alert: %s", err)

