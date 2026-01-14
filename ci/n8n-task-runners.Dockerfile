ARG BASE_IMAGE=n8nio/runners:2.3.5
ARG NODE_VERSION=22.21.1
ARG PYTHON_VERSION=3.12

# ==============================================================================
# STAGE 1: Base image with JS task runner
# ==============================================================================
FROM ${BASE_IMAGE} AS n8n-runners

# ==============================================================================
# STAGE 2: Python runner build (@n8n/task-runner-python) with uv
# Produces a relocatable venv tied to the python version used
# ==============================================================================
FROM python:${PYTHON_VERSION}-slim-bookworm AS python-runner-builder
ARG TARGETPLATFORM
ARG UV_VERSION=0.8.14

RUN set -e; \
  case "$TARGETPLATFORM" in \
    "linux/amd64") UV_ARCH="x86_64-unknown-linux-gnu" ;; \
    "linux/arm64") UV_ARCH="aarch64-unknown-linux-gnu" ;; \
    *) echo "Unsupported platform: $TARGETPLATFORM" >&2; exit 1 ;; \
  esac; \
  apt-get update; \
  apt-get install -y --no-install-recommends ca-certificates wget; \
  rm -rf /var/lib/apt/lists/*; \
  mkdir -p /tmp/uv && cd /tmp/uv; \
  wget -q "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-${UV_ARCH}.tar.gz"; \
  wget -q "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-${UV_ARCH}.tar.gz.sha256"; \
  sha256sum -c "uv-${UV_ARCH}.tar.gz.sha256"; \
  tar -xzf "uv-${UV_ARCH}.tar.gz"; \
  install -m 0755 "uv-${UV_ARCH}/uv" /usr/local/bin/uv; \
  cd / && rm -rf /tmp/uv

WORKDIR /app/task-runner-python

COPY third_party/n8n/packages/@n8n/task-runner-python/pyproject.toml \
     third_party/n8n/packages/@n8n/task-runner-python/.python-version** \
     ./
RUN uv venv
RUN uv sync \
    --no-editable \
    --no-install-project \
    --no-dev \
    --all-extras

COPY third_party/n8n/packages/@n8n/task-runner-python/ ./
RUN uv sync \
    --no-dev \
    --all-extras \
    --no-editable

WORKDIR /home/runner

# ==============================================================================
# STAGE 3: Task Runner Launcher download
# ==============================================================================
FROM alpine:3.22.1 AS launcher-downloader
ARG TARGETPLATFORM
ARG LAUNCHER_VERSION=1.4.2

RUN set -e; \
    case "$TARGETPLATFORM" in \
        "linux/amd64") ARCH_NAME="amd64" ;; \
        "linux/arm64") ARCH_NAME="arm64" ;; \
        *) echo "Unsupported platform: $TARGETPLATFORM" && exit 1 ;; \
    esac; \
    mkdir /launcher-temp && cd /launcher-temp; \
    wget -q "https://github.com/n8n-io/task-runner-launcher/releases/download/${LAUNCHER_VERSION}/task-runner-launcher-${LAUNCHER_VERSION}-linux-${ARCH_NAME}.tar.gz"; \
    wget -q "https://github.com/n8n-io/task-runner-launcher/releases/download/${LAUNCHER_VERSION}/task-runner-launcher-${LAUNCHER_VERSION}-linux-${ARCH_NAME}.tar.gz.sha256"; \
    echo "$(cat task-runner-launcher-${LAUNCHER_VERSION}-linux-${ARCH_NAME}.tar.gz.sha256) task-runner-launcher-${LAUNCHER_VERSION}-linux-${ARCH_NAME}.tar.gz" > checksum.sha256; \
    sha256sum -c checksum.sha256; \
    mkdir -p /launcher-bin; \
    tar xzf task-runner-launcher-${LAUNCHER_VERSION}-linux-${ARCH_NAME}.tar.gz -C /launcher-bin; \
    cd / && rm -rf /launcher-temp

# ==============================================================================
# STAGE 4: Node alpine base for JS task runner
# ==============================================================================
FROM node:${NODE_VERSION}-bookworm-slim AS node-debian

# ==============================================================================
# STAGE 5: Runtime
# ==============================================================================
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime
ARG N8N_VERSION=snapshot
ARG N8N_RELEASE_TYPE=dev

ENV NODE_ENV=production \
    N8N_RELEASE_TYPE=${N8N_RELEASE_TYPE} \
    SHELL=/bin/sh

COPY --from=python-runner-builder /usr/local/bin/uv /usr/local/bin/uv
COPY --from=node-debian /usr/local/bin/node /usr/local/bin/node
COPY --from=node-debian /usr/local/lib/node_modules/corepack /usr/local/lib/node_modules/corepack

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
      tini \
      libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s ../lib/node_modules/corepack/dist/corepack.js /usr/local/bin/corepack && \
    ln -s ../lib/node_modules/corepack/dist/pnpm.js /usr/local/bin/pnpm

RUN groupadd -g 1000 runner \
 && useradd  -u 1000 -g runner -m -d /home/runner runner

WORKDIR /home/runner

COPY --from=n8n-runners --chown=root:root /opt/runners/task-runner-javascript /opt/runners/task-runner-javascript
COPY --from=python-runner-builder --chown=root:root /app/task-runner-python /opt/runners/task-runner-python
COPY --from=launcher-downloader /launcher-bin/* /usr/local/bin/
COPY --chown=root:root ci/n8n-task-runners.json /etc/n8n-task-runners.json
COPY --chown=root:root third_party/JobSpy /opt/third_party/JobSpy

RUN cd /opt/runners/task-runner-javascript \
    && pnpm add moment uuid
RUN cd /opt/runners/task-runner-python \
    && uv pip install --no-cache-dir -U \
        pandas>=2.3.3 \
        numpy>=2.4.0 \
        beautifulsoup4>=4.14.3 \
        markdownify>=0.13.1 \
        python-dateutil>=2.9.0.post0 \
        pytz>=2025.2 \
        regex>=2024.11.6 \
        six>=1.17.0 \
        soupsieve>=2.8.1 \
        tls-client>=1.0.1 \
        tzdata>=2025.3 \
        pydantic>=2.12.5 \
        pydantic_core \
        typing_extensions \
        typing-inspection \
        requests \
        charset-normalizer \
        idna \
        urllib3 \
        certifi
RUN cd /opt/runners/task-runner-python \
    && uv pip install -e /opt/third_party/JobSpy

USER runner

EXPOSE 5680/tcp
ENTRYPOINT ["tini", "--", "/usr/local/bin/task-runner-launcher"]
CMD ["javascript", "python"]
