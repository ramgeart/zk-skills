# Playbook — Persistent Agents (Docker Compose + VPN)

## Agent model
- One agent = one compose stack (`vpn` + `ui`)
- UI shares VPN network namespace (`network_mode: service:vpn`)
- Credentials mount is read-only
- Desired state declared in `$AGENTS_ROOT/registry.json`

## Standard operations

### Create/update from registry
1. Add/modify entry in `registry.json`
2. Run `agentsctl apply --agent <name>`
3. Run `agentsctl status --agent <name>`
4. Run `agentsctl health --agent <name>`

### Start/stop on demand
- Start: set `state: "running"` then `agentsctl apply --agent <name>`
- Stop: set `state: "stopped"` then `agentsctl apply --agent <name>`

### Assign a task
- Use `docker exec` on `agent-<name>-ui` for bounded commands
- Write outputs to `/config/tasks/` for persistence
- Re-run health check after task execution

## Acceptance criteria (minimum)

1. `agent-<name>-vpn` and `agent-<name>-ui` are running.
2. UI responds on `127.0.0.1:<port>` (HTTP 200/401 acceptable for auth-gated UI).
3. Country check from VPN namespace matches expected country.
4. Host gateway from agent subnet is blocked.
5. Credentials file inside UI container is mounted read-only.

## Troubleshooting quick map

- VPN up but wrong country:
  - verify `.env.vpn` values generated from WireGuard file
  - test country from multiple APIs (ipapi/ipwhois)
- UI unreachable:
  - check `FIREWALL_INPUT_PORTS` includes UI port (3000 inside namespace)
  - verify loopback port binding on vpn service
- Agent can hit host network:
  - verify `DOCKER-USER` rules for agent subnet
  - verify source subnet in registry matches compose subnet

## Security posture

- Keep `blockHostIps` in registry for explicit host addresses to deny.
- Never mount full OpenClaw config into agent containers.
- Keep agent data isolated in `$AGENTS_ROOT/<name>/data`.
