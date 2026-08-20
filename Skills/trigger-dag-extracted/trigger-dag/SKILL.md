---
name: trigger-dag
description: Trigger an Apache Airflow DAG on a Google Cloud Composer instance. Use this skill whenever the user says "trigger dag", "run dag", "start dag", "fire dag", "launch dag", or provides a DAG name and configuration JSON and wants to start a run. Also trigger when the user says things like "run this dag with this config", "kick off <dag-name>", or "execute <dag-name> with these params".
---

# Trigger DAG

Triggers a DAG run on a Cloud Composer Airflow instance via the Airflow REST API.

## Setup

The script reads its configuration from environment variables. Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable       | Description                                         |
|----------------|-----------------------------------------------------|
| `AIRFLOW_URI`  | Base URL of the Cloud Composer Airflow instance     |

Auth is handled automatically via `gcloud auth print-access-token` — no extra config needed as long as `gcloud` is authenticated.

## When to use

- User says "trigger", "run", "start", "fire", "kick off", or "execute" a DAG
- User provides a DAG name (e.g. `sharpen-file`, `tree-growth-preprocessing`)
- User provides a JSON configuration block (inline or as a file path)

## How to use

Run the bundled Python script:

```bash
python /path/to/skill/scripts/trigger_dag.py \
  --dag-id <dag-name> \
  --conf '<json-string>'
```

Or pass a JSON file:

```bash
python /path/to/skill/scripts/trigger_dag.py \
  --dag-id <dag-name> \
  --conf-file /path/to/config.json
```

### Arguments

| Argument      | Required | Description                                                        |
|---------------|----------|--------------------------------------------------------------------|
| `--dag-id`    | Yes      | The DAG ID exactly as it appears in Airflow (e.g. `sharpen-file`) |
| `--conf`      | No*      | JSON string with the DAG run configuration                         |
| `--conf-file` | No*      | Path to a JSON file with the DAG run configuration                 |

*Either `--conf` or `--conf-file` is optional — omit both to trigger with an empty config.

### Installation

Requires stdlib + `requests` + `python-dotenv`:

```bash
pip install requests python-dotenv --break-system-packages
```

## Response format

After triggering, always report:
- **DAG run ID** (`dag_run_id`)
- **State** (should be `queued`)
- **DAG ID** confirmed

If the HTTP response is not 200, show the full error response so the user can debug.
