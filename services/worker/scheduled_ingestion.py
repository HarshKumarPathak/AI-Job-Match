"""Simple long-running scheduler for periodic job ingestion."""

import os
import time

from run_ingestion import main


def run() -> None:
    interval_minutes = int(os.getenv("INGEST_INTERVAL_MINUTES", "360"))
    while True:
        main()
        time.sleep(max(5, interval_minutes * 60))


if __name__ == "__main__":
    run()
