# Install `direnv`

```bash
curl -sfL https://direnv.net/install.sh | bash
```

# Integrating `direnv` on `MSYS2` / `MinGW64` / `Git Bash`

```bash
# Make direnv executable
chmod +x /mingw64/bin/direnv

# Append the direnv hook to your Git Bash login profile
cat >> ~/.bash_profile <<'EOF'
_direnv_hook() {
  local previous_exit_status=$?;
  eval "$(MSYS_NO_PATHCONV=1 "direnv" export bash | sed 's|export PATH=|export _X_DIRENV_PATH=|g')";
  if [ -n "$_X_DIRENV_PATH" ]; then
    _X_DIRENV_PATH=$(cygpath -p "$_X_DIRENV_PATH")
    export "PATH=$_X_DIRENV_PATH"
    unset _X_DIRENV_PATH
  fi
  return $previous_exit_status;
};


if ! [[ "$PROMPT_COMMAND" =~ _direnv_hook ]]; then
  PROMPT_COMMAND="_direnv_hook;$PROMPT_COMMAND"
fi
EOF

# Load the updated profile in the current shell
source ~/.bash_profile

# Trust this directory so direnv will load its .envrc
direnv allow
```
