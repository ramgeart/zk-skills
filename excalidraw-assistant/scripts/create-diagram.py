#!/usr/bin/env python3
"""Create an Excalidraw diagram via the MCP server using mcporter.

Usage:
  python3 create-diagram.py --elements '<json array string>'
  python3 create-diagram.py --file elements.json
  python3 create-diagram.py --file elements.json --export
"""
import argparse
import json
import subprocess
import sys


def call_mcp(tool: str, args: dict) -> str:
    """Call an Excalidraw MCP tool via mcporter."""
    result = subprocess.run(
        ["mcporter", "call", f"excalidraw.{tool}", "--args", json.dumps(args)],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr or result.stdout}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Create Excalidraw diagrams via MCP")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--elements", help="JSON array string of Excalidraw elements")
    group.add_argument("--file", help="Path to JSON file with elements array")
    parser.add_argument("--export", action="store_true", help="Export to excalidraw.com shareable URL")
    parser.add_argument("--checkpoint", help="Restore from checkpoint ID before adding elements")
    args = parser.parse_args()

    # Load elements
    if args.file:
        with open(args.file) as f:
            elements = json.load(f)
        elements_str = json.dumps(elements)
    else:
        elements_str = args.elements

    # Optionally prepend checkpoint restore
    if args.checkpoint:
        arr = json.loads(elements_str)
        arr.insert(0, {"type": "restoreCheckpoint", "id": args.checkpoint})
        elements_str = json.dumps(arr)

    # Create the view
    print("Creating diagram...")
    result = call_mcp("create_view", {"elements": elements_str})
    print(result)

    # Optionally export
    if args.export:
        print("\nExporting to excalidraw.com...")
        url = call_mcp("export_to_excalidraw", {"json": elements_str})
        print(f"Shareable URL: {url}")


if __name__ == "__main__":
    main()
