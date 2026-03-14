#!/usr/bin/env bash
#                       Copyright 2026, Sébastien Kéroack
#                             All rights reserved.
#
#  Unauthorized copying, modification, distribution, or use of this code,
#  via any medium, is strictly prohibited without the express
#  written permission of the author.
# ==============================================================================

function setup_submodule() {
  pushd "$PROJECT_ROOT" >/dev/null
  local sm_name="${1:?submodule name is required}"   # ex: NVIDIA/gpu-operator
  local sm_url="${2:?submodule url is required}"     # ex: https://github.com/NVIDIA/gpu-operator.git
  local sm_path="${3:?submodule path is required}"   # ex: third_party/gpu-operator
  local sm_ref="${4:-}"                              # ex: v25.3.0 (optional)
  local sm_jobs="${GIT_SUBMODULE_JOBS:-8}"

  # Register submodule if missing, otherwise ensure URL is correct.
  if ! git config -f .gitmodules --get "submodule.${sm_name}.path" >/dev/null 2>&1; then
    git submodule add --force --name "$sm_name" --depth 1 "$sm_url" "$sm_path"
  else
    git submodule set-url "$sm_path" "$sm_url"
  fi

  # Keep local edits ignored; prefer shallow behavior.
  git config -f .gitmodules "submodule.${sm_name}.ignore" dirty
  git config -f .gitmodules "submodule.${sm_name}.shallow" true

  # Sync + fast update (non-recursive).
  git -c submodule.recurse=false submodule sync -- "$sm_path"
  git -c protocol.version=2 -c submodule.recurse=false submodule update --init \
    --depth 1 --jobs "$sm_jobs" --filter=blob:none -- "$sm_path"

  # Optional ref pinning (tag/branch/sha).
  if [[ -n "$sm_ref" ]]; then
    git -C "$sm_path" -c submodule.recurse=false fetch --depth 1 --filter=blob:none origin "$sm_ref" || \
    git -C "$sm_path" -c submodule.recurse=false fetch --depth 1 --filter=blob:none origin "refs/tags/$sm_ref:refs/tags/$sm_ref"
    git -C "$sm_path" checkout --detach FETCH_HEAD
  fi

  # Check if a patch is present for this submodule and apply it if so.
  local sm_patch="$sm_path.patch"
  if [[ -f "$sm_patch" ]]; then
    echo "Applying patch for submodule $sm_name from $sm_patch"
    git -C "$sm_path" apply --whitespace=fix -- "$PROJECT_ROOT/$sm_patch"
  fi
  popd >/dev/null # $PROJECT_ROOT
}
