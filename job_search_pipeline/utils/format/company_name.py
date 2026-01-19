#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

def transform(value: str) -> str:
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
