---
name: wireguard-panel
description: "Manage WireGuard VPN client profiles directly from a web admin panel using browser automation. Use when creating, editing, revoking, downloading, or rotating WireGuard peer profiles and QR configs from the panel UI, including validation and safe-change confirmation steps."
---

# WireGuard Panel

Operate WireGuard profile lifecycle from the panel UI with safe, repeatable browser actions.

## Scope

- Create new peer/profile
- Edit profile metadata (name, limits, expiry, tags)
- Regenerate keys/config
- Download `.conf` and/or QR
- Revoke, disable, enable, or delete profiles
- Verify that profile state changed as requested

## Required tooling

- Use `browser` with `target=host`.
- Prefer an already-open panel tab; otherwise navigate to panel URL provided by user.
- Use snapshots before and after each mutation.

## Workflow

1. Identify panel tab (`browser.tabs`) and focus it.
2. Snapshot current state and locate the target profile list/table.
3. Confirm target profile identity before edits (name/id/public key suffix).
4. Execute exactly one requested mutation at a time.
5. Snapshot and verify success state (status badge, updated timestamp, row state, toast).
6. Report concise result and next actionable option.

## Safety rules

- Ask for confirmation before destructive operations: delete, revoke, mass changes, or key rotation affecting active users.
- Never expose private keys in chat output.
- If UI is ambiguous, stop and ask for disambiguation (same names, duplicated peers).
- For bulk requests, provide dry-run summary first (what will change) unless user explicitly asks immediate execution.

## Output format

- `Done`: action completed + profile name/id.
- `Verified`: concrete UI evidence (badge/state row text).
- `Artifacts`: config/QR downloaded or where it is available in UI.
- `Next`: optional follow-up (test handshake, rotate old peer, etc.).
