#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================


from job_search_pipeline.utils import parse


def transform(title: str, description: str) -> str:
    level = parse.job_level.transform(title, title=True)
    if not level:
        level = parse.job_level.transform(description)
    return level if level else "N/A"
