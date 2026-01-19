#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

import base64
import os
import re
import subprocess
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path


def _slugify(value: str) -> str:
    value = (value or "").strip()
    # Convert accented characters to their closest ASCII equivalent (e.g., é->e, ç->c, œ->oe).
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9\-_]+", "", value)
    return value or "unknown"


def _parsify(value: str) -> str:
    value = re.sub(r"^Objet : ", "", value)
    return value


def _render_simple_placeholders(template_html: str, values: dict) -> str:
    rendered = template_html
    for key, val in values.items():
        if val is None:
            val = ""
        val = str(val)
        rendered = rendered.replace(key, val)
    return rendered

# ---- n8n Python node entrypoint ----
chrome_bin = (
    os.environ.get("CHROME_BIN") or
    os.environ.get("CHROMIUM_BIN") or
    "chromium")

out = []

for it in _items:
    j = it.get("json") or {}

    template = Path(j.get("template", "/home/runner/candidate/cover_letter.template.html"))
    if not template.exists():
        raise FileNotFoundError(f"Template not found: {template}")

    # Get first and last name
    full_name = j["candidate"]["name"]
    full_name_parts = full_name.split(" ")
    first_name = full_name_parts[0]
    last_name = full_name_parts[-1]

    company = j["company"]
    job_title = j["job"]
    job_url = j["url"]
    pdf_name = f"{_slugify(full_name)}-{_slugify(company)}-{_slugify(job_title)}.pdf"

    # Placeholder replacement.
    rendered_html = _render_simple_placeholders(
        template.read_text(encoding="utf-8"),
        {
            "__FNAME__": first_name,
            "__LNAME__": last_name,
            "__COMPANY__": company,
            "__JOB_TITLE__": job_title,
            "__LETTER__": _parsify(j["cover_letter"]),
            "__PHONE__": j["candidate"]["phone"],
            "__EMAIL__": j["candidate"]["email"],
            "__DATE__": datetime.now().strftime("%B %d, %Y"),
        },
    )

    with tempfile.TemporaryDirectory(prefix="cover-letter-") as tmp:
        tmp_dir = Path(tmp)
        html_path = tmp_dir / "input.html"
        pdf_path = tmp_dir / "output.pdf"

        html_path.write_text(rendered_html, encoding="utf-8")

        # Use Chromium directly to render the PDF
        cmd = [
            chrome_bin,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--print-to-pdf-no-header",
            f"--print-to-pdf={pdf_path.as_posix()}",
            html_path.as_uri(),
        ]

        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=int(j.get("timeout_seconds") or 50),
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "Chromium failed to render PDF. "
                f"rc={completed.returncode}\n"
                f"stdout={completed.stdout}\n"
                f"stderr={completed.stderr}"
            )

        pdf_bytes = pdf_path.read_bytes()
        pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")

    out.append(
        {
            "json": {
                "template": str(template),
                "pdf_name": pdf_name,
                "job_url": job_url,
            },
            "binary": {
                "data": {
                    "data": pdf_b64,
                    "mimeType": "application/pdf",
                    "fileName": pdf_name,
                }
            },
        }
    )

return out