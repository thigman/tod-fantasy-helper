/**
 * Fantasy Helper Web UI
 */

let gameState = null;
let selectedHeroForAttack = null;
let selectedEnemyForAttack = null;
let selectedEnemyForRange = null;
let selectedRange = null;

const API_BASE = "/api";

// Initialize - reconnect to active session if one exists
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch(`${API_BASE}/game-state`);
        if (response.ok) {
            gameState = await response.json();
            if (!gameState.battle_over) {
                showGameUI();
                updateDisplay();
                return;
            }
        }
    } catch (_) {}
    // No active session - show start screen
});

// Start a new game
async function startGame() {
    try {
        const response = await fetch(`${API_BASE}/new-encounter`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({}),
        });

        if (!response.ok) throw new Error("Failed to start game");

        gameState = await response.json();
        showGameUI();
        updateDisplay();
    } catch (error) {
        console.error("Start game error:", error);
        alert("Failed to start game");
    }
}

// Show game UI
function showGameUI() {
    document.getElementById("startScreen").classList.remove("show");
    document.getElementById("mainActions").style.display = "grid";
    document.getElementById("mainContent").style.display = "grid";
}

// Hide game UI
function hideGameUI() {
    document.getElementById("startScreen").classList.add("show");
    document.getElementById("mainActions").style.display = "none";
    document.getElementById("mainContent").style.display = "none";
}

// Update display from game state
function updateDisplay() {
    if (!gameState) return;

    // Update round info
    document.getElementById("roundInfo").textContent = `Round ${gameState.round}`;

    // Update heroes
    const heroesList = document.getElementById("heroesList");
    heroesList.innerHTML = "";
    gameState.heroes.forEach((hero) => {
        heroesList.appendChild(createUnitElement(hero, "hero"));
    });

    // Update enemies
    const enemiesList = document.getElementById("enemiesList");
    enemiesList.innerHTML = "";
    gameState.enemies.forEach((enemy) => {
        enemiesList.appendChild(createUnitElement(enemy, "enemy"));
    });

    // Update combat log
    updateCombatLog();

    // Check if battle is over
    if (gameState.battle_over) {
        showBattleOver();
    }
}

// Create unit element
function createUnitElement(unit, type) {
    const div = document.createElement("div");
    div.className = `unit ${type}`;
    if (!unit.alive) {
        div.classList.add("dead");
    }

    const nameDiv = document.createElement("div");
    nameDiv.className = "unit-name";
    nameDiv.textContent = unit.name;
    div.appendChild(nameDiv);

    const statsDiv = document.createElement("div");
    statsDiv.className = "unit-stats";

    const hpPercent = (unit.hp / unit.max_hp) * 100;
    statsDiv.innerHTML = `
        <div class="stat">
            <span class="stat-label">HP:</span>
            <span class="stat-value">${unit.hp}/${unit.max_hp}</span>
        </div>
        <div class="stat">
            <span class="stat-label">ARM:</span>
            <span class="stat-value">${unit.arm}</span>
        </div>
        <div class="stat">
            <span class="stat-label">STR:</span>
            <span class="stat-value">${unit.str}</span>
        </div>
        <div class="stat">
            <span class="stat-label">DEX:</span>
            <span class="stat-value">${unit.dex}</span>
        </div>
        <div class="stat">
            <span class="stat-label">MS:</span>
            <span class="stat-value">${unit.ms}</span>
        </div>
        <div class="stat">
            <span class="stat-label">WPN:</span>
            <span class="stat-value">${unit.weapon}</span>
        </div>
    `;
    div.appendChild(statsDiv);

    // HP bar
    const hpBar = document.createElement("div");
    hpBar.className = "hp-bar";
    const hpFill = document.createElement("div");
    hpFill.className = "hp-fill";
    if (hpPercent < 50) hpFill.classList.add("damaged");
    hpFill.style.width = `${Math.max(0, hpPercent)}%`;
    hpBar.appendChild(hpFill);
    div.appendChild(hpBar);

    // Tactical info for enemies
    if (type === "enemy") {
        const tacticalDiv = document.createElement("div");
        tacticalDiv.className = "tactical";
        let tacticalInfo = `${unit.rng}`;
        if (unit.engaged_target) {
            tacticalInfo += ` | Engaging ${unit.engaged_target}`;
        } else if (unit.focus_target) {
            tacticalInfo += ` | Focusing ${unit.focus_target}`;
        }
        if (unit.morale_state !== "STEADY") {
            tacticalInfo += ` | ${unit.morale_state}`;
        }
        tacticalDiv.textContent = tacticalInfo;
        div.appendChild(tacticalDiv);
    }

    return div;
}

