#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

import re
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


def normalize_inclusive_job_title(value: str, gender: str = "man") -> str:
    """Normalize inclusive French job titles to a single gendered form.

    Examples:
      - "Développeur/Développeuse" -> "Développeur" (man) / "Développeuse" (woman)
      - "Développeuse/Développeur" -> "Développeur" (man) / "Développeuse" (woman)
      - "Développeur(se)"          -> "Développeur" (man) / "Développeuse" (woman)
      - "Développeur(euse)"        -> "Développeur" (man) / "Développeuse" (woman)
      - "Développeur.euse"         -> "Développeur" (man) / "Développeuse" (woman)
      - "Chargé(e)"                -> "Chargé" (man) / "Chargée" (woman)

    Notes:
      - This function is intentionally conservative.
      - It does not truncate on separators like '/', '|', '\\'.
    """

    value = value or ""
    gender = (gender or "").strip().lower()
    if gender not in {"man", "woman"}:
        raise NotImplementedError("Only 'man' and 'woman' genders are supported.")

    # 1) Handle paired forms like "Développeuse/Développeur".
    pair_pattern = re.compile(
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ]+)(eur|euse)\s*/\s*\1(eur|euse)\b",
        re.IGNORECASE,
    )

    def repl_pair(match: re.Match) -> str:
        root = match.group(1)
        s1 = match.group(2).lower()
        s2 = match.group(3).lower()
        if {s1, s2} != {"eur", "euse"}:
            return match.group(0)
        return f"{root}{'eur' if gender == 'man' else 'euse'}"

    value = pair_pattern.sub(repl_pair, value)

    # 2) Handle words like "Développeur(euse)" / "Développeur.euse" and "vendeur(se)".
    euse_pattern = re.compile(
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ]+)eur(?:\((?:euse|se)\)|[.·](?:euse|se))(?![A-Za-zÀ-ÖØ-öø-ÿ])",
        re.IGNORECASE,
    )

    def repl_euse(match: re.Match) -> str:
        root = match.group(1)
        return f"{root}{'eur' if gender == 'man' else 'euse'}"

    value = euse_pattern.sub(repl_euse, value)

    # 3) Handle simple optional ".e" / "(e)" suffixes (e.g., "senior.e", "chargé(e)").
    #    We keep it conservative: "senior" is invariant, so we drop the marker for both.
    # Using a lookahead instead of \b because the match can end with ')', and
    # \b is false between two non-word characters (e.g., ') '), which would miss
    # cases like "Chargé(e)".
    opt_e_pattern = re.compile(
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ]+)(?:\((?:e)\)|[.·]e)(?![A-Za-zÀ-ÖØ-öø-ÿ])"
    )

    def repl_opt_e(match: re.Match) -> str:
        root = match.group(1)
        if root.lower() in {"senior", "sénior", "junior"}:
            return root
        if gender == "woman" and not root.lower().endswith("e"):
            return f"{root}e"
        return root

    return opt_e_pattern.sub(repl_opt_e, value)


_TRAILING_ENCAPS_PATTERN = re.compile(r"(?:\s*[\(\[\{][^\)\]\}]*[\)\]\}]\s*)+$")


