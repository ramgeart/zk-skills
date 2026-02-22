---
name: excalidraw-assistant
description: Create and edit hand-drawn style diagrams via the Excalidraw MCP server. Use when asked to draw diagrams, flowcharts, architecture visuals, mind maps, or any sketch-style illustration. Connects to excalidraw-mcp (remote or local) for rendering and interactive editing.
---

# Excalidraw Assistant

Create hand-drawn style diagrams using the [Excalidraw MCP](https://github.com/excalidraw/excalidraw-mcp) server.

## MCP Server Setup

The skill uses the Excalidraw MCP App server. Two modes:

### Remote (recommended)

MCP endpoint: `https://mcp.excalidraw.com`

Configure in OpenClaw or your MCP client:

```json
{
  "mcpServers": {
    "excalidraw": {
      "url": "https://mcp.excalidraw.com"
    }
  }
}
```

### Local

```bash
git clone https://github.com/excalidraw/excalidraw-mcp.git
cd excalidraw-mcp
pnpm install && pnpm run build
```

```json
{
  "mcpServers": {
    "excalidraw": {
      "command": "node",
      "args": ["/path/to/excalidraw-mcp/dist/index.js", "--stdio"]
    }
  }
}
```

## Workflow

1. **Understand the request** — What type of diagram? (flowchart, architecture, mind map, sequence, entity-relationship, network, etc.)
2. **Call the MCP tool** — Use `create_excalidraw_diagram` with a clear description
3. **Present the result** — The MCP returns an interactive Excalidraw canvas or PNG
4. **Iterate** — User can ask to modify, add elements, change styles

## Diagram Types & Prompting Tips

| Type | Key elements to specify |
|------|------------------------|
| **Flowchart** | Steps, decisions, start/end, flow direction |
| **Architecture** | Components, connections, protocols, layers |
| **Mind map** | Central topic, branches, sub-branches |
| **Sequence** | Actors, messages, order, async vs sync |
| **ER diagram** | Entities, relationships, cardinality |
| **Network** | Nodes, connections, labels, topology |

## Best Practices

- Be specific about layout direction (left-to-right, top-to-bottom)
- Name every node/component explicitly
- Specify connection labels and arrow types
- For complex diagrams, build incrementally (start simple, add detail)
- Use color coding to group related elements

## Example Prompts

```
"Draw an architecture diagram: user → load balancer → 3 API servers → PostgreSQL database"
"Create a flowchart for user registration: signup form → validate email → send confirmation → activate account"
"Mind map for project planning with branches: scope, timeline, resources, risks"
```

## Limitations

- MCP Apps extension required in the client (Claude, ChatGPT, VS Code, Goose, etc.)
- Remote server depends on `mcp.excalidraw.com` availability
- Complex diagrams may need iterative refinement