// Update combat log
function updateCombatLog() {
    const logDiv = document.getElementById("combatLog");
    logDiv.innerHTML = "";

    gameState.log.forEach((entry) => {
        const entryDiv = document.createElement("div");
        entryDiv.className = "log-entry";

        if (entry.includes("hits")) {
            entryDiv.classList.add("hit");
        } else if (entry.includes("misses")) {
            entryDiv.classList.add("miss");
        } else if (entry.includes("defeated")) {
            entryDiv.classList.add("damage");
        }

        entryDiv.textContent = entry;
        logDiv.appendChild(entryDiv);
    });

    // Scroll to bottom
    logDiv.scrollTop = logDiv.scrollHeight;
}

// Show battle over screen
function showBattleOver() {
    const screen = document.getElementById("battleOverScreen");
    screen.classList.add("show");

    document.getElementById("battleResult").textContent = gameState.battle_result;

    const stats = `Rounds: ${gameState.round}`;
    document.getElementById("battleStats").textContent = stats;
}

// Modal functions
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove("show");
}

// Hero Attack Flow
async function performHeroAttack() {
    const available = gameState.heroes.filter((h) => h.alive && !gameState.acted.includes(h.name));

    if (available.length === 0) {
        alert("No available heroes");
        return;
    }

    showHeroSelection(available);
}

function showHeroSelection(heroes) {
    const heroList = document.getElementById("heroList");
    heroList.innerHTML = "";

    heroes.forEach((hero) => {
        const btn = document.createElement("button");
        btn.className = "option-btn";
        btn.textContent = `${hero.name} (HP: ${hero.hp}/${hero.max_hp})`;
        btn.onclick = () => selectHeroForAttack(hero);
        heroList.appendChild(btn);
    });

    document.getElementById("heroAttackModal").classList.add("show");
}

function selectHeroForAttack(hero) {
    selectedHeroForAttack = hero;
    closeModal("heroAttackModal");

    // If wizard, show spell selection. Otherwise show enemy selection
    if (hero.weapon === "MM") {
        showSpellSelection();
    } else {
        showEnemySelection("for attack");
    }
}

function showSpellSelection() {
    document.getElementById("spellSelectModal").classList.add("show");
}

function showEnemySelection(context = "") {
    const enemyList = document.getElementById("enemyList");
    enemyList.innerHTML = "";

    const availableEnemies = gameState.enemies.filter((e) => e.alive);

    availableEnemies.forEach((enemy) => {
        const btn = document.createElement("button");
        btn.className = "option-btn";
        btn.textContent = `${enemy.name} (HP: ${enemy.hp}/${enemy.max_hp}, ${enemy.rng})`;
        btn.onclick = () => selectEnemyForAttack(enemy);
        enemyList.appendChild(btn);
    });

    document.getElementById("enemyModalTitle").textContent = `Select Enemy ${context}`;
    document.getElementById("enemySelectModal").classList.add("show");
}

function selectEnemyForAttack(enemy) {
    selectedEnemyForAttack = enemy;
    closeModal("enemySelectModal");

    if (selectedHeroForAttack && selectedEnemyForAttack) {
        executeAttack();
    }
}

async function castSpell(spellIndex) {
    closeModal("spellSelectModal");
    selectedEnemyForAttack = null;
    showEnemySelection("for spell");

    // Store spell index for later use
    window.selectedSpellIndex = spellIndex;
}

async function executeAttack() {
    if (!selectedHeroForAttack || !selectedEnemyForAttack) return;

    try {
        const payload = {
            hero_name: selectedHeroForAttack.name,
            enemy_name: selectedEnemyForAttack.name,
            spell_index: window.selectedSpellIndex ?? null,
        };

        const response = await fetch(`${API_BASE}/hero-attack`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const error = await response.json();
            alert("Attack failed: " + error.detail);
            return;
        }

        gameState = await response.json();
        updateDisplay();

        selectedHeroForAttack = null;
        selectedEnemyForAttack = null;
        window.selectedSpellIndex = null;
    } catch (error) {
        console.error("Attack error:", error);
        alert("Failed to execute attack");
    }
}

