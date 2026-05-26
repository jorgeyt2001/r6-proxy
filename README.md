# R6 Proxy API

Self-hosted Rainbow Six Siege stats API with caching.

## Endpoints

- `GET /api/player?name=USERNAME&platform=uplay` — Player stats
- `GET /api/health` — Health check

## Deploy

### Render
1. Create account at https://render.com
2. Create new Web Service
3. Connect this repo or upload files
4. Add environment variables: `R6_EMAIL`, `R6_PASSWORD`

### Local
```bash
pip install -r requirements.txt
R6_EMAIL=... R6_PASSWORD=... python main.py
```
