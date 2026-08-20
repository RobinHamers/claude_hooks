#!/usr/bin/env python3
"""Trigger an Airflow DAG run on a Cloud Composer instance."""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

AIRFLOW_URI = os.environ.get("AIRFLOW_URI", "").rstrip("/")


def get_gcloud_token() -> str:
    result = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def trigger_dag(dag_id: str, conf: dict, logical_date: str | None = None) -> tuple[int, dict]:
    if not AIRFLOW_URI:
        print("ERROR: AIRFLOW_URI is not set. Copy .env.example to .env and fill it in.", file=sys.stderr)
        sys.exit(1)

    payload: dict = {"conf": conf}
    if logical_date:
        # Queued DAG runs are dequeued in ascending logical_date order, so an
        # earlier logical_date jumps ahead of runs already waiting in the queue.
        payload["logical_date"] = logical_date

    token = get_gcloud_token()
    response = requests.post(
        f"{AIRFLOW_URI}/api/v1/dags/{dag_id}/dagRuns",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    return response.status_code, response.json()


def main():
    parser = argparse.ArgumentParser(description="Trigger an Airflow DAG run")
    parser.add_argument("--dag-id", required=True, help="DAG ID to trigger")
    parser.add_argument("--conf", default=None, help="JSON string configuration")
    parser.add_argument("--conf-file", default=None, help="Path to JSON config file")
    parser.add_argument(
        "--logical-date",
        default=None,
        help=(
            "Explicit logical_date (ISO-8601, e.g. 2020-01-01T00:00:00+00:00). "
            "An earlier date than the pending runs makes this run start next. "
            "Must be unique for the DAG."
        ),
    )
    parser.add_argument(
        "--jump-queue",
        action="store_true",
        help="Shorthand for a very early logical_date (1970 + a unique offset), so this run is dequeued first.",
    )
    args = parser.parse_args()

    if args.conf_file:
        with open(args.conf_file) as f:
            conf = json.load(f)
    elif args.conf:
        conf = json.loads(args.conf)
    else:
        conf = {}

    logical_date = args.logical_date
    if args.jump_queue and not logical_date:
        # Unique-but-ancient timestamp: sorts before any realistic queued run.
        offset = int(time.time()) % 31_536_000
        logical_date = (
            datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=offset)
        ).isoformat()

    status_code, result = trigger_dag(args.dag_id, conf, logical_date)

    print(json.dumps(result, indent=2))

    if status_code != 200:
        print(f"\nERROR: HTTP {status_code}", file=sys.stderr)
        sys.exit(1)

    print(f"\nDAG run ID : {result.get('dag_run_id')}")
    print(f"State      : {result.get('state')}")
    print(f"Logical dt : {result.get('logical_date')}")


if __name__ == "__main__":
    main()
