# JOB-SEARCH-PIPELINE

Automates job discovery → extraction → scoring → application materials using n8n workflows, Python utilities, and optional LLM prompts via Ollama (local) or OpenAI-compatible APIs.

This repo contains an n8n-based pipeline for job searching and processing (workflows, parsing utilities, prompts, and helper scripts).

**Main folders**

- `candidate/`: resume inputs/templates/prompts used by the pipeline (e.g., as source material for tailoring)
- `ci/`: docker-compose + Dockerfiles
- `job_search_pipeline/`: scraping/parsing utilities
- `workflows/`: n8n workflow exports
- `env.fake.sh`: example environment variables file (copy/adjust values for your local setup)

## Quick start

After n8n is running, import a workflow from this repo’s `workflows/` directory (in n8n: **Workflows** → **Import from File**) to get the pipeline set up.

Initialize the repo environment:
```bash
[ -z "${CI_REPO_INITED:-}" ] && source init.sh
```

Build images and start containers:
```bash
# Build a patched n8n Docker image with increased timeout limits
docker build \
  --build-arg BASE_IMAGE=n8nio/n8n:$N8N_VERSION \
  -t n8n-patched:latest \
  -f ci/n8n.Dockerfile .
# Build a n8n runners image with extra packages installed
docker build \
  --build-arg BASE_IMAGE=n8nio/runners:$N8N_VERSION \
  --build-arg PYTHON_VERSION=$PYTHON_VERSION \
  -t n8n-task-runners:latest \
  -f ci/n8n-task-runners.Dockerfile .
# Start n8n and n8n-task-runners containers using docker-compose
docker compose \
  -f ci/docker-compose.yaml \
  up
```

If you want to run a local LLM server (and point n8n to it), start Ollama:
```bash
set -o allexport; source env.sh; set +o allexport

docker run -d \
  --network job-search-pipeline-net \
  --name ollama \
  -p 11434:11434 \
  -e OLLAMA_MAX_LOADED_MODELS=$OLLAMA_MAX_LOADED_MODELS \
  -e OLLAMA_CONTEXT_LENGTH=$OLLAMA_CONTEXT_LENGTH \
  -e OLLAMA_KEEP_ALIVE=$OLLAMA_KEEP_ALIVE \
  -e OLLAMA_LOAD_TIMEOUT=$OLLAMA_LOAD_TIMEOUT \
  -e OLLAMA_NOHISTORY=$OLLAMA_NOHISTORY \
  -v "$OLLAMA_HOME:/root/.ollama" \
  ollama/ollama:$OLLAMA_VERSION

docker exec -it ollama ollama run $OLLAMA_MODEL ""
```

See more informations by running:
```bash
set -o allexport; source env.sh; set +o allexport

bash info.sh
```

## License

MIT — see `LICENSE`.
