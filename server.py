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
from models.spell import Spell
from models.enemy import Enemy
from models.enums import RangeBand
from encounters.builder import build_encounter
from game_session import GameSession
from data_loader import load_heroes_from_json, load_enemies_from_json

import os

VERSION = "0.1.0"

app = FastAPI()

# Global session (single active game)
current_session: Optional[GameSession] = None


# Pydantic models for API
class NewEncounterRequest(BaseModel):
    pass


class HeroAttackRequest(BaseModel):
    hero_name: str
    enemy_name: Optional[str] = None
    enemy_names: Optional[list[str]] = None
    spell_index: Optional[int] = None


class EncounterConfigRequest(BaseModel):
    pass


class EncounterCustomRequest(BaseModel):
    hero_quantities: dict[str, int]
    enemy_quantities: dict[str, int]


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


# API: Get encounter configuration (available heroes and enemies)
@app.get("/api/encounter-config")
async def get_encounter_config():
    heroes = load_heroes_from_json()
    enemies = load_enemies_from_json()
    
    def serialize_unit(unit):
        return {
            "id": unit.name.lower().replace(" ", "_"),
            "name": unit.name,
            "hp": unit.max_hp,
            "arm": unit.arm,
            "weapon": unit.weapon.name if unit.weapon else None,
        }
    
    return {
        "heroes": [serialize_unit(h) for h in heroes],
        "enemies": [serialize_unit(e) for e in enemies],
    }


# API: Start custom encounter
@app.post("/api/encounter-custom")
async def encounter_custom(request: EncounterCustomRequest):
    global current_session
    
    import copy
    
    all_heroes_templates = load_heroes_from_json()
    all_enemies_templates = load_enemies_from_json()
    
    selected_heroes = []
    for hero_id, quantity in request.hero_quantities.items():
        if quantity > 0:
            template = next((h for h in all_heroes_templates if h.name.lower().replace(" ", "_") == hero_id), None)
            if template:
                for i in range(quantity):
                    # Deep copy the template to create a new instance
                    hero_copy = copy.deepcopy(template)
                    if quantity > 1:
                        hero_copy.name = f"{template.name} #{i+1}"
                    selected_heroes.append(hero_copy)
    
    selected_enemies = []
    for enemy_id, quantity in request.enemy_quantities.items():
        if quantity > 0:
            template = next((e for e in all_enemies_templates if e.name.lower().replace(" ", "_") == enemy_id), None)
            if template:
                for i in range(quantity):
                    # Deep copy the template to create a new instance
                    enemy_copy = copy.deepcopy(template)
                    if quantity > 1:
                        enemy_copy.name = f"{template.name} #{i+1}"
                    selected_enemies.append(enemy_copy)
    
    if not selected_heroes or not selected_enemies:
        raise HTTPException(status_code=400, detail="Must select at least one hero and one enemy")
    
    current_session = GameSession(selected_heroes, selected_enemies)
    return current_session.get_state()


# API: Create new encounter
@app.post("/api/new-encounter")
async def new_encounter(request: NewEncounterRequest):
    global current_session

    # Build default hero party
    fighter_sword = Weapon("LSWD", "1d8", 2)
    
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
            secondary_weapon=None,
            spells=[],
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
            spells=[
                Spell("Magic Missile", "1d8", 2, area=False),
                Spell("Fireball", "2d8", 0, area=True),
            ],
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
            spells=[],
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
            spells=[],
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


# API: Get version
@app.get("/api/version")
async def get_version():
    return {"version": VERSION}


# API: Hero action
@app.post("/api/hero-attack")
async def hero_attack(request: HeroAttackRequest):
    if not current_session:
        raise HTTPException(status_code=400, detail="No active game session")

    result = current_session.hero_attack(
        request.hero_name,
        enemy_name=request.enemy_name,
        enemy_names=request.enemy_names,
        spell_index=request.spell_index,
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
