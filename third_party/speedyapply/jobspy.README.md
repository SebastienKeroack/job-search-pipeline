## Saving Local Changes as a Patch

If you've modified files in `third_party/speedyapply/jobspy/` locally and want to save those changes as a patch file (without committing), use:

```bash
git -C third_party/speedyapply/jobspy diff --output ../jobspy.patch
```

This command:

- **`git -C third_party/speedyapply/jobspy`**: Runs git commands in the `jobspy` subdirectory
- **`diff`**: Compares JobSpy’s working tree against its current `HEAD` commit
- **`--output ../jobspy.patch`**: Writes the diff to `jobspy.patch` (one level up, in the `third_party/` directory)

### Result

A `jobspy.patch` file is created at `${workspaceFolder}/third_party/speedyapply/jobspy.patch` containing all local changes in unified diff format.

### Applying the Patch Later

```bash
git -C third_party/speedyapply/jobspy apply --verbose --ignore-whitespace ../jobspy.patch
```

### Notes

- This captures **uncommitted** changes only.
- Use `git diff HEAD` instead if you want changes since the last commit (including staged changes).
- The patch is useful for version control or sharing modifications without full git history.
