#!/bin/bash
#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================
# --- Reference:
# see: https://platform.openai.com/docs/api-reference/responses?lang=curl
# see: https://platform.openai.com/docs/guides/text?lang=curl
# see: https://platform.openai.com/docs/guides/migrate-to-responses?lang=bash
# ==============================================================================

if [ ! -f "env.sh" ]; then
  echo "Error: env.sh file not found!"
  echo "Create it by copying env.fake.sh to env.sh and filling in the required values."
  exit 1
fi
source env.sh

# A simple test to verify that the OpenAI model is working correctly
REPLY=$(curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "'$OPENAI_API_MODEL'",
    "reasoning": {"effort": "low"},
    "max_output_tokens": 64,
    "input": "Hey",
    "store": false
  }')
jq -r .output[1].content[0].text <<< "$REPLY"