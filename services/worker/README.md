# Job ingestion worker

This folder contains a deliberately small ingestion runner. It keeps source fetching
separate from the API while remaining easy to understand and schedule with cron,
Task Scheduler, GitHub Actions, or a cloud scheduler later.

From the repository root:

powershell
$env:PYTHONPATH="services/api"
python services/worker/run_ingestion.py --source demo
python services/worker/run_ingestion.py --source arbeitnow

The bundled sources are the local demo source and the documented Arbeitnow API. Real providers should be added
as JobSource adapters only when their official API/feed/public endpoint permits use.

The runner commits normalized and deduplicated jobs through the same ingestion service
used by the API.
