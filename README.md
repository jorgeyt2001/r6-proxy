# R6 Siege Stats Proxy API

Self-hosted API proxy for Rainbow Six Siege player statistics with caching to avoid Ubisoft rate limits.

## Features

- 🎮 **Player Stats** — Get level, rank, MMR, K/D, wins, losses
- ⚡ **Caching** — Configurable TTL to reduce API calls
- 🔒 **Secure** — Credentials stored as environment variables
- 🚀 **Simple** — Single endpoint: `/api/player`

## Quick Start

### Local Development

```bash
# Clone the repo
git clone https://github.com/jorgeyt2001/r6-proxy.git
cd r6-proxy

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export R6_EMAIL=your_ubisoft_email
export R6_PASSWORD=your_ubisoft_password
export CACHE_TTL_SECONDS=3600

# Run the server
python main.py
```

### Deploy to Render

1. Fork or clone this repo to your GitHub
2. Create a [Render](https://render.com) account
3. Click **New → Web Service**
4. Connect your GitHub repo
5. Add environment variables:
   - `R6_EMAIL` — Your Ubisoft email
   - `R6_PASSWORD` — Your Ubisoft password
   - `CACHE_TTL_SECONDS` — Cache duration (default: 3600)

## API Endpoints

### Get Player Stats

```
GET /api/player?name=PLAYER_NAME&platform=uplay
```

**Parameters:**
- `name` (required) — Player username
- `platform` (optional) — `uplay`, `psn`, `xbl`, `xplay` (default: `uplay`)

**Example Response:**
```json
{
  "status": "ok",
  "player": {
    "name": "ShanksX009",
    "platform": "uplay",
    "level": 156,
    "id": "abc123...",
    "uid": "def456..."
  },
  "rank": {
    "current": "Gold III",
    "mmr": 2200,
    "wins": 150,
    "losses": 120,
    "kd_ratio": 1.45
  }
}
```

### Health Check

```
GET /api/health
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `R6_EMAIL` | Yes | - | Ubisoft account email |
| `R6_PASSWORD` | Yes | - | Ubisoft account password |
| `CACHE_TTL_SECONDS` | No | `3600` | Cache duration in seconds |
| `PORT` | No | `8000` | Server port |

## Tech Stack

- **FastAPI** — Web framework
- **Uvicorn** — ASGI server
- **siegeapi** — Ubisoft API wrapper
- **python-dotenv** — Environment variables

## License

MIT License — see [LICENSE](LICENSE) for details.

## Disclaimer

This project is for educational purposes. Uses Ubisoft's public API. Please respect Ubisoft's Terms of Service and don't abuse the API.