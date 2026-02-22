# Data Gateway API Reference

The Data Gateway is a local service providing a unified feed of market-related news and social media posts.

## Base URL
`http://localhost:3000`

## Endpoints

### GET /feed
Retrieves the latest ingested records.

**Parameters:**
- `limit` (integer, optional): Maximum number of records to return. Default: 10.
- `source` (string, optional): Filter by source.
    - `binance_square`: Trending posts from Binance Square.
    - `binance_square_news`: Global news items from Binance Square.

**Response:**
A JSON array of records:
```json
[
  {
    "source": "binance_square",
    "external_id": "...",
    "content": {
      "author": "Author Name",
      "text": "Full text of the post/news",
      "url": "Original URL",
      "publisher": {
        "name": "...",
        "bio": "...",
        "followers": "...",
        "following": "...",
        "liked": "...",
        "shared": "..."
      }
    },
    "timestamp": "2026-02-20T17:00:24Z"
  }
]
```
