<!-- SHARED FILE. Canonical copy lives in leapps-org/leapps-parity. Do not edit in place;
     edit the canonical copy and re-run the sync script, or your change will be overwritten. -->

# Landing a change

Work on a feature branch and land it through a pull request. Do not push to `main`.
Branch prefixes follow existing repo style: `fix/`, `feat/`, `chore/`, `ci/`.

PRs leave a reviewable trail for co-maintainers; direct pushes are invisible to watchers.

A docs-generation bot commits on `main` after each merge, so **fetch before branching** or
you will start from a stale base.

## Attribution

Commits and PRs produced with an AI coding agent carry a trailer naming the agent **and its
version**, with the vendor's no-reply address so the co-author is actually attributed:

```
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Co-Authored-By: OpenAI Codex <codex@openai.com>
```

Name the tool and version *you* actually used. Do not copy the example literally. A trailer
with no `<email>` is not attributed by GitHub; it renders as plain body text.

Human co-authors get the usual trailer alongside it.

This applies to these repos. When contributing upstream to someone else's project, follow
that project's convention instead.

The artifact `author` field inside `__artifacts_v2__` is a **different surface** and stays
unversioned: `@YourHandle` or `@YourHandle, Claude`. That string reaches the HTML report
and the LAVA manifest and gets quoted in casework, where a model version is noise.

## After merging

Merged branches are not cleaned up automatically; these repos do not have
`delete_branch_on_merge` enabled, so remote branches linger indefinitely. Prefer:

```bash
gh pr merge <n> --merge --delete-branch
```

If the branch lives in a git worktree, `git worktree remove <path>` first or the local
delete fails. Otherwise, after merging: `git pull --ff-only` on main, `git branch -d`, then
`git push origin --delete <branch>`.

When a change should be evaluated for propagation to the other cores, apply the
**"Needs Cross Core Leveling"** label, and see `leapp-cross-core.md`.

## Shared checkouts

A LEAPP checkout may be in use by more than one session at a time. A clean `git status`
proves nothing; only a fetched remote does.

- Prefer an isolated worktree: `git worktree add <path> <your-branch>`. The shared checkout
  is never touched, so nobody can move the branch under you.
- Run `git branch --show-current` immediately before **every** commit, not once at the start.
- Stage explicit paths. Never `git add -A`. It sweeps up another session's untracked files.
- Never `git reset --hard` on a shared branch; it destroys uncommitted work that is not yours.
- Leave the checkout on a fast-forwarded `main` when you finish, not on a feature branch.
