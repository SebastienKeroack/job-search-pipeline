#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

import re
from enum import Enum


class CompensationInterval(Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    HOURLY = "hourly"


def transform(*args, **kwargs):
    """Helper function to call extract_salary with the same signature."""
    return extract_salary(*args, **kwargs)


def extract_salary(
    salary_str,
    lower_limit=1000,
    upper_limit=700000,
    hourly_threshold=350,
    monthly_threshold=30000,
    enforce_annual_salary=False,
    currency="USD",
):
    """
    Extracts salary information from a string and returns the salary interval, min and max salary values, and currency.
    (TODO: Needs test cases as the regex is complicated and may not cover all edge cases)
    """
    if not salary_str:
        return None, None, None, None

    # Accept: "$85,000 - $110,000", "$85k–110k", "85 000,00$ à 110 000,00$"
    # Range separators: hyphen/dash variants, and common textual separators.
    RANGE_SEP = r"(?:[-—–]|\bto\b|\bà\b|\ba\b|\bet\b|\band\b)"
    NUMBER = r"(?:\d+(?:[,\s\u00A0]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)"

    patterns = [
        # $ prefixed (original style, but more flexible number parsing)
        re.compile(rf"\$\s*({NUMBER})([kK]?)\s*{RANGE_SEP}\s*(?:\$)?\s*({NUMBER})([kK]?)", re.IGNORECASE),
        # $ suffixed (French/CA style)
        re.compile(rf"({NUMBER})([kK]?)\s*\$\s*{RANGE_SEP}\s*({NUMBER})([kK]?)\s*\$?", re.IGNORECASE),
    ]

    def to_number(s: str) -> float:
        # Normalize spaces (incl NBSP), then handle separators robustly.
        s = s.replace("\u00A0", " ").strip()
        s = re.sub(r"\s+", "", s)

        # Heuristic: decide whether ',' / '.' is decimal or thousand separator.
        def looks_like_thousands_sep(txt: str, sep: str) -> bool:
            parts = txt.split(sep)
            return len(parts) > 1 and all(p.isdigit() for p in parts) and len(parts[-1]) == 3

        if "," in s and "." not in s:
            if looks_like_thousands_sep(s, ","):
                s = s.replace(",", "")
            else:
                s = s.replace(",", ".")  # decimal comma
        elif "." in s and "," not in s:
            if looks_like_thousands_sep(s, "."):
                s = s.replace(".", "")
            # else '.' is decimal dot -> keep it
        else:
            # Both present: assume US-style thousands comma + decimal dot
            s = s.replace(",", "")

        return float(s)

    def convert_hourly_to_annual(hourly_wage):
        return hourly_wage * 2080

    def convert_monthly_to_annual(monthly_wage):
        return monthly_wage * 12

    def infer_interval_from_context(value: float, before: str, after: str) -> str:
        after_l = after.lower()
        if any(k in after_l for k in ["par heure", "heure", "hour", "/h", "/hr"]):
            return CompensationInterval.HOURLY.value
        if any(k in after_l for k in ["par mois", "mois", "month", "/mo", "/m"]):
            return CompensationInterval.MONTHLY.value
        if any(k in after_l for k in ["par an", "année", "annuel", "year", "/an", "/yr"]):
            return CompensationInterval.YEARLY.value

        # Fall back to thresholds.
        if value < hourly_threshold:
            return CompensationInterval.HOURLY.value
        if value < monthly_threshold:
            return CompensationInterval.MONTHLY.value
        return CompensationInterval.YEARLY.value

    # Try extracting salary ranges (may appear multiple times in long descriptions).
    range_candidates = []
    for pat in patterns:
        for m in pat.finditer(salary_str):
            min_salary = to_number(m.group(1))
            max_salary = to_number(m.group(3))

            # Handle 'k' suffix for min and max salaries independently
            if "k" in (m.group(2) or "").lower():
                min_salary *= 1000
            if "k" in (m.group(4) or "").lower():
                max_salary *= 1000

            before = salary_str[max(0, m.start() - 60) : m.start()]
            after = salary_str[m.end() : m.end() + 60]
            before_l = before.lower()
            after_l = after.lower()

            # If the amount is immediately described as a bonus/premium, ignore it.
            near_before = salary_str[max(0, m.start() - 25) : m.start()].lower()
            if any(k in near_before for k in ["prime", "bonus"]):
                continue

            score = 0
            if any(k in before_l for k in ["rémunération", "remuneration"]):
                score += 3
            if any(k in before_l for k in ["salaire", "salary"]):
                score += 2
            if any(k in after_l for k in ["par heure", "heure", "hour", "/h", "/hr"]):
                score += 2
            if any(k in after_l for k in ["par mois", "mois", "month", "/mo", "/m"]):
                score += 1
            if any(k in after_l for k in ["par an", "année", "annuel", "year", "/an", "/yr"]):
                score += 1
            if any(k in before_l for k in ["prime", "bonus"]):
                score -= 2

            # Exclude bonuses/premiums unless they are clearly tied to salary.
            # Example false positives: "Prime de soir : 3$/heure", "Prime ... 5000$".
            if any(k in before_l for k in ["prime", "bonus"]) and not any(
                k in before_l for k in ["rémunération", "remuneration", "salaire", "salary"]
            ):
                continue

            interval = infer_interval_from_context(min_salary, before, after)

            if interval == CompensationInterval.HOURLY.value:
                annual_min_salary = convert_hourly_to_annual(min_salary)
                annual_max_salary = convert_hourly_to_annual(max_salary) if max_salary < hourly_threshold else None
            elif interval == CompensationInterval.MONTHLY.value:
                annual_min_salary = convert_monthly_to_annual(min_salary)
                annual_max_salary = convert_monthly_to_annual(max_salary) if max_salary < monthly_threshold else None
            else:
                annual_min_salary = min_salary
                annual_max_salary = max_salary

            if not annual_max_salary:
                continue

            if (
                lower_limit <= annual_min_salary <= upper_limit
                and lower_limit <= annual_max_salary <= upper_limit
                and annual_min_salary < annual_max_salary
            ):
                range_candidates.append(
                    (score, m.start(), interval, min_salary, max_salary, annual_min_salary, annual_max_salary)
                )

    if not range_candidates:
        # Try extracting a single salary value (common in job descriptions).
        single_patterns = [
            # $ prefixed
            re.compile(rf"\$\s*({NUMBER})([kK]?)", re.IGNORECASE),
            # $ suffixed (French/CA style)
            re.compile(rf"({NUMBER})([kK]?)\s*\$", re.IGNORECASE),
        ]

        # Amounts that are very commonly NOT base salary (benefits/bonuses/perks).
        # We only accept them if a salary keyword is present nearby.
        nonsalary_context = [
            "référencement",
            "referencement",
            "referral",
            "reference",
            "référence",
            "reference",
            "remboursement",
            "allocation",
            "montant alloué",
            "montant alloue",
            "prime",
            "bonus",
        ]

        candidates = []
        for pat in single_patterns:
            for m in pat.finditer(salary_str):
                raw = m.group(1)
                suffix = (m.group(2) or "").lower()
                value = to_number(raw)
                if "k" in suffix:
                    value *= 1000

                before = salary_str[max(0, m.start() - 60) : m.start()]
                after = salary_str[m.end() : m.end() + 60]

                # If the amount is immediately described as a bonus/premium, ignore it.
                near_before = salary_str[max(0, m.start() - 25) : m.start()].lower()
                if any(k in near_before for k in ["prime", "bonus"]):
                    continue

                score = 0
                before_l = before.lower()
                after_l = after.lower()
                has_salary_keyword = any(k in before_l for k in ["rémunération", "remuneration", "salaire", "salary"])
                if has_salary_keyword:
                    score += 3
                has_unit_keyword = any(k in after_l for k in ["par heure", "heure", "hour", "/h", "/hr"])
                if has_unit_keyword:
                    score += 2
                if any(k in after_l for k in ["par mois", "mois", "month", "/mo", "/m"]):
                    score += 1
                if any(k in after_l for k in ["par an", "année", "annuel", "year", "/an", "/yr"]):
                    score += 1
                # De-prioritize bonuses/prime amounts.
                if any(k in before_l for k in ["prime", "bonus"]):
                    score -= 2

                # Exclude bonuses/premiums unless they are clearly tied to salary.
                if any(k in before_l for k in ["prime", "bonus"]) and not any(
                    k in before_l for k in ["rémunération", "remuneration", "salaire", "salary"]
                ):
                    continue

                # If we don't see salary keywords or time-unit context, it's too ambiguous.
                # This avoids false positives like referral bonuses: "jusqu'à 1000$".
                if not has_salary_keyword and not has_unit_keyword:
                    continue

                # Ignore common benefit/referral/bonus contexts unless salary is explicit.
                if not has_salary_keyword and any(k in before_l or k in after_l for k in nonsalary_context):
                    continue

                interval = infer_interval_from_context(value, before, after)
                candidates.append((score, m.start(), interval, value))

        if not candidates:
            return None, None, None, None

        # Pick the best candidate (highest score, then earliest occurrence).
        candidates.sort(key=lambda t: (-t[0], t[1]))
        _score, _pos, interval, value = candidates[0]

        if interval == CompensationInterval.HOURLY.value:
            annual_value = convert_hourly_to_annual(value)
        elif interval == CompensationInterval.MONTHLY.value:
            annual_value = convert_monthly_to_annual(value)
        else:
            annual_value = value

        if not (lower_limit <= annual_value <= upper_limit):
            return None, None, None, None

        if enforce_annual_salary:
            return interval, annual_value, None, currency
        return interval, value, None, currency

    # Pick the best candidate (highest score, then latest occurrence).
    range_candidates.sort(key=lambda t: (-t[0], -t[1]))
    _score, _pos, interval, min_salary, max_salary, annual_min_salary, annual_max_salary = range_candidates[0]

    if enforce_annual_salary:
        return interval, annual_min_salary, annual_max_salary, currency
    return interval, min_salary, max_salary, currency
