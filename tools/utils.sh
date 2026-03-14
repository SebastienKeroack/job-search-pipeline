#!/usr/bin/env bash
#                       Copyright 2026, Sébastien Kéroack
#                             All rights reserved.
#
#  Unauthorized copying, modification, distribution, or use of this code,
#  via any medium, is strictly prohibited without the express
#  written permission of the author.
# ==============================================================================

# Get the location of this script
declare tools_path=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")

# Source all utils.sh scripts in the tools directory and its subdirectories
pushd "$tools_path" >/dev/null

declare -a scripts=()
declare name=$(realpath --relative-to="$tools_path/.." "$PWD")
echo "Loaded: $name/utils.sh"

mapfile -t scripts < <(find "." \
  -maxdepth 2 \
  -name 'utils.sh' \
  -not -path './utils.sh' 2>/dev/null)
for script in "${scripts[@]}"; do
  name=$(realpath --relative-to="$tools_path/.." "$script")
  source "$script"
  if [ $? -ne 0 ]; then
    echo "ERROR: Failed to source: $name"
    exit 1
  else
    echo "Loaded: $name"
  fi
done

popd >/dev/null # "$tools_path"
