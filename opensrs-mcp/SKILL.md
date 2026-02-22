---
name: opensrs-mcp
description: "Operate OpenSRS reseller API through a hardened MCP bridge. Use this whenever the user asks to manage domains or DNS in OpenSRS (list domains, check balance, read DNS zone, create/update A records, or automate OpenSRS tasks). This skill fixes known OpenSRS pitfalls: wrong endpoint, missing XCP protocol, and invalid DNS actions."
---

# OpenSRS MCP (consolidated)

Use this skill for OpenSRS automation with reliable defaults.

## Known-good OpenSRS behavior

- Endpoint: `https://rr-n1-tor.opensrs.net:55443/`
- Envelope must include: `<item key="protocol">XCP</item>`
- Auth signature: `MD5(MD5(payload + api_key) + api_key)`
- DNS zone read/write works with:
  - `object=domain`, `action=get_dns_zone`
  - `object=domain`, `action=set_dns_zone`
- **Do not use** old invalid actions like `dns_zone/get_records`.

## Required environment

- `OPENSRS_USERNAME`
- `OPENSRS_API_KEY`
- Optional: `OPENSRS_ENDPOINT` (defaults to `rr-n1-tor`)

Example:

```bash
cp .env.example .env
# fill values
export $(grep -v '^#' .env | xargs)
```

## Included components

- `scripts/opensrs_mcp_server.js` → MCP server (stdio)
- `scripts/test_prod.js` → production smoke test
- `scripts/opensrs_bridge.py` → simple CLI bridge for direct XML calls

## Quick validation (must pass)

```bash
npm install
npm run test:prod
```

Expected successful checks:

1. `reseller/get_balance`
2. `domain/get_domains_by_expiredate`
3. `domain/get_dns_zone`

## MCP tools exposed by server

- `opensrs_get_balance`
- `opensrs_list_domains`
- `opensrs_get_dns_zone`
- `opensrs_upsert_a_record`

## Safety rules

- Preserve existing zone records when updating A records.
- Never wipe records unless user explicitly requests full reset.
- Confirm destructive operations before executing.
