#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

import re


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
    # Handles both 'Développeuse.eur' and 'Développeur.euse' (with or without dot)
    inclusive_eur_euse_pattern = re.compile(
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ]+)euse[.·]?eur\b|\b([A-Za-zÀ-ÖØ-öø-ÿ]+)eur[.·]?euse\b",
        re.IGNORECASE,
    )
    def inclusive_eur_euse_dispatch(match: re.Match) -> str:
        # Only one of group(1) or group(2) will be set
        root = match.group(1) or match.group(2)
        return f"{root}{'eur' if gender == 'man' else 'euse'}"
    value = inclusive_eur_euse_pattern.sub(inclusive_eur_euse_dispatch, value)
    gender = (gender or "").strip().lower()
    if gender not in {"man", "woman"}:
        raise NotImplementedError("Only 'man' and 'woman' genders are supported.")

    # 1) Handle paired forms like "Développeuse/Développeur".
    pair_pattern = re.compile(
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ]+)(eur|euse)\s*/\s*\1(eur|euse)\b",
        re.IGNORECASE,
    )

    # Also handle "X ou Y" forms like "Développeuse ou Développeur".
    ou_pattern = re.compile(
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ]+)(eur|euse)\s+ou\s+\1(eur|euse)\b",
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
    value = ou_pattern.sub(repl_pair, value)

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
    #    For "sénior.e", "junior.e", allow "séniore"/"juniore" for women.
    opt_e_pattern = re.compile(
        r"\b([A-Za-zÀ-ÖØ-öø-ÿ]+)(?:\((?:e)\)|[.·]e)(?![A-Za-zÀ-ÖØ-öø-ÿ])"
    )
    def repl_opt_e(match: re.Match) -> str:
        root = match.group(1)
        if root.lower() in {"senior", "sénior", "junior"}:
            if gender == "woman" and not root.lower().endswith("e"):
                return f"{root}e"
            return root
        if gender == "woman" and not root.lower().endswith("e"):
            return f"{root}e"
        return root
    return opt_e_pattern.sub(repl_opt_e, value)


_TRAILING_ENCAPS_PATTERN = re.compile(r"(?:\s*[\(\[\{][^\)\]\}]*[\)\]\}]\s*)+$")


def transform(value: str, gender: str = "man") -> str:
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
                else:
                    # If the right side contains technical details (e.g., 'Vue.js',
                    # parentheses like '(Vue 3)', or dot-separated tokens), prefer
                    # the left part which is likely the canonical French title.
                    if re.search(r"[.\(\)]", right) or re.search(r"[A-Za-z]{2,}\.[A-Za-z]{1,}", right):
                        title = left_part
    title = _TRAILING_ENCAPS_PATTERN.sub("", title or "").strip()
    return title or "N/A"
