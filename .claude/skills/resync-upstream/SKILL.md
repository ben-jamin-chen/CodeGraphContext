---
name: resync-upstream
description: Sync this CodeGraphContext checkout with upstream `CodeGraphContext/CodeGraphContext` and replay our local performance patches on top. Use when the user says "resync CGC", "pull upstream", "sync the watcher fork", or asks whether we're behind upstream. Also handles restarting `cgc-watch.service` so the running watcher picks up new code.
---

# Resync this checkout with upstream CodeGraphContext

## When to invoke

The user asks any of:
- "Resync CGC / CodeGraphContext / the watcher"
- "Are we behind upstream?"
- "Pull the latest into our branch"
- "Did we make our own fork or branch?"
- After a long break, "what's our local state vs. upstream?"

## Repo facts you should know before doing anything

- Remote layout (conventional fork workflow):
  - `origin` → **`ben-jamin-chen/CodeGraphContext`** — the personal fork, where we push.
  - `upstream` → **`CodeGraphContext/CodeGraphContext`** — the canonical org repo, where we pull from.
- Local `main` tracks **`upstream/main`**. Never push commits directly to `upstream`; push to `origin` and open PRs against `upstream`.
- Our working branch is **`crexi-watcher-pool`**, tracking `origin/crexi-watcher-pool`. It carries our perf enhancements as commits on top of `upstream/main`.
- `gh` has two accounts logged in: `ben-jamin-chen` (active, used for fork operations) and `bc-crexi` (inactive). Run `gh auth status` to confirm `ben-jamin-chen` is active before any `gh` push/PR/fork commands.
- Local enhancements at time of writing (three commits, in order):
  1. `watcher: bound concurrent file-event handlers via ThreadPoolExecutor` — bounded `ThreadPoolExecutor` in `src/codegraphcontext/core/watcher.py` to avoid Neo4j connection pool exhaustion on event bursts.
  2. `watch: accept multiple directories in one watcher process` — variadic `cgc watch [PATHS]...` in `src/codegraphcontext/cli/main.py` + `cli_helpers.py`; the systemd unit depends on this.
  3. `watch: gate startup sync behind CGC_WATCH_SYNC_ON_START (default off)` — in `cli_helpers.py`; upstream's v0.5.0 `sync_on_start` re-parses **every** file with no change detection, which on the Crexi monolith is a multi-hour full re-index on each watcher restart that severs cross-file CALLS edges until the end-of-sync relink (this bit us on 2026-06-11: DevTools + Lease edges had to be repaired by re-indexing those subtrees).

  If new local enhancements are added, list them in step 4 below.
