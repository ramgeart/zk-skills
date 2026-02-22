#!/usr/bin/env bash
# Setup Excalidraw MCP server via mcporter
# Usage: ./setup-mcp.sh [--local /path/to/excalidraw-mcp]
set -euo pipefail

if ! command -v mcporter &>/dev/null; then
  echo "Installing mcporter..."
  npm install -g mcporter
fi

if mcporter list 2>/dev/null | grep -q "^excalidraw"; then
  echo "✅ Excalidraw MCP already configured"
  mcporter list excalidraw
  exit 0
fi

if [[ "${1:-}" == "--local" && -n "${2:-}" ]]; then
  LOCAL_PATH="$2"
  if [[ ! -f "$LOCAL_PATH/dist/index.js" ]]; then
    echo "Building from source..."
    cd "$LOCAL_PATH"
    pnpm install && pnpm run build
  fi
  mcporter config add excalidraw --stdio "node $LOCAL_PATH/dist/index.js --stdio"
  echo "✅ Excalidraw MCP configured (local: $LOCAL_PATH)"
else
  mcporter config add excalidraw --url https://mcp.excalidraw.com
  echo "✅ Excalidraw MCP configured (remote: https://mcp.excalidraw.com)"
fi

# Verify
mcporter list excalidraw --schema
