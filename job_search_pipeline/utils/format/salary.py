#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

from job_search_pipeline.utils import format as fmt


def transform(
    min_amount: float,
    max_amount: float,
    currency: str,
    interval: str,
) -> str:
    lo = fmt.value.optional_float(min_amount)
    hi = fmt.value.optional_float(max_amount)
    if lo is None and hi is None:
        return "N/A"
    if lo is not None and hi is not None and lo != hi:
        amt = f"{lo:,.0f}-{hi:,.0f}"
    else:
        one = lo if lo is not None else hi
        amt = f"{one:,.0f}"
    # Example output: "CAD 80,000-95,000 / year"
    unit = fmt.value.na(interval, default="")
    suffix = f" / {unit}" if unit not in ("", "N/A") else ""
    cur = fmt.value.na(currency, default="")
    prefix = f"{cur} " if cur not in ("", "N/A") else ""
    return f"{prefix}{amt}{suffix}".strip()
