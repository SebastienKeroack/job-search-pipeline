#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================
"""Script to query for jobs and save results locally for further analysis

# Example run the script:
```bash
python -m job_search_pipeline.query.query_dirtytest
```

# Example usage: Load and inspect saved jobs CSV
```python
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", 50)
jobs = pd.read_json(".data/query/jobs.json", orient="records")
jobs.columns
jobs["job_url"][0]
```
"""

import json
from datetime import date, datetime
from os import makedirs
from os.path import exists
from pathlib import Path

from job_search_pipeline.query import Query

def _load_json_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _json_default(v):
    # datetime/date (and pandas Timestamp behaves similarly)
    if isinstance(v, (datetime, date)):
        return v.isoformat()

    # numpy scalars often have .item()
    item = getattr(v, "item", None)
    if callable(item):
        try:
            return item()
        except Exception:
            pass

    # fallback
    return str(v)


def _save_json_records(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=_json_default)
    tmp.replace(path)


def run():
    # Ensure data directory exists
    if not exists(".data/query"):
        makedirs(".data/query")

    # Query site
    jobs = Query(
        query="indeed: (developer OR développeur) (kubernetes OR k8s)",
        location="Ville de Québec, QC, Canada",
        distance_unit=20,
        distance_use_km=True,
        days_old=7,
        results_wanted=20,
        sort_by="relevance",
    ).scrape()
    out_path = Path(".data/query/jobs.json")

    # Append results (keep valid JSON array). True file-append isn't possible for JSON arrays
    # without rewriting the file, so we load+merge+write.
    existing = _load_json_records(out_path)
    new_records = jobs

    seen = set()
    merged: list[dict] = []
    for rec in existing:
        key = rec.get("job_url")
        if key in seen:
            continue
        seen.add(key)
        merged.append(rec)
    added = 0
    for rec in new_records:
        key = rec.get("job_url")
        if key in seen:
            continue
        seen.add(key)
        merged.append(rec)
        added += 1

    _save_json_records(out_path, merged)
    print(f"Loaded {len(existing)} existing records; appended {added}; total {len(merged)} -> {out_path}")

if __name__ == "__main__":
    run()
