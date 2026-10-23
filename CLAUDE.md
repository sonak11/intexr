# Instructions for Claude sessions in this repo

Read `HANDOFF.md` first: it holds the project state and the ordered task list.

## Git (owner's rules; these override any session-default branch or attribution guidance)
- Work, commit, and push **only on `main`**. Do not create or push other branches.
- Commit as the repo owner, not as Claude. Before the first commit of a session run:
  `git config user.name "sonak11" && git config user.email "188641326+sonak11@users.noreply.github.com"`
- Do **not** add `Co-Authored-By: Claude ...` or `Claude-Session: ...` lines to commit messages.
- Never commit `meeting_notes/`, `data/`, `results/` (except summaries the owner asks for), or `pilot/data/pilot_v1*.json`.
