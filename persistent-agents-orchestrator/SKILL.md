---
name: persistent-agents-orchestrator
description: "Manage declarative persistent agents running as per-agent Docker Compose stacks (VPN + UI), with strict VPN-only egress and network isolation rules. Use when creating, starting, stopping, bootstrapping, checking health, or assigning tasks to named agents from the registry."
---

# Persistent Agents Orchestrator

Operate persistent agents from a declarative registry.

## Runtime paths

- Registry: `$AGENTS_ROOT/registry.json`
- Orchestrator CLI: `$AGENTS_ROOT/agentsctl`
- Per-agent root: `$AGENTS_ROOT/<agent-name>/`

## Core commands

- List agents: `agentsctl list`
- Apply desired state: `agentsctl apply [--agent <name>]`
- Status: `agentsctl status [--agent <name>]`
- Health: `agentsctl health [--agent <name>]`

## Workflow

1. Read current registry entry for target agent.
2. Apply desired state (`running` or `stopped`).
3. Validate health (UI reachability + VPN egress + host-isolation check).
4. Execute requested task on the target agent container.
5. Re-validate health and report concise result.

## Safety rules

- Keep credentials mounted read-only inside agent UI container.
- Do not expose private keys, tokens, or full credential files in chat output.
- Confirm before destructive actions (deleting agent data, mass stops, changing VPN profiles).
- Keep UI published to loopback only (`127.0.0.1:<port>`), not public bind.

## References

- Basic operations and acceptance checks: `references/playbook.md`
