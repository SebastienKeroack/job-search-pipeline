#!/bin/bash
#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

if [ ! -f ".env" ]; then
  echo "Error: .env file not found!"
  echo "Create it by copying .env.example to .env and filling in the required values."
  exit 1
fi
source .env

# A simple test to verify that the Ollama model is running correctly
REPLY=$(curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'$OLLAMA_MODEL'",
    "prompt": "Hey",
    "stream": false
  }')
jq -r .response <<< "$REPLY"
