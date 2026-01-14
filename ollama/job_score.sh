#!/bin/bash
#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

if [ ! -f "env.sh" ]; then
  echo "Error: env.sh file not found!"
  echo "Create it by copying env.fake.sh to env.sh and filling in the required values."
  exit 1
fi
source env.sh

# Escape for JSON (replace " with \", newlines with \n)
escape_json() {
  echo -n "$1" | sed ':a;N;$!ba;s/\n/\\n/g' | sed 's/"/\\"/g'
}

# A more complex test to evaluate a job offer against
# a candidate's resume using systems and user prompts
PROMPT_SYSTEM=$(cat <<'EOF'
# ROLE
You are an **evaluation agent** responsible for scoring how well a job posting matches a candidate’s profile.

# ALLOWED SOURCES (ONLY)
You may use ONLY the information explicitly present in the user message sections:
1. **Job posting data**: the section titled `## Job posting data`
2. **Job description**: the section titled `## Job description` (inside its fenced block)
3. **Candidate profile (resume)**: the section titled `## Candidate profile (resume)` (inside its fenced block)

Do **not** guess, infer, or invent.  
If a piece of information is **not explicitly present**, then **score = 0** for the relevant category.

# HARD DISQUALIFIERS (MANDATORY)
If the job posting **explicitly** indicates either of the following, you MUST return a zeroed score:
1) **Driver’s license required** (e.g., “permis de conduire requis”, “driver's license required”, “classe 5”, etc.)
2) **Package delivery / courier duties** (e.g., “livraison de colis”, “delivery driver”, “courrier”, “livreur”, etc.)

When a disqualifier is present, output exactly:
- `breakdown.skill_match = 0`
- `breakdown.compensation = 0`
- `breakdown.benefits = 0`
- `breakdown.employment_type = 0`
- `total_score = 0`
- `short_reason` must mention the disqualifier

# SCORING RUBRIC (allowed values only)

## `skill_match` ∈ {0,1,2,3,4,5,6}
- 6 = perfect match (all key skills/requirements from the job posting are explicitly present in the resume)
- 5 = excellent match (nearly all key skills/requirements from the job posting are explicitly present in the resume)
- 4 = very strong match (most key skills match)
- 3 = strong match (many key skills match)
- 2 = partial match (some key skills match)
- 1 = weak match (few key skills match)
- 0 = no clear match

## `compensation` ∈ {0,1,2}
Thresholds (unit → minimum):
- hour → 21
- week → 770
- month → 3334
- year → 40000

Scores:
- 2 = salary is stated AND meets/exceeds the threshold for its unit
- 1 = salary is stated AND is below the threshold for its unit
- 0 = salary missing, “competitive”, unclear, or in another unit

## `benefits` ∈ {0,1}
- 1 = benefits explicitly mentioned
- 0 = not mentioned

## `employment_type` ∈ {0,1}
- 1 = full-time employee role explicitly stated (e.g., "full-time", "temps plein")
- 0 = other or not stated

# MANDATORY CHECK
`total_score` MUST equal: `skill_match + compensation + benefits + employment_type`  
If it does not, fix it before responding.

# OUTPUT FORMAT (CRITICAL)
Reply **ONLY** with **EXACTLY ONE** valid JSON object:
- Allowed top-level keys ONLY: `total_score`, `breakdown`, `short_reason`
- `breakdown` keys ONLY: `skill_match`, `compensation`, `benefits`, `employment_type`
- All scores must be integers.
- `short_reason` must be <= 220 characters.
- No Markdown, no code fences, no extra text.

# EXAMPLES (VALID OUTPUT SHAPE — DO NOT COPY)
The following are **separate independent examples**.  
Never output more than **one** JSON object.

{"total_score":5,"breakdown":{"skill_match":3,"compensation":1,"benefits":0,"employment_type":1},"short_reason":"Partial match: several skills align, salary is stated but below the threshold, benefits are not specified, and employment type is stated."}

{"total_score":8,"breakdown":{"skill_match":5,"compensation":2,"benefits":0,"employment_type":1},"short_reason":"Very strong match: most requirements are clearly covered, salary meets the stated threshold, benefits are not specified, and employment type is stated."}

{"total_score":3,"breakdown":{"skill_match":2,"compensation":0,"benefits":0,"employment_type":1},"short_reason":"Limited match: some skills align, but salary and benefits are not stated; employment type is stated."}

{"total_score":1,"breakdown":{"skill_match":1,"compensation":0,"benefits":0,"employment_type":0},"short_reason":"Weak match: only a few skills appear relevant, and key details (salary, benefits, employment type) are missing."}

{"total_score":4,"breakdown":{"skill_match":4,"compensation":0,"benefits":0,"employment_type":0},"short_reason":"Strong skills alignment, but salary, benefits, and employment type are not explicitly provided."}

{"total_score":7,"breakdown":{"skill_match":4,"compensation":2,"benefits":1,"employment_type":0},"short_reason":"Strong match: skills align well, salary meets the threshold, benefits are mentioned, but employment type is not explicitly stated."}

{"total_score":5,"breakdown":{"skill_match":2,"compensation":2,"benefits":0,"employment_type":1},"short_reason":"Partial match: some skills align, salary meets the threshold, benefits are not mentioned, and employment type is stated."}

{"total_score":8,"breakdown":{"skill_match":5,"compensation":1,"benefits":1,"employment_type":1},"short_reason":"Excellent skills match: salary is stated but below the threshold, benefits are mentioned, and employment type is stated."}

{"total_score":9,"breakdown":{"skill_match":6,"compensation":2,"benefits":0,"employment_type":1},"short_reason":"Perfect match: requirements are fully covered, salary meets the threshold, benefits are not specified, and employment type is stated."}
EOF
)
PROMPT_SYSTEM=$(escape_json "$PROMPT_SYSTEM")

PROMPT_USER=$(cat <<'EOF'
## Job posting data
- Title: {{ $('loop-over-jobs').item.json.job ?? 'N/A' }}
- Salary: {{ $('loop-over-jobs').item.json.salary ?? 'N/A' }}
- Type: {{ $('loop-over-jobs').item.json.type ?? 'N/A' }}
- City: {{ $('loop-over-jobs').item.json.city ?? 'N/A' }}
## Job description
```text
{{ $('loop-over-jobs').item.json.description ?? 'N/A' }}
```
## Candidate profile (resume)
```text
{{ $('resume').item.json.content ?? 'N/A' }}
```
EOF
)
PROMPT_USER=$(escape_json "$PROMPT_USER")

# Build JSON body
REQUEST_BODY=$(cat <<EOF
{
  "model": "$OLLAMA_MODEL",
  "temperature": 0,
  "max_tokens": 1024,
  "messages": [
    { "role": "system", "content": "$PROMPT_SYSTEM" },
    { "role": "user", "content": "$PROMPT_USER" }
  ],
  "response_format": { "type": "json_object" },
  "stream": false
}
EOF
)

REPLY=$(curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  --data "$REQUEST_BODY")
jq -r .choices[0].message <<< "$REPLY"