#!/bin/bash
#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

# Check for required files
missing=0
for file in "env.sh" "resume/content.md" "resume/location.txt" "resume/query.txt"; do
  if [ ! -f "$file" ]; then
    ext="${file##*.}"
    file_name="${file%.*}"
    echo "Error: $file file not found!"
    echo "Create it by copying:"
    echo "  cp ${file_name}.fake.${ext} $file"
    echo "Then edit $file to add the required information."
    echo
    missing=1
  fi
done
[ "$missing" -eq 1 ] && exit 1

jq_update_by_id() {
  local file=$1;
  local uuid=$2
  local value_file=$3
  jq \
    --arg ID "$uuid" \
    --arg NEW_VALUE "$value_file" \
    '(.nodes[].parameters?.assignments?.assignments | select(. != null)[] | select(.id == $ID)).value = ($NEW_VALUE | fromjson)' \
    "$file" > tmp.$$.json && mv tmp.$$.json "$file"
}

for workflow in "developer" "general"; do
  # Update candidate resume in workflow
  jq_update_by_id \
    "workflows/job-listings_llm-${workflow}.json" \
    "c0847ad4-c633-4426-a36b-48e6b0865886" \
    "$(cat resume/content.md | jq -Rs .)"

  # Update job search query in workflow
  jq_update_by_id \
    "workflows/job-listings-${workflow}.json" \
    "17e26303-b893-4328-8777-a1b268c726aa" \
    "$(cat resume/query.txt | jq -Rs .)"

  # Update job search location in workflow
  jq_update_by_id \
    "workflows/job-listings-${workflow}.json" \
    "8d2ab468-0eef-42d8-938b-daafb691de33" \
    "$(cat resume/location.txt | jq -Rs .)"
done