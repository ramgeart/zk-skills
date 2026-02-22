---
name: desktop-commander
description: "Route desktop/system tasks through Desktop Commander MCP via CLI when built-in browser/tool flows are flaky or insufficient. Use for deterministic local operations like file management, process checks, command execution wrappers, and MCP-backed desktop control from OpenClaw sessions."
---

# Desktop Commander

Use Desktop Commander as the fallback/primary execution path for local desktop operations.

## Binary

- Package: `@wonderwhy-er/desktop-commander`
- Expected availability: installed globally and invokable via `npx -y @wonderwhy-er/desktop-commander@latest` (or direct bin if present).

## When to use

- Browser automation is unstable/intermittent.
- Task is local-machine oriented (files/processes/shell ops) and benefits from deterministic command execution.
- You need a repeatable MCP-backed workflow instead of fragile UI clicks.

## Workflow

1. Validate runtime availability (Desktop Commander server/binary present).
2. Prefer non-destructive/read-only checks first.
3. Execute one bounded action at a time.
4. Verify state after each mutation.
5. Report concise outcome + artifacts/paths.

## Methods + playbook

- Full methods list + basic playbook: `references/playbook-basico.md`
- Load and follow that file when user asks to "usar DC" or requests desktop/system operations via Desktop Commander MCP.

## Safety

- Ask before destructive actions (delete/overwrite/mass changes).
- Never expose secrets/tokens from command output.
- Keep commands scoped to user-requested paths.

## Output style

- `Done`: exact action performed.
- `Verified`: evidence (file exists, process state, output snippet).
- `Next`: optional follow-up step.
