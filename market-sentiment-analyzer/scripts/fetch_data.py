#!/usr/bin/env python3
import urllib.request
import json
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Fetch data from Data Gateway for sentiment analysis.")
    parser.add_argument("--limit", type=int, default=10, help="Number of records to fetch")
    parser.add_argument("--source", type=str, help="Source to filter by")
    args = parser.parse_args()

    url = f"http://localhost:3000/feed?limit={args.limit}"
    if args.source:
        url += f"&source={args.source}"

    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                print(f"Error: Received status {response.status}")
                sys.exit(1)
            
            data = json.loads(response.read().decode())

        if not data:
            print("No data found in the gateway.")
            return

        print(f"--- Fetched {len(data)} records ---")
        for i, record in enumerate(data, 1):
            content = record.get("content", {})
            author = content.get("author", "Unknown")
            text = content.get("text", "")
            print(f"\n[{i}] Source: {record.get('source')} | Author: {author}")
            # Clean up newlines for prettier console output
            preview = text.replace('\n', ' ')
            print(f"Text: {preview[:300]}..." if len(preview) > 300 else f"Text: {preview}")
            
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
