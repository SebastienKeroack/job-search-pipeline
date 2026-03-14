ARG BASE_IMAGE=n8nio/n8n:2.11.4
FROM ${BASE_IMAGE} AS base
USER root
COPY --chown=node:node \
  third_party/piggeldi2013/n8n-timeout-patch/patch-http-timeouts.js \
  /home/node/.n8n/patch-http-timeouts.js
RUN mkdir -p /opt/extra \
  && npm --prefix /opt/extra install undici@5 \
  && chown -R node:node /opt/extra
USER node
