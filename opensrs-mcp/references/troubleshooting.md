# OpenSRS troubleshooting

## Common errors

### `Authentication Failed` (401)
- Wrong username/key combination.
- API key rotated and old key still in use.

### `Access denied: invalid ip address` (400)
- OpenSRS IP allowlist/firewall not updated for the current server IP.

### `Unrecognized protocol` (500)
- Missing `protocol=XCP` item in XML payload.
- Wrong envelope structure/order.

### `Invalid Command: get_records` (400)
- Invalid legacy command path (`dns_zone/get_records`).
- Use `domain/get_dns_zone` instead.

## Known-good minimal checks

1. `object=domain, action=lookup`
2. `object=reseller, action=get_balance`
3. `object=domain, action=get_dns_zone`

If #1 works but #2 fails with protocol errors, verify `protocol=XCP` presence in payload.
