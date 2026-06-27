"""
FastAPI server for Fantasy Helper.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from models.hero import Hero
from models.weapon import Weapon
from models.enemy import Enemy
from models.enums import RangeBand
from encounters.builder import build_encounter
from game_session import GameSession

import os

app = FastAPI()

# Global session (single active game)
current_session: Optional[GameSession] = None


# Pydantic models for API
class NewEncounterRequest(BaseModel):
    pass


class HeroAttackRequest(BaseModel):
    hero_name: str
    enemy_name: str
    spell_index: Optional[int] = None


class SetEnemyRangeRequest(BaseModel):
    enemy_name: str
    range_band: str  # "MEL", "OOM", "OOB"
    engaged_hero: Optional[str] = None


class ReinforcementRequest(BaseModel):
    unit_type: str  # "Fighter", "Wizard", "Orc Warrior", "Orc Archer"
    is_hero: bool


# Root endpoint - serve index.html
@app.get("/")
async def root():
    return FileResponse("static/index.html")


# API: Create new encounter
@app.post("/api/new-encounter")
async def new_encounter(request: NewEncounterRequest):
    global current_session

    # Build default hero party
    fighter_sword = Weapon("LSWD", "1d8", 2)
    fighter_bow = Weapon("BOW", "1d6", 1)
    
    wizard_mm = Weapon("MM", "1d8", 2)
    wizard_dagger = Weapon("DAG", "1d4", 0)
    
    claw = Weapon("CLAW", "1d4", 0)
    
    heroes = [
        Hero(
            name="Fighter",
            hp=25,
            max_hp=25,
            arm=4,
            str_=7,
            dex=5,
            ms=7,
            rs=1,
            spd=6,
            intel=2,
            weapon=fighter_sword,
            secondary_weapon=fighter_bow,
        ),
        Hero(
            name="Wizard",
            hp=12,
            max_hp=12,
            arm=1,
            str_=2,
            dex=4,
            ms=2,
            rs=2,
            spd=6,
            intel=8,
            weapon=wizard_mm,
            secondary_weapon=wizard_dagger,
        ),
    ]

    # Build encounter (simulates menu choices - default to Orc Warrior + Archer)
    enemies = [
        Enemy(
            name="Orc Warrior",
            hp=16,
            max_hp=16,
            arm=3,
            str_=6,
            dex=4,
            ms=6,
            spd=6,
            morale=5,
            pack=7,
            weapon=Weapon("AXE", "1d8", 2),
            secondary_weapon=claw,
            rng=RangeBand.OOM,
        ),
        Enemy(
            name="Orc Archer",
            hp=12,
            max_hp=12,
            arm=1,
            str_=4,
            dex=5,
            ms=4,
            spd=6,
            morale=5,
            pack=5,
            weapon=Weapon("BOW", "1d6", 1),
            secondary_weapon=claw,
            rng=RangeBand.OOM,
        ),
    ]

    current_session = GameSession(heroes, enemies)
    return current_session.get_state()


# API: Get current game state
@app.get("/api/game-state")
async def get_game_state():
    if not current_session:
        raise HTTPException(status_code=400, detail="No active game session")

    return current_session.get_state()


# API: Hero action
@app.post("/api/hero-attack")
async def hero_attack(request: HeroAttackRequest):
    if not current_session:
        raise HTTPException(status_code=400, detail="No active game session")

    result = current_session.hero_attack(
        request.hero_name, request.enemy_name, request.spell_index
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return current_session.get_state()


# API: Enemy turn
@app.post("/api/enemy-turn")
async def enemy_turn():
    if not current_session:
        raise HTTPException(status_code=400, detail="No active game session")

    result = current_session.enemy_turn()

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return current_session.get_state()


# API: Set enemy range
@app.post("/api/set-enemy-range")
async def set_enemy_range(request: SetEnemyRangeRequest):
    if not current_session:
        raise HTTPException(status_code=400, detail="No active game session")

    result = current_session.set_enemy_range(
        request.enemy_name, request.range_band, request.engaged_hero
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return current_session.get_state()


# API: Add reinforcement
@app.post("/api/reinforcement")
async def add_reinforcement(request: ReinforcementRequest):
    if not current_session:
        raise HTTPException(status_code=400, detail="No active game session")

    result = current_session.add_reinforcement(request.unit_type, request.is_hero)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return current_session.get_state()


# API: Next round
@app.post("/api/next-round")
async def next_round():
    if not current_session:
        raise HTTPException(status_code=400, detail="No active game session")

    result = current_session.next_round()

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return current_session.get_state()


# API: End battle
@app.post("/api/end-battle")
async def end_battle():
    global current_session

    if not current_session:
        raise HTTPException(status_code=400, detail="No active game session")

    state = current_session.end_battle()
    current_session = None

    return state


# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
