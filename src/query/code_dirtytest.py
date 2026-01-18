#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

import pandas as pd

from src.utils.format.job_title import format_job_title


def _na(v, default="N/A"):
    if v is None:
        return default
    if isinstance(v, float) and v != v:  # NaN
        return default
    if isinstance(v, str) and not v.strip():
        return default
    return v


def _join_if_list(v, sep=", ", default="N/A"):
    if v is None:
        return default
    if isinstance(v, float) and v != v:  # NaN
        return default
    if isinstance(v, list):
        return sep.join([str(x) for x in v if x is not None and str(x).strip()]) or default
    if isinstance(v, str):
        return v if v.strip() else default
    return str(v)


def _city_from_location(location: str) -> str:
    location = _na(location)
    if not location or location == "N/A":
        return "N/A"
    # jobspy often returns "City, ST" (or similar). Keep first chunk as "city".
    return location.split(",")[0].strip().lower() or "N/A"


def _format_lang_title(value: str, gender: str = "man") -> str:
    gender = (gender or "").strip().lower()
    if gender not in {"man", "woman"}:
        raise NotImplementedError("Only 'man' and 'woman' genders are supported.")
    
    # Basic normalization rules
    value = value.strip()

    # If value is an email use the domain name as title
    if value and "@" in value:
        parts = value.split("@")
        domain = parts[1]
        domain_parts = domain.split(".")
        title = domain_parts[0]
        return title.capitalize() or "N/A"

    # If value contains separators like '/', '|', or '\'
    # take the first part as title
    for sep in ['/', '|', '\\']:
        if sep in value:
            parts = value.split(sep)
            title = parts[0].strip()
            return title.strip() or "N/A"

    return value or "N/A"


# TODO: expand with more formatting rules as needed.
def _format_lang_desc(value: str) -> str:
    return value or "N/A"


def format_salary(job: dict) -> str:
    # jobspy fields: min_amount, max_amount, currency, interval
    min_amount = job["min_amount"]
    max_amount = job["max_amount"]
    currency = job["currency"]
    interval = job["interval"]
    if min_amount is None and max_amount is None:
        return "N/A"
    # normalize numbers
    def _num(x):
        try:
            v = float(x)
            # Treat NaN (including from strings like 'nan') as missing
            if v != v:
                return None
            return v
        except Exception:
            return None
    lo = _num(min_amount)
    hi = _num(max_amount)
    if lo is None and hi is None:
        return "N/A"
    if lo is not None and hi is not None and lo != hi:
        amt = f"{lo:,.0f}-{hi:,.0f}"
    else:
        one = lo if lo is not None else hi
        amt = f"{one:,.0f}"
    # Example output: "CAD 80,000-95,000 / year"
    cur = _na(currency, ""); unit = _na(interval, "")
    suffix = f" / {unit}" if unit not in ("", "N/A") else ""
    prefix = f"{cur} " if cur not in ("", "N/A") else ""
    return f"{prefix}{amt}{suffix}".strip()


def _parse(job: dict, query: str) -> dict:
    return {
        "datePublished": _na(job["date_posted"]),
        "source": "python-jobspy",
        "platform": "Indeed",
        "company": _format_lang_title(job["company"]),
        "companyDescription": _format_lang_desc(job["company_description"]),
        "companyUrl": _na(job["company_url"]),
        "jobTitle": format_job_title(job["title"], gender="man"),
        "jobDescription": _format_lang_desc(job["description"]),
        "jobSalary": format_salary(job),
        "jobUrl": _na(job["job_url"] or job["job_url_direct"]),
        "jobType": _join_if_list(job["job_type"], sep=", "),
        "jobCity": _city_from_location(str(job["location"])),
        "query": query,
    }


# ---- n8n Python node entrypoint ----
outs = []

jobs = pd.read_json(".data/query/jobs.json", orient="records")
jobs = jobs.to_dict(orient="records")
for job in jobs:
    outs.append({"json": _parse(job, "")})

print(f"Parsed {len(outs)} jobs JSON data.")
for out, job in zip(outs, jobs):
    print(out["json"]["jobTitle"], "\t\t===>\t\t", job["title"])