#!/usr/bin/env bash
#                       Copyright 2026, Sébastien Kéroack
#                             All rights reserved.
#
#  Unauthorized copying, modification, distribution, or use of this code,
#  via any medium, is strictly prohibited without the express
#  written permission of the author.
# ==============================================================================

# Initialize a git repository if none exists
if [ ! -d '.git' ]; then
  git init --initial-branch=main --shared=umask
  git config core.ignorecase false
  git add .
fi

# Add n8n-io/n8n
setup_submodule \
  "n8n-io/n8n" \
  "https://github.com/n8n-io/n8n.git" \
  "third_party/n8n-io/n8n" \
  "n8n@$N8N_VERSION"

# Add Piggeldi2013/n8n-timeout-patch
setup_submodule \
  "piggeldi2013/n8n-timeout-patch" \
  "https://github.com/Piggeldi2013/n8n-timeout-patch.git" \
  "third_party/piggeldi2013/n8n-timeout-patch" \
  "main"

# Add speedyapply/JobSpy
setup_submodule \
  "speedyapply/jobspy" \
  "https://github.com/speedyapply/JobSpy.git" \
  "third_party/speedyapply/jobspy" \
  "$JOBSPY_COMMIT_HASH"
