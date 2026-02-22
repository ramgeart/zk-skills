---
name: proton-suite
description: "Manage Proton ecosystem products through browser automation: Mail, Calendar, Drive, Pass, Docs, and Sheets (spreadsheets inside Proton Docs). Use when reading/sending email, managing events, organizing files, handling credentials in Proton Pass, or creating/editing Proton documents and sheets. Requires browser tool on host with profile=openclaw."
---

# Proton Suite

Control Proton apps from the host browser session.

## Fixed context

- Account: *(configure your Proton account)*
- Session mode: keep signed in
- Browser: `target=host`, `profile=openclaw`

## App entrypoints

- Mail: `https://mail.proton.me/u/0`
- Calendar: `https://calendar.proton.me/u/0`
- Drive: `https://drive.proton.me/u/0`
- Pass: `https://pass.proton.me/u/0`
- Docs/Sheets: `https://docs.proton.me/u/0`
- Account/login: `https://account.proton.me/apps`

## Workflow

1. Call `browser.tabs` and reuse an existing Proton tab when possible.
2. If needed, `browser.navigate` to the app entrypoint.
3. Take `browser.snapshot` and act only on current refs.
4. For multi-step operations, confirm intent before high-impact actions:
   - Mail: sending, deleting, archiving many messages
   - Calendar: deleting/editing existing events
   - Drive/Docs/Sheets: deleting/moving files or changing share permissions
   - Pass: creating, editing, deleting credentials
5. After each mutation, snapshot again and verify result state.

## Reliability rules

- Proton is SPA-heavy: if UI looks partial, snapshot again after a short wait.
- Prefer deterministic actions (`click`, `type`, `select`) over evaluate scripts.
- If auth expires, go to account URL and re-authenticate, then return to the target app.
- Keep outputs concise: report what changed, what failed, and next safe step.
