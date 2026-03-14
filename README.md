# JOB-SEARCH-PIPELINE

Automates job discovery → extraction → scoring → application materials using n8n workflows, Python utilities, and optional LLM prompts via Ollama (local) or OpenAI-compatible APIs.

This repo contains an n8n-based pipeline for job searching and processing (workflows, parsing utilities, prompts, and helper scripts).

**Main folders**

- `candidate/`: resume inputs/templates/prompts used by the pipeline (e.g., as source material for tailoring)
- `ci/`: docker-compose + Dockerfiles
- `job_search_pipeline/`: scraping/parsing utilities
- `workflows/`: n8n workflow exports
- `.env.example`: example environment variables file (copy/adjust values for your local setup)

## Quick start

After n8n is running, import a workflow from this repo’s `workflows/` directory (in n8n: **Workflows** → **Import from File**) to get the pipeline set up.

Initialize the repo environment:

```bash
bash ./setup.sh third_party
```

Build images and start containers:

```bash
# Enable editable mode (optional)
bash ./setup.sh editable

# Build images using docker
bash ./setup.sh docker

# Start containers using docker-compose
docker compose \
  -f "./ci/docker-compose.yaml" \
  up
```

If you want to run a local LLM server (and point n8n to it), start Ollama:

```bash
set -a; source .envrc; set +a

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

Create a candidate archive for upload to Google Drive:

```bash
bash ./export.sh candidate
```

## Kubernetes

Build the n8n task runners image for Kubernetes:

```bash
bash ./setup.sh kubernetes
```

## Before a commit do

```bash
# Test Python
pytest

# Test JavaScript
bun run test

# Bump version in 'version.txt' and then:
python ci/generate_version.py
```

## License

MIT — see `LICENSE`.
