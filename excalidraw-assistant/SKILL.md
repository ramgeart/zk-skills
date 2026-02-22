---
name: excalidraw-assistant
description: Create interactive hand-drawn diagrams using the Excalidraw MCP server. Use when asked to draw diagrams, flowcharts, architecture visuals, mind maps, sequence diagrams, or any sketch-style illustration. Renders interactive Excalidraw canvases via MCP Apps with smooth viewport animation and fullscreen editing.
---

# Excalidraw Assistant

Creates interactive Excalidraw diagrams via the [Excalidraw MCP](https://github.com/excalidraw/excalidraw-mcp) server. Diagrams render as interactive MCP App widgets directly in the chat — not static images.

## Prerequisites

- `mcporter` CLI installed (`npm install -g mcporter`)
- Excalidraw MCP server configured

Run `scripts/setup-mcp.sh` to configure automatically, or manually:

```bash
mcporter config add excalidraw --url https://mcp.excalidraw.com
```

Verify: `mcporter list excalidraw --schema` should show 5 tools.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `read_me` | Returns the element format reference. Call ONCE per conversation before `create_view`. |
| `create_view` | Renders elements as an interactive Excalidraw canvas. Takes `elements` (JSON string). |
| `export_to_excalidraw` | Uploads diagram to excalidraw.com, returns shareable URL. Takes `json` (JSON string). |
| `save_checkpoint` | Saves diagram state for later restore. |
| `read_checkpoint` | Reads saved checkpoint state. |

## Workflow

### First diagram in a conversation

1. Call `read_me` — loads element format reference (colors, shapes, arrows, camera). Do this **once**.
2. Build your elements JSON array following the format from `read_me`.
3. Call `create_view` with `elements` as a **JSON string** (not a parsed array).
4. Optionally call `export_to_excalidraw` to get a shareable URL.

### Editing an existing diagram

1. Use the `checkpointId` returned by `create_view`.
2. Start elements with `{"type": "restoreCheckpoint", "id": "<checkpointId>"}`.
3. Add new elements or use `{"type": "delete", "ids": "id1,id2"}` to remove.
4. Call `create_view` again.

### Via script

```bash
python3 scripts/create-diagram.py --file elements.json
python3 scripts/create-diagram.py --file elements.json --export
python3 scripts/create-diagram.py --elements '[...]' --checkpoint abc123
```

## Element Format Source of Truth

Use **exactly**: [references/element-format.md](references/element-format.md)

This file is the canonical spec for element format, camera rules, palette, checkpoints, delete/restore patterns, dark mode, and examples. Do not simplify it, paraphrase it away, or invent alternative rules.

Rules:
1. Call `read_me` once per conversation.
2. Then follow `references/element-format.md` exactly.
3. Do not call `read_me` again in the same conversation.
4. Always send `elements` to `create_view` as a JSON **string**.

### Key rules

- **Always start with a `cameraUpdate`** as the first element (controls viewport).
- Camera must be **4:3 ratio**: 400×300, 600×450, 800×600, 1200×900, 1600×1200.
- **Minimum font size**: 16 for body, 20 for titles, never below 14.
- **Draw order matters**: background → shape → its label → its arrows → next shape (progressive).
- **`elements` must be a JSON string**, not a parsed array — the MCP schema requires `type: string`.
- Use `label` property on shapes for auto-centered text (preferred over separate text elements).
- Arrow bindings use `fixedPoint`: top=[0.5,0], bottom=[0.5,1], left=[0,0.5], right=[1,0.5].

### Minimal example

```json
[
  {"type": "cameraUpdate", "width": 800, "height": 600, "x": 0, "y": 0},
  {"type": "rectangle", "id": "b1", "x": 100, "y": 100, "width": 200, "height": 100,
   "roundness": {"type": 3}, "backgroundColor": "#a5d8ff", "fillStyle": "solid",
   "label": {"text": "Start", "fontSize": 20}},
  {"type": "rectangle", "id": "b2", "x": 450, "y": 100, "width": 200, "height": 100,
   "roundness": {"type": 3}, "backgroundColor": "#b2f2bb", "fillStyle": "solid",
   "label": {"text": "End", "fontSize": 20}},
  {"type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 150, "height": 0,
   "points": [[0,0],[150,0]], "endArrowhead": "arrow",
   "startBinding": {"elementId": "b1", "fixedPoint": [1, 0.5]},
   "endBinding": {"elementId": "b2", "fixedPoint": [0, 0.5]}}
]
```

### Color palette

**Shape fills (pastel):** `#a5d8ff` (blue), `#b2f2bb` (green), `#ffd8a8` (orange), `#d0bfff` (purple), `#ffc9c9` (red), `#fff3bf` (yellow), `#c3fae8` (teal), `#eebefa` (pink)

**Zone backgrounds (opacity 30-35):** `#dbe4ff` (blue), `#e5dbff` (purple), `#d3f9d8` (green)

**Stroke/accent:** `#4a9eed` (blue), `#22c55e` (green), `#f59e0b` (amber), `#ef4444` (red), `#8b5cf6` (purple), `#ec4899` (pink), `#06b6d4` (cyan)

## Common Diagram Types

| Type | Tips |
|------|------|
| **Flowchart** | Top-to-bottom or left-to-right. Diamonds for decisions. |
| **Architecture** | Group with zone rectangles (low opacity). Labeled arrows for protocols. |
| **Sequence** | Vertical lifelines (dashed arrows), horizontal message arrows, actor boxes at top. |
| **Mind map** | Central node, radiating branches. Use colors to group themes. |
| **Animation** | Use `delete` + replace at same position + camera nudges for transformation effects. |

## Tips

- Use `cameraUpdate` liberally — it animates smoothly and guides attention as you draw.
- For large diagrams, zoom into each section as you draw it, then zoom out at the end.
- Do NOT use emoji in text — Excalidraw's font doesn't render them.
- For dark mode: add a massive dark rectangle first, use dark fills and light text (see full reference).
- Never reuse a deleted element's ID — always assign new IDs.