// Enemy Turn
async function performEnemyTurn() {
    try {
        const response = await fetch(`${API_BASE}/enemy-turn`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            const error = await response.json();
            alert("Enemy turn failed: " + error.detail);
            return;
        }

        gameState = await response.json();
        updateDisplay();
    } catch (error) {
        console.error("Enemy turn error:", error);
        alert("Failed to execute enemy turn");
    }
}

// Set Enemy Range
function showSetEnemyRange() {
    const rangeEnemyList = document.getElementById("rangeEnemyList");
    rangeEnemyList.innerHTML = "";

    const enemies = gameState.enemies.filter((e) => e.alive);

    enemies.forEach((enemy) => {
        const btn = document.createElement("button");
        btn.className = "option-btn";
        btn.textContent = `${enemy.name} (${enemy.rng})`;
        btn.onclick = () => selectEnemyForRange(enemy);
        rangeEnemyList.appendChild(btn);
    });

    document.getElementById("setRangeModal").classList.add("show");
}

function selectEnemyForRange(enemy) {
    selectedEnemyForRange = enemy;
    closeModal("setRangeModal");
    showRangeSelection();
}

function showRangeSelection() {
    document.getElementById("rangeSelectionModal").classList.add("show");
}

async function selectRange(rangeBand) {
    closeModal("rangeSelectionModal");
    selectedRange = rangeBand;

    if (rangeBand === "MEL") {
        showEngagedHeroSelection();
    } else {
        await applyRangeChange(null);
    }
}

function showEngagedHeroSelection() {
    const engagedHeroList = document.getElementById("engagedHeroList");
    engagedHeroList.innerHTML = "";

    const heroes = gameState.heroes.filter((h) => h.alive);

    heroes.forEach((hero) => {
        const btn = document.createElement("button");
        btn.className = "option-btn";
        btn.textContent = hero.name;
        btn.onclick = () => selectEngagedHero(hero);
        engagedHeroList.appendChild(btn);
    });

    document.getElementById("engagedHeroModal").classList.add("show");
}

async function selectEngagedHero(hero) {
    closeModal("engagedHeroModal");
    await applyRangeChange(hero.name);
}

async function applyRangeChange(engagedHero) {
    if (!selectedEnemyForRange) return;

    try {
        const payload = {
            enemy_name: selectedEnemyForRange.name,
            range_band: selectedRange,
            engaged_hero: engagedHero,
        };

        const response = await fetch(`${API_BASE}/set-enemy-range`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const error = await response.json();
            alert("Set range failed: " + error.detail);
            return;
        }

        gameState = await response.json();
        updateDisplay();

        selectedEnemyForRange = null;
        selectedRange = null;
    } catch (error) {
        console.error("Set range error:", error);
        alert("Failed to set enemy range");
    }
}

// Reinforcements
function showReinforcements() {
    document.getElementById("reinforcementsModal").classList.add("show");
}

async function addReinforcement(unitType, isHero) {
    closeModal("reinforcementsModal");

    try {
        const payload = {
            unit_type: unitType,
            is_hero: isHero,
        };

        const response = await fetch(`${API_BASE}/reinforcement`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const error = await response.json();
            alert("Reinforcement failed: " + error.detail);
            return;
        }

        gameState = await response.json();
        updateDisplay();
    } catch (error) {
        console.error("Reinforcement error:", error);
        alert("Failed to add reinforcement");
    }
}

// Next Round
async function nextRound() {
    try {
        const response = await fetch(`${API_BASE}/next-round`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            const error = await response.json();
            alert("Next round failed: " + error.detail);
            return;
        }

        gameState = await response.json();
        updateDisplay();
    } catch (error) {
        console.error("Next round error:", error);
        alert("Failed to advance to next round");
    }
}

// End Battle
async function endBattle() {
    if (!confirm("End battle?")) return;

    try {
        const response = await fetch(`${API_BASE}/end-battle`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) throw new Error("Failed to end battle");

        gameState = await response.json();
        showBattleOver();
    } catch (error) {
        console.error("End battle error:", error);
        alert("Failed to end battle");
    }
}
