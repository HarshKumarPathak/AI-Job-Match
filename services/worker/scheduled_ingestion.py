"""Simple resilient scheduler for periodic job ingestion."""

import os
import time

from run_ingestion import main


def run() -> None:
    interval_minutes = int(os.getenv("INGEST_INTERVAL_MINUTES", "360"))
    interval_seconds = max(5, interval_minutes * 60)

    while True:
        try:
            main()
        except Exception as exc:
            # Keep the scheduler alive so a temporary provider/network failure
            # does not permanently stop future ingestion cycles.
            print(f"Scheduled ingestion failed: {exc}", flush=True)

        time.sleep(interval_seconds)


if __name__ == "__main__":
    run()
