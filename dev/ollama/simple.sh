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

# A simple test to verify that the Ollama model is running correctly
REPLY=$(curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'$OLLAMA_MODEL'",
    "prompt": "Hey",
    "stream": false
  }')
jq -r .response <<< "$REPLY"