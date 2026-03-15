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

# Generate .env if it does not exist
if [ ! -f ".env" ]; then
  cp .env.example \
     .env
  source .env
fi

# Ensure candidate/exists.sh passes
bash "$PROJECT_ROOT/candidate/exists.sh"
if [ $? -ne 0 ]; then
  echo "Please create the missing files and re-run setup.sh." >&2
  exit 1
fi

ACTION="${1:-help}"
case "$ACTION" in
  third_party)
    # Run third-party setup script to initialize submodules and install dependencies
    bash "$PROJECT_ROOT/third_party/setup.sh"

    # Patch n8n
    sed -i -E "s#^([[:space:]]*requires-python[[:space:]]*=[[:space:]]*)\".*\"#\1\">=${PYTHON_VERSION}\"#" \
      "$PROJECT_ROOT/third_party/n8n-io/n8n/packages/@n8n/task-runner-python/pyproject.toml"
    echo "${PYTHON_VERSION}" > \
      "$PROJECT_ROOT/third_party/n8n-io/n8n/packages/@n8n/task-runner-python/.python-version"
    ;;
  editable)
    if in_python_venv; then
      # Install JobSpy in editable mode (only when running inside a virtual environment)
      uv pip install -e "$PROJECT_ROOT/third_party/speedyapply/jobspy"
      # Install job-search-pipeline in editable mode
      uv pip install -e "$PROJECT_ROOT"
    else
      echo "Not in a Python virtual environment. Skipping editable installation"
    fi
    ;;
  docker)
    # Create directory to persist n8n data
    mkdir -p "$N8N_HOME"

    # Create directory to persist ollama data
    mkdir -p "$OLLAMA_HOME"

    # Copy the patch file to the n8n home directory for Docker volume mounting
    cp "$PROJECT_ROOT/third_party/piggeldi2013/n8n-timeout-patch/patch-http-timeouts.js" \
       "$N8N_HOME/patch-http-timeouts.js"

    # Generate docker-compose.yaml
    N8N_RUNNERS_AUTH_TOKEN=$(openssl rand -hex 32) \
    envsubst < "$PROJECT_ROOT/ci/docker-compose.yaml" \
             > "$PROJECT_ROOT/build/docker-compose.yaml"

    # Build a patched n8n Docker image with increased timeout limits
    docker build \
      --build-arg BASE_IMAGE=n8nio/n8n:$N8N_VERSION \
      -t "n8n-patched:$N8N_VERSION" \
      -f "$PROJECT_ROOT/ci/n8n.Dockerfile" \
      "$PROJECT_ROOT"

    # Build a n8n runners image with extra packages installed
    docker build \
      --build-arg BASE_IMAGE=n8nio/runners:$N8N_VERSION \
      --build-arg PYTHON_VERSION=$PYTHON_VERSION \
      -t "n8n-task-runners:$N8N_VERSION" \
      -f "$PROJECT_ROOT/ci/n8n-task-runners.Dockerfile" \
      "$PROJECT_ROOT"

    echo
    echo "Docker images built. You can now run 'docker-compose -f build/docker-compose.yaml up' to start the services."
    ;;
  kubernetes)
    # Build a n8n runners image with extra packages installed
    nerdctl -n=k8s.io build \
      --platform "$ARCH" \
      --build-arg BASE_IMAGE=n8nio/runners:$N8N_VERSION \
      --build-arg PYTHON_VERSION=$PYTHON_VERSION \
      -t "n8n-task-runners:$N8N_VERSION" \
      -f "$PROJECT_ROOT/ci/n8n-task-runners.Dockerfile" \
      "$PROJECT_ROOT"
    ;;
  *)
    echo "job-search-pipeline setup script"
    echo ""
    echo "Usage: $0 <action>"
    echo ""
    echo "Actions:"
    echo "  third_party  - Initialize submodules and install third-party dependencies"
    echo "  docker       - Build Docker images"
    echo "  kubernetes   - Build Kubernetes image"
    ;;
esac
