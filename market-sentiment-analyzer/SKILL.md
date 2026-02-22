---
name: market-sentiment-analyzer
description: "Analyze market sentiment by reading unified feeds from the local data gateway. Use when: (1) The user asks for a market summary or current 'vibe', (2) Analyzing specific crypto news/trends from Binance Square, (3) Identifying bullish or bearish trends based on recent social media and news data."
---

# Market Sentiment Analyzer

This skill enables the analysis of cryptocurrency market sentiment using data aggregated by the local `data-gateway`.

## Workflow

1.  **Fetch Data**: Use the `scripts/fetch_data.py` script or `curl` to retrieve the latest feed from the gateway.
2.  **Analyze**: Review the text of each record to identify:
    *   **Sentiment**: Bullish, Bearish, or Neutral.
    *   **Keywords**: Mentioned assets (BTC, ETH, etc.), regulatory news, macro events.
    *   **Source Weight**: Consider the author's stats (followers, likes) if available in the `publisher` field.
3.  **Summarize**: Provide a concise summary of the overall market sentiment and highlight key drivers.

## Usage Examples

### Fetching recent trends
```bash
python3 scripts/fetch_data.py --limit 20 --source binance_square
```

### Fetching global news
```bash
python3 scripts/fetch_data.py --limit 10 --source binance_square_news
```

## Reference

- **API Specification**: See [references/api.md](references/api.md) for endpoint details and data schemas.
- **Data Gateway**: The gateway is assumed to be running on `http://localhost:3000`.
