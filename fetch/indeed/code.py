#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

from jobspy import scrape_jobs


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


def _format_salary(job) -> str:
    # jobspy fields: min_amount, max_amount, currency, interval
    min_amount = job.get("min_amount")
    max_amount = job.get("max_amount")
    currency = job.get("currency")
    interval = job.get("interval")
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
        "datePublished": _na(job.get("date_posted")),
        "source": "python-jobspy",
        "platform": "Indeed",
        "company": _na(job.get("company")),
        "companyDescription": _na(job.get("company_description")),
        "companyUrl": _na(job.get("company_url")),
        "jobTitle": _na(job.get("title")),
        "jobDescription": _na(job.get("description")),
        "jobSalary": _format_salary(job),
        "jobUrl": _na(job.get("job_url") or job.get("job_url_direct")),
        "jobType": _join_if_list(job.get("job_type"), sep=", "),
        "jobCity": _city_from_location(str(job.get("location"))),
        "query": query,
    }


def run_one_query(search_term: str, location: str = "quebec city, qc, canada"):
    city_state = ','.join(location.split(',')[:-1]).strip().lower()
    country = location.split(',')[-1].strip().lower()

    jobs = scrape_jobs(
        site_name="indeed",
        search_term=search_term,
        location=city_state,
        country_indeed=country,
        results_wanted=32,
        hours_old=7 * 24,
        distance=20,  # miles
        sort_by="relevance",
    )
    # DataFrame -> list[dict]
    return jobs.to_dict(orient="records")


# ---- n8n Python node entrypoint ----
out = []

for it in _items:
    j = it.get("json") or {}
    if (query := _na(j.get("query"))) == "N/A":
        continue
    if (location := _na(j.get("location"))) == "N/A":
        continue
    jobs = run_one_query(str(query), str(location))
    for job in jobs:
        out.append({"json": _parse(job, str(query))})

return out