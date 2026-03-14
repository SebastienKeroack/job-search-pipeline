#!/bin/bash
#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

# Shell options:
# -e: abort script if one command fails
# -u: error if undefined variable used
# -x: log all commands
# -o pipefail: entire command fails if pipe fails. watch out for yes | ...
# -o history: record shell history
# -o allexport: export all functions and variables to be available to subscripts
set -a; source .envrc; set +a
set -eu

# Generate .env if it does not exist
if [ ! -f ".env" ]; then
  cp .env.example \
     .env
  source .env
fi

# Ensure candidate/exists.sh passes
if ! "$PROJECT_ROOT/candidate/exists.sh"; then
  echo "Please create the missing files and re-run export.sh." >&2
  exit 1
fi

ACTION="${1:-help}"

case "$ACTION" in
  candidate)
    # Package candidate/ directory into a zip file for distribution
    if command -v 7z >/dev/null 2>&1; then
      pushd "$PROJECT_ROOT/candidate" >/dev/null
      7z a "$PROJECT_ROOT/build/candidate.zip" \
        "llm/application_email/prompt/system.md" \
        "llm/application_letter/prompt/system.md" \
        "llm/compatibility_score/prompt/system.md" \
        "llm/job_level/prompt/system.md" \
        "resume.md" \
        "search.json" \
        "candidate.json" \
        "application_letter.html" \
        "avatar.jpeg"
      popd >/dev/null # $PROJECT_ROOT/candidate
    else
      echo "Error: '7z' command is not available to create the candidate.zip file."
      exit 1
    fi
    ;;
  *)
    echo "job-search-pipeline export script"
    echo ""
    echo "Usage: $0 <action>"
    echo ""
    echo "Actions:"
    echo "  candidate - Export candidate files to a zip file for distribution"
    ;;
esac
