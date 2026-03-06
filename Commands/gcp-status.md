Show current GCP / Vertex AI status for the active project.

Steps:
1. Get the active project: `gcloud config get-value project`
2. Run these in parallel:
   a. List running/recent Vertex AI custom jobs: `gcloud ai custom-jobs list --region=europe-west1 --filter="state=JOB_STATE_RUNNING OR state=JOB_STATE_PENDING" --format="table(name,state,createTime)" 2>/dev/null || gcloud ai custom-jobs list --region=us-central1 --filter="state=JOB_STATE_RUNNING OR state=JOB_STATE_PENDING" --format="table(name,state,createTime)" 2>/dev/null`
   b. List recent batch prediction jobs: `gcloud ai batch-prediction-jobs list --region=europe-west1 --format="table(name,state,createTime)" --limit=5 2>/dev/null`
   c. Check billing account: `gcloud billing accounts list --format="table(name,displayName,open)" 2>/dev/null`
3. Show a clean summary:
   - Active project
   - Running/pending jobs (if any)
   - Recent batch predictions
   - Any errors or warnings

Important:
- If gcloud is not authenticated, say so clearly and suggest `gcloud auth login`
- If no jobs are running, say so clearly
- Try europe-west1 first, fallback to us-central1
