#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

from job_search_pipeline.query import Query

# ---- n8n Python node entrypoint ----
out = []

for it in _items:
    q = Query.from_dict(**it["json"])
    for job in q.run():
        out.append({"json": job.parse()})

return out
