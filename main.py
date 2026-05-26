"""
R6 Siege Stats Proxy API
Self-hosted alternative to avoid Ubisoft rate limits via caching.
"""

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Environment variables
R6_EMAIL = os.getenv("R6_EMAIL")
R6_PASSWORD = os.getenv("R6_PASSWORD")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour default

# In-memory TTL cache
cache: Dict[str, dict] = {}


def _cache_key(name: str, platform: str) -> str:
    return f"{platform}:{name.lower()}"


def _get_cached(name: str, platform: str) -> Optional[dict]:
    key = _cache_key(name, platform)
    entry = cache.get(key)
    if entry and (time.time() - entry["_cached_at"]) < CACHE_TTL_SECONDS:
        return entry["data"]
    return None


def _set_cached(name: str, platform: str, data: dict):
    key = _cache_key(name, platform)
    cache[key] = {"data": data, "_cached_at": time.time()}


# Ubisoft auth singleton
auth = None
auth_lock = asyncio.Lock()


async def _ensure_auth():
    global auth
    if auth is not None:
        return auth

    from siegeapi import Auth

    async with auth_lock:
        if auth is not None:
            return auth
        if not R6_EMAIL or not R6_PASSWORD:
            raise RuntimeError("Missing R6_EMAIL or R6_PASSWORD environment variables")
        auth = Auth(R6_EMAIL, R6_PASSWORD)
        await auth.connect()
        return auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: nothing special needed (lazy auth).
    Shutdown: close Ubisoft session."""
    yield
    global auth
    if auth is not None:
        try:
            await auth.close()
        except Exception:
            pass


app = FastAPI(
    title="R6 Proxy API",
    description="Self-hosted Rainbow Six Siege stats proxy with caching",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/player")
async def get_player(
    name: str = Query(..., description="Player username"),
    platform: str = Query("uplay", description="Platform: uplay, psn, xbl, xplay"),
):
    """Fetch player stats from Ubisoft with caching."""
    valid_platforms = {"uplay", "psn", "xbl", "xplay"}
    if platform not in valid_platforms:
        raise HTTPException(status_code=400, detail=f"Invalid platform. Must be one of: {valid_platforms}")

    if not name.strip():
        raise HTTPException(status_code=400, detail="Name is required")

    # Check cache first
    cached = _get_cached(name, platform)
    if cached:
        return {"status": "cached", **cached}

    try:
        auth_client = await _ensure_auth()
        player = await auth_client.get_player(name, platform)

        # Load stats
        await player.load_progress()
        await player.load_ranked_v2()

        response = {
            "status": "ok",
            "player": {
                "name": player.name,
                "platform": platform,
                "level": player.level,
                "id": player.id,
                "uid": player.uid,
                "profile_pic_url": player.profile_pic_url,
            }
        }

        if player.ranked_profile:
            rp = player.ranked_profile
            kd = round(rp.kills / rp.deaths, 2) if rp.deaths > 0 else rp.kills
            response["rank"] = {
                "current": rp.rank,
                "current_id": rp.rank_id,
                "mmr": rp.rank_points,
                "max_rank": rp.max_rank,
                "max_rank_id": rp.max_rank_id,
                "top_rank_position": rp.top_rank_position,
                "season_id": rp.season_id,
                "season_code": rp.season_code,
                "wins": rp.wins,
                "losses": rp.losses,
                "abandons": rp.abandons,
                "kills": rp.kills,
                "deaths": rp.deaths,
                "kd_ratio": kd,
            }
        else:
            response["rank"] = None

        # Store in cache
        _set_cached(name, platform, response)
        return response

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Too many calls" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="Ubisoft rate limit reached. Try again later or use cached data."
            )
        raise HTTPException(status_code=500, detail=f"Failed to fetch player: {error_msg}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "cache_entries": len(cache)}


@app.get("/")
async def root():
    return {
        "service": "R6 Proxy API",
        "endpoints": {
            "player_stats": "/api/player?name=USERNAME&platform=uplay",
            "health": "/api/health",
        },
        "cache_ttl_seconds": CACHE_TTL_SECONDS,
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
