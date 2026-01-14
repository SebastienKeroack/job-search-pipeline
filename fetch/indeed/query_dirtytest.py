#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================
"""Script to query Indeed for jobs and save results locally for further analysis

# Example run the script:
```bash
python fetch/indeed/query_dirtytest.py
```

# Example usage: Load and inspect saved jobs CSV
```python
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", 50)
jobs = pd.read_json(".data/indeed/jobs.json", orient="records")
jobs.columns
jobs["job_url"][0]
```
"""

from os import makedirs
from os.path import exists
from jobspy import scrape_jobs


def run():
    # Ensure data directory exists
    if not exists(".data/indeed"):
        makedirs(".data/indeed")
    # Query Indeed
    jobs = scrape_jobs(
        site_name="indeed",
        search_term="développeur python",
        location="val-belair, qc",
        country_indeed="canada",
        results_wanted=5,
        hours_old=7 * 24,
        distance=20, # in miles
        sort_by="relevance",
    )
    # Save it locally as JSON
    jobs.to_json(
        ".data/indeed/jobs.json",
        orient="records",
        indent=2,
        force_ascii=False
    )

if __name__ == "__main__":
    run()