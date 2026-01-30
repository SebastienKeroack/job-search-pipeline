## Saving Local Changes as a Patch

If you've modified files in `third_party/JobSpy/` locally and want to save those changes as a patch file (without committing), use:

```bash
git -C third_party/JobSpy diff --output ../JobSpy.patch
```

This command:
- **`git -C third_party/JobSpy`**: Runs git commands in the `JobSpy` subdirectory
- **`diff`**: Compares JobSpy’s working tree against its current `HEAD` commit
- **`--output ../JobSpy.patch`**: Writes the diff to `JobSpy.patch` (one level up, in the `third_party/` directory)

### Result
A `JobSpy.patch` file is created at `${workspaceFolder}/third_party/JobSpy.patch` containing all local changes in unified diff format.

### Applying the Patch Later
```bash
git -C third_party/JobSpy apply --verbose --ignore-whitespace ../JobSpy.patch
```

### Notes
- This captures **uncommitted** changes only.
- Use `git diff HEAD` instead if you want changes since the last commit (including staged changes).
- The patch is useful for version control or sharing modifications without full git history.