def format_job_title(value: str, gender: str = "man") -> str:
    """Format a job title for downstream usage.

    - Normalizes inclusive forms via normalize_inclusive_job_title.
    - Removes trailing encapsulated segments like "(4 mois)", "[remote]", "{contract}".
    """

    base = (value or "").strip()
    title = normalize_inclusive_job_title(base, gender=gender)

    # Some sources prefix the title with program/duration info, e.g.
    # "Stage coopératif - Été 2026: Développeur...".
    # If the left side looks like a stage/coop label, keep only the right side.
    if ":" in title:
        left, right = title.split(":", 1)
        left = left.strip()
        right = right.strip()
        if re.search(
            r"\b(stage|stagiaire|co-?op|coop(?:ératif)?|intern(?:ship)?|été|hiver|automne|printemps|202\d)\b",
            left,
            flags=re.IGNORECASE,
        ):
            title = right or title

    # Some sources provide bilingual titles such as:
    # - "EN | FR" / "FR | EN"
    # - "FR / EN" (with spaces)
    # - "EN \\ FR" (with spaces)
    # In these cases, keep the left-most title to avoid noisy duplicates.
    if "|" in title:
        left = title.split("|", 1)[0].strip()
        title = left or title
    else:
        spaced_sep = re.search(r"\s([/\\])\s", title)
        if spaced_sep:
            sep = spaced_sep.group(1)
            left = title.split(sep, 1)[0].strip()
            title = left or title

    # Remove trailing non-title suffixes after a dash, e.g.
    # "... – 4 mois Stage/Co-op (Été 2026)".
    dash_match = re.search(r"\s[–-]\s(.+)$", title)
    if dash_match:
        right = dash_match.group(1).strip()
        left_part = title[: dash_match.start()].strip()

        # 1) Bilingual titles like "FR - EN": keep left-most.
        # Heuristic: left contains common French markers, right does not.
        if left_part and right:
            fr_markers = re.search(r"\b(d'|de|des|du|la|le|les|en)\b", left_part, flags=re.IGNORECASE)
            fr_markers_right = re.search(r"\b(d'|de|des|du|la|le|les|en)\b", right, flags=re.IGNORECASE)
            if fr_markers and not fr_markers_right and not re.search(r"\d", right):
                title = left_part
            else:
                # 2) Trailing duration/contract info after dash.
                if re.match(r"\d", right) or re.search(
                    r"\b(mois|stage|co-?op|intern(?:ship)?|contrat|contract|cdd|cdi|freelance|temporaire)\b",
                    right,
                    flags=re.IGNORECASE,
                ):
                    title = left_part
    title = _TRAILING_ENCAPS_PATTERN.sub("", title or "").strip()
    return title or "N/A"


def _format_lang_title(value: str) -> str:
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


def format_salary(job) -> str:
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
    location = _na(job.get("location"))

    return {
        "datePublished": _na(job.get("date_posted")),
        "source": "python-jobspy",
        "platform": "Indeed",
        "emails": _join_if_list(job.get("emails"), sep=", "),
        "company": _format_lang_title(job.get("company")),
        "companyDescription": _na(job.get("company_description")),
        "companyUrl": _na(job.get("company_url")),
        "jobTitle": format_job_title(job.get("title"), gender="man"),
        "jobDescription": _na(job.get("description")),
        "jobSalary": format_salary(job),
        "jobUrl": _na(job.get("job_url") or job.get("job_url_direct")),
        "jobType": _join_if_list(job.get("job_type"), sep=", "),
        "jobCity": _city_from_location(location),
        "query": f'query="{query}"; location="{location}"',
    }


def run_one_query(
  search_term: str,
  location: str,
  results_wanted: int,
  distance: int,
  days_old: int,
):
    city_state = ','.join(location.split(',')[:-1]).strip().lower()
    country = location.split(',')[-1].strip().lower()

    jobs = scrape_jobs(
        site_name="indeed",
        search_term=search_term,
        location=city_state,
        country_indeed=country,
        results_wanted=results_wanted,
        hours_old=days_old * 24,
        distance=distance,  # miles
        sort_by="relevance",
    )

    return jobs.to_dict(orient="records")


# ---- n8n Python node entrypoint ----
out = []

for it in _items:
    j = it["json"]
    search_term = str(j["query"])
    location = str(j["location"])
    results_wanted = int(j["results_wanted"])
    distance = int(j["distance"])
    days_old = int(j["days_old"])

    jobs = run_one_query(
        search_term=search_term,
        location=location,
        results_wanted=results_wanted,
        distance=distance,  # miles
        days_old=days_old,
    )
    for job in jobs:
        out.append({"json": _parse(job, search_term)})

return out