- `cgc` is installed in **editable mode** in `/home/t-x/git/CodeGraphContext/.venv` (`.venv/lib/python*/site-packages/__editable__.codegraphcontext-*.pth` points at `/home/t-x/git/CodeGraphContext/src`).
- `cgc-watch.service` is a **systemd user service** that runs `cgc watch /home/t-x/git/backend /home/t-x/git/web` (multi-path support comes from our local enhancement #2 — if that patch is lost, the service fails on restart). Because it's a long-running Python process, source edits in this checkout do not hot-reload — the service must be restarted after a resync.
- `cgc` CLI subcommands (`cgc query`, etc.) fork fresh each invocation, so they automatically pick up new source — no restart needed.

## Procedure

### 1. Snapshot starting state

```bash
git status
git rev-parse --is-shallow-repository
git remote -v
git log --oneline -5 main
git log --oneline -5 crexi-watcher-pool
git diff main..crexi-watcher-pool --stat
git ls-remote origin HEAD
```

If the clone is shallow (returns `true`), run `git fetch --unshallow origin main` once. After that, the clone is permanent and you won't need to do it again.

### 2. Fast-forward main from upstream

```bash
git checkout main
git pull --ff-only upstream main
```

If `--ff-only` rejects, something has been committed locally to `main` that doesn't belong there — investigate before forcing anything. (`main` tracks `upstream/main`, so a bare `git pull` works too, but be explicit when in doubt.)

### 3. Check whether upstream touched files we patched

```bash
git log --oneline <previous-main-tip>..main -- src/codegraphcontext/core/watcher.py
```

If empty: rebase/cherry-pick will be clean. If non-empty: inspect each commit and follow the conflict policy in step 4.

### 4. Replay our enhancements on top of fresh main

**Preferred:** rebase.

```bash
git checkout crexi-watcher-pool
git rebase main
```

**Fallback** if `git rebase` is blocked by your permission layer (Bash policy denies it), use cherry-pick — exactly equivalent here as long as the branch is a clean sequence of commits with no merge commits:

```bash
git checkout crexi-watcher-pool
git reset --keep main
git cherry-pick <each enhancement commit, in original order>
```

**Conflict policy — `src/codegraphcontext/core/watcher.py`:**

These edits must persist (re-apply them into upstream's new shape if the file was refactored):

- `from concurrent.futures import ThreadPoolExecutor` near the top of the file.
- `self._executor = ThreadPoolExecutor(max_workers=int(get_config_value("WATCHER_MAX_WORKERS") or 8), thread_name_prefix="cgc-watcher-worker")` inside `RepositoryEventHandler.__init__`.
- In the debounce path, the `threading.Timer` callback must be `lambda: self._executor.submit(action)` — the action runs on the executor, not directly in the Timer thread.

If upstream has introduced its own concurrency model (their own pool, asyncio rewrite, worker queue), **stop and ask the user** before re-applying our patch — it may be redundant or actively wrong against the new model.

**Conflict policy — `src/codegraphcontext/cli/cli_helpers.py` / `cli/main.py`:**

- The `watch` command must keep its variadic `paths` argument and `watch_helper` its per-path validation + watch loop (enhancement #2).
- `watch_helper` must NOT pass `sync_on_start=True` unconditionally for already-indexed repos — keep it gated behind `CGC_WATCH_SYNC_ON_START` (enhancement #3). If upstream adds change detection (file hashing / mtime skip) to `synchronize_with_disk` / `update_file_in_graph`, the gate may become unnecessary — verify before dropping it, and test on a scratch repo, never by restarting the production watcher first.

### 5. Verify the replay

```bash
git log --oneline main..crexi-watcher-pool          # should show our enhancement commits only
git diff main..crexi-watcher-pool --stat            # should list only the files our patches touch
git diff main -- src/codegraphcontext/core/watcher.py | grep -E '(ThreadPoolExecutor|cgc-watcher-worker|_executor\.submit)'
git diff main -- src/codegraphcontext/cli/cli_helpers.py | grep -E '(CGC_WATCH_SYNC_ON_START|path_objs)'
.venv/bin/cgc watch --help 2>&1 | grep -F '[PATHS]...'
```

All grep terms must hit. If any are missing, a patch lost something during conflict resolution — fix before continuing.

### 6. Push the resynced state to your fork

```bash
git push origin main                                # fast-forward, no force needed
git push --force-with-lease origin crexi-watcher-pool  # required: rebase rewrote history
```

`--force-with-lease` is the safe form of `--force` — it refuses the push if `origin/crexi-watcher-pool` has new commits we don't know about, which protects against blowing away work pushed from another machine. Never use plain `--force` for this branch.

### 7. Refresh the editable install metadata

`cgc --version` reads the version from frozen install metadata (`importlib.metadata`), **not** from the source or `pyproject.toml`. After a resync that bumped `version` in `pyproject.toml`, the `.dist-info` is stale until regenerated, so `cgc --version` lies (e.g. reports `0.4.10` when the source is `0.4.12`). The running code is always correct regardless — this only fixes the reported string.

This venv has **no in-venv `pip`** (it was created by `uv`). Regenerate the metadata with global `uv`, `--no-deps` (pure metadata refresh, no dependency churn, safe while the watcher runs):

```bash
uv pip install -e /home/t-x/git/CodeGraphContext \
  --python /home/t-x/git/CodeGraphContext/.venv/bin/python \
  --no-deps
```

Verify: `cgc --version` now matches `pyproject.toml`, and `.venv/lib/python*/site-packages/` shows the new `codegraphcontext-<version>.dist-info`. The `.pth` still points at `src/`, so no source behavior changes. Skip this step if `pyproject.toml`'s `version` was unchanged by the resync.

### 8. Restart the running watcher

```bash
systemctl --user restart cgc-watch.service
systemctl --user is-active cgc-watch.service        # → active
systemctl --user status cgc-watch.service --no-pager | head -15
```

Confirm the new `Main PID` is different from before, the start timestamp is current, and the journal shows the normal `🔍 Watching` / `👀 Monitoring` lines with no tracebacks.

### 9. Smoke test (optional but cheap)

Touch a file in `/home/t-x/git/backend` and tail the service journal — you should see the watcher pick it up and process it on a thread named `cgc-watcher-worker-N` (proves our pool patch is the active code path).

```bash
journalctl --user -u cgc-watch.service -n 30 --no-pager
```

## Things this skill is NOT for

- Opening a PR against `upstream`. That's a separate workflow — `gh pr create --repo CodeGraphContext/CodeGraphContext --base main --head ben-jamin-chen:crexi-watcher-pool`. Only do this if we actually want to upstream a patch.
- Restarting Neo4j. The database is decoupled from cgc source. Only restart it if upstream ships a schema migration.
- Resyncing other indexed repositories (the watcher targets `/home/t-x/git/backend`, not this repo). That's a separate workflow.
- Building/installing cgc from scratch — the editable install is already wired. The only sanctioned install command is the `uv pip install -e . --no-deps` metadata refresh in step 7; never run a full `pip install`/`uv pip install` (with deps) or recreate the venv unless you deliberately intend to change the dependency set.
