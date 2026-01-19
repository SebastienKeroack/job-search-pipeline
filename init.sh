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
set -o allexport; source env.sh; set +o allexport
set -eu

# Detect whether we're inside a Python virtual environment (venv/virtualenv/conda).
in_python_venv() {
  # Common indicators
  if [ -n "${VIRTUAL_ENV:-}" ] || [ -n "${CONDA_PREFIX:-}" ]; then
    return 0
  fi

  # Fallback: compare sys.prefix vs sys.base_prefix (works for venv)
  local py=""
  py="$(command -v python3 || true)"
  if [ -z "$py" ]; then py="$(command -v python || true)"; fi
  if [ -z "$py" ]; then
    return 1
  fi

  "$py" - <<'PY' >/dev/null 2>&1
import sys
base = getattr(sys, "base_prefix", sys.prefix)
real = getattr(sys, "real_prefix", None)  # virtualenv
raise SystemExit(0 if (sys.prefix != base or real is not None) else 1)
PY
}

# Ensure candidate/exists.sh passes
if ! candidate/exists.sh; then
  echo "Please create the missing files and re-run init.sh." >&2
  exit 1
fi

# Initialize a git repository if none exists
if [ ! -d '.git' ]; then
  git init --initial-branch=main --shared=umask
  git config core.ignorecase false
  git add .
fi

# Create directory to persist n8n data
if [ ! -d "$N8N_HOME" ]; then
  if [ "${MSYSTEM:-}" = "MINGW64" ]; then
    mkdir -p "$N8N_HOME"
  else
    install -d -m 770 -o $(whoami) -g $(whoami) "$N8N_HOME"
  fi
fi

# Create directory to persist ollama data
if [ ! -d "$OLLAMA_HOME" ]; then
  if [ "${MSYSTEM:-}" = "MINGW64" ]; then
    mkdir -p "$OLLAMA_HOME"
  else
    install -d -m 770 -o $(whoami) -g $(whoami) "$OLLAMA_HOME"
  fi
fi

# Add n8n-timeout-patch
if [ ! -d 'third_party/n8n-timeout-patch' ]; then
  git submodule add -f \
    --name Piggeldi2013/n8n-timeout-patch \
    https://github.com/Piggeldi2013/n8n-timeout-patch.git \
    third_party/n8n-timeout-patch
  git config -f .gitmodules \
    submodule.Piggeldi2013/n8n-timeout-patch.ignore dirty
else
  git submodule update --init --recursive third_party/n8n-timeout-patch
fi

# Copy the patch file to the n8n home directory for Docker volume mounting
cp third_party/n8n-timeout-patch/patch-http-timeouts.js \
  "$N8N_HOME/patch-http-timeouts.js"

# Add JobSpy
if [ ! -d "third_party/JobSpy" ]; then
  git submodule add -f \
    --name speedyapply/JobSpy \
    https://github.com/speedyapply/JobSpy.git \
    third_party/JobSpy
  git config -f .gitmodules \
    submodule.speedyapply/JobSpy.ignore dirty
else
  git submodule update --init --recursive third_party/JobSpy
fi

# Checkout pinned commit, patch, and install JobSpy
pushd third_party/JobSpy
# Pinned commit to ensure compatibility with current codebase
git fetch --tags
git checkout $JOBSPY_COMMIT_HASH

# Patch JobSpy
if git apply --check ../JobSpy.patch 2> /dev/null; then
  # third_party/JobSpy/jobspy/__init__.py b/jobspy/__init__.py
  # third_party/JobSpy/jobspy/util.py b/jobspy/util.py
  git apply --verbose --ignore-whitespace ../JobSpy.patch
fi

# Install JobSpy in editable mode (only when running inside a virtual environment)
if in_python_venv; then
  python -m pip install -e .
else
  echo "Skipping 'pip install -e third_party/JobSpy'" >&2
fi
popd

# Add n8n
if [ ! -d "third_party/n8n" ]; then
  git submodule add -f \
    --name n8n-io/n8n \
    https://github.com/n8n-io/n8n.git \
    third_party/n8n
  git config -f .gitmodules \
    submodule.n8n-io/n8n.ignore dirty
else
  git submodule update --init --recursive third_party/n8n
fi

# Checkout pinned commit, and patch n8n
pushd third_party/n8n
git fetch --tags
git checkout n8n@$N8N_VERSION

# Patch n8n
sed -i -E "s#^([[:space:]]*requires-python[[:space:]]*=[[:space:]]*)\".*\"#\1\">=${PYTHON_VERSION}\"#" \
  packages/@n8n/task-runner-python/pyproject.toml
echo "${PYTHON_VERSION}" > \
  packages/@n8n/task-runner-python/.python-version
popd

# Generate env.sh if it does not exist
if [ ! -f "env.sh" ]; then
  cp env.fake.sh \
     env.sh
fi

# Generate docker-compose.yaml if it does not exist
if [ ! -f "ci/docker-compose.yaml" ]; then
  N8N_RUNNERS_AUTH_TOKEN=$(openssl rand -hex 32) \
  envsubst < ci/docker-compose.template.yaml \
           > ci/docker-compose.yaml
fi

# Generate environment.yaml if it does not exist
if [ ! -f "ci/environment.yaml" ]; then
  envsubst < ci/environment.template.yaml \
           > ci/environment.yaml
fi

# Install job-search-pipeline in editable mode
if in_python_venv; then
  python -m pip install -e .
else
  echo "Skipping 'pip install -e .' (no virtual environment detected)." >&2
fi

# Indicate that initialization has been completed
set -o allexport; export CI_REPO_INITED=true; set +o allexport
