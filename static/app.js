/**
 * Fantasy Helper Web UI
 */

let gameState = null;
let selectedHeroForAttack = null;
let selectedEnemyForAttack = null;
let selectedEnemyForRange = null;
let selectedRange = null;

const API_BASE = "/api";

// Load and display version
async function loadVersion() {
    try {
        const response = await fetch(`${API_BASE}/version`);
        if (response.ok) {
            const data = await response.json();
            document.getElementById("versionDisplay").textContent = data.version;
        }
    } catch (_) {}
}

// Initialize - reconnect to active session if one exists
document.addEventListener("DOMContentLoaded", async () => {
    loadVersion();
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

// Start a new game (show encounter builder)
async function startGame() {
    await showEncounterBuilder();
}

function showStartScreen() {
    const startScreen = document.getElementById("startScreen");
    startScreen.classList.add("show");
}

async function showEncounterBuilder() {
    try {
        const response = await fetch(`${API_BASE}/encounter-config`);
        if (!response.ok) throw new Error("Failed to load encounter config");

        const config = await response.json();
        
        // Initialize quantities
        window.heroQuantities = {};
        window.enemyQuantities = {};
        config.heroes.forEach(h => window.heroQuantities[h.id] = 0);
        config.enemies.forEach(e => window.enemyQuantities[e.id] = 0);

        // Create hero quantity controls
        const heroDiv = document.getElementById("heroQuantities");
        heroDiv.innerHTML = "";
        config.heroes.forEach((hero) => {
            const container = document.createElement("div");
            container.style.display = "flex";
            container.style.alignItems = "center";
            container.style.justifyContent = "space-between";
            container.style.marginBottom = "10px";
            container.style.padding = "8px";
            container.style.backgroundColor = "#2a2a2a";
            container.style.borderRadius = "4px";

            const label = document.createElement("span");
            label.textContent = `${hero.name}`;
            label.style.flex = "1";

            const controls = document.createElement("div");
            controls.style.display = "flex";
            controls.style.alignItems = "center";
            controls.style.gap = "5px";

            const minusBtn = document.createElement("button");
            minusBtn.textContent = "−";
            minusBtn.style.width = "30px";
            minusBtn.style.padding = "5px";
            minusBtn.onclick = () => {
                if (window.heroQuantities[hero.id] > 0) {
                    window.heroQuantities[hero.id]--;
                    display.textContent = window.heroQuantities[hero.id];
                }
            };

            const display = document.createElement("span");
            display.textContent = "0";
            display.style.width = "30px";
            display.style.textAlign = "center";

            const plusBtn = document.createElement("button");
            plusBtn.textContent = "+";
            plusBtn.style.width = "30px";
            plusBtn.style.padding = "5px";
            plusBtn.onclick = () => {
                window.heroQuantities[hero.id]++;
                display.textContent = window.heroQuantities[hero.id];
            };

            controls.appendChild(minusBtn);
            controls.appendChild(display);
            controls.appendChild(plusBtn);

            container.appendChild(label);
            container.appendChild(controls);
            heroDiv.appendChild(container);
        });

        // Create enemy quantity controls
        const enemyDiv = document.getElementById("enemyQuantities");
        enemyDiv.innerHTML = "";
        config.enemies.forEach((enemy) => {
            const container = document.createElement("div");
            container.style.display = "flex";
            container.style.alignItems = "center";
            container.style.justifyContent = "space-between";
            container.style.marginBottom = "10px";
            container.style.padding = "8px";
            container.style.backgroundColor = "#2a2a2a";
            container.style.borderRadius = "4px";

            const label = document.createElement("span");
            label.textContent = `${enemy.name}`;
            label.style.flex = "1";

            const controls = document.createElement("div");
            controls.style.display = "flex";
            controls.style.alignItems = "center";
            controls.style.gap = "5px";

            const minusBtn = document.createElement("button");
            minusBtn.textContent = "−";
            minusBtn.style.width = "30px";
            minusBtn.style.padding = "5px";
            minusBtn.onclick = () => {
                if (window.enemyQuantities[enemy.id] > 0) {
                    window.enemyQuantities[enemy.id]--;
                    display.textContent = window.enemyQuantities[enemy.id];
                }
            };

            const display = document.createElement("span");
            display.textContent = "0";
            display.style.width = "30px";
            display.style.textAlign = "center";

            const plusBtn = document.createElement("button");
            plusBtn.textContent = "+";
            plusBtn.style.width = "30px";
            plusBtn.style.padding = "5px";
            plusBtn.onclick = () => {
                window.enemyQuantities[enemy.id]++;
                display.textContent = window.enemyQuantities[enemy.id];
            };

            controls.appendChild(minusBtn);
            controls.appendChild(display);
            controls.appendChild(plusBtn);

            container.appendChild(label);
            container.appendChild(controls);
            enemyDiv.appendChild(container);
        });

        document.getElementById("startScreen").classList.remove("show");
        document.getElementById("encounterBuilderModal").classList.add("show");
    } catch (error) {
        console.error("Encounter builder error:", error);
        alert("Failed to load encounter options");
    }
}

async function startCustomEncounter() {
    const totalHeroes = Object.values(window.heroQuantities).reduce((a, b) => a + b, 0);
    const totalEnemies = Object.values(window.enemyQuantities).reduce((a, b) => a + b, 0);

    if (totalHeroes === 0 || totalEnemies === 0) {
        alert("Select at least one hero and one enemy");
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/encounter-custom`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                hero_quantities: window.heroQuantities,
                enemy_quantities: window.enemyQuantities,
            }),
        });

        if (!response.ok) throw new Error("Failed to start encounter");

        gameState = await response.json();
        closeModal("encounterBuilderModal");
        showGameUI();
        updateDisplay();
    } catch (error) {
        console.error("Start custom encounter error:", error);
        alert("Failed to start battle");
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

    // Check if unit has acted this turn
    const hasActed =
        (type === "hero" && gameState.acted.includes(unit.name)) ||
        (type === "enemy" && gameState.enemy_acted.includes(unit.name));

    if (hasActed) {
        div.classList.add("acted");
    }

    const nameDiv = document.createElement("div");
    nameDiv.className = "unit-name";
    nameDiv.textContent = unit.name;
    if (hasActed) {
        nameDiv.textContent += " ✓ ACTED";
    }
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
            <span class="stat-label">SPD:</span>
            <span class="stat-value">${unit.spd}</span>
        </div>
        <div class="stat">
            <span class="stat-label">WPN:</span>
            <span class="stat-value">${unit.weapon.name} (${unit.weapon.damage}, pen ${unit.weapon.pen})</span>
        </div>
        ${unit.secondary_weapon ? `
        <div class="stat">
            <span class="stat-label">WPN2:</span>
            <span class="stat-value">${unit.secondary_weapon.name} (${unit.secondary_weapon.damage}, pen ${unit.secondary_weapon.pen})</span>
        </div>
        ` : ''}
        ${unit.spells && unit.spells.length > 0 ? `
        <div class="stat">
            <span class="stat-label">SPELLS:</span>
            <span class="stat-value">${unit.spells.map(s => `${s.name} (${s.damage}, pen ${s.pen})${s.area ? ' [AREA]' : ''}`).join(' | ')}</span>
        </div>
        ` : ''}
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
    document.getElementById("battleStats").textContent = `Rounds: ${gameState.round}`;

    // Show final status
    const finalStatus = document.getElementById("finalStatus");
    finalStatus.innerHTML = "";

    // Heroes
    const heroHeader = document.createElement("div");
    heroHeader.style.fontWeight = "bold";
    heroHeader.style.color = "#4a9eff";
    heroHeader.style.marginBottom = "8px";
    heroHeader.textContent = "Heroes:";
    finalStatus.appendChild(heroHeader);

    gameState.heroes.forEach((hero) => {
        const status = document.createElement("div");
        status.style.marginBottom = "4px";
        status.style.color = hero.alive ? "#4ade80" : "#ff6b6b";
        status.textContent = `  ${hero.name}: HP ${hero.hp}/${hero.max_hp} | Dmg: ${hero.damage_done}`;
        finalStatus.appendChild(status);
    });

    const enemyHeader = document.createElement("div");
    enemyHeader.style.fontWeight = "bold";
    enemyHeader.style.color = "#ff6b6b";
    enemyHeader.style.marginTop = "12px";
    enemyHeader.style.marginBottom = "8px";
    enemyHeader.textContent = "Enemies:";
    finalStatus.appendChild(enemyHeader);

    gameState.enemies.forEach((enemy) => {
        const status = document.createElement("div");
        status.style.marginBottom = "4px";
        status.style.color = enemy.alive ? "#4ade80" : "#888";
        status.textContent = `  ${enemy.name}: HP ${enemy.hp}/${enemy.max_hp}`;
        finalStatus.appendChild(status);
    });

    // Show combat log
    const logDiv = document.getElementById("endBattleLog");
    logDiv.innerHTML = "";

    gameState.log.forEach((entry) => {
        const entryDiv = document.createElement("div");
        entryDiv.style.marginBottom = "3px";

        if (entry.includes("hits")) {
            entryDiv.style.color = "#4ade80";
        } else if (entry.includes("misses")) {
            entryDiv.style.color = "#facc15";
        } else if (entry.includes("defeated") || entry.includes("VICTORY")) {
            entryDiv.style.color = "#ff6b6b";
        } else {
            entryDiv.style.color = "#aaa";
        }

        entryDiv.textContent = entry;
        logDiv.appendChild(entryDiv);
    });

    // Scroll to bottom
    logDiv.scrollTop = logDiv.scrollHeight;
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
    if (hero.weapon.name === "MM") {
        showSpellSelection();
    } else {
        showEnemySelection("melee");
    }
}

function showSpellSelection() {
    document.getElementById("spellSelectModal").classList.add("show");
}

function showEnemySelection(attackType = "melee") {
    const enemyList = document.getElementById("enemyList");
    enemyList.innerHTML = "";

    let availableEnemies = gameState.enemies.filter((e) => e.alive);
    
    // Filter by range requirement
    if (attackType === "melee") {
        availableEnemies = availableEnemies.filter((e) => e.rng === "MEL");
        
        // Heroes can ONLY attack enemies they're engaged with
        const heroIsEngaged = gameState.enemies.some((e) => e.engaged_target === selectedHeroForAttack.name);
        if (!heroIsEngaged) {
            // Hero not engaged - no melee attacks allowed
            const msg = document.createElement("div");
            msg.style.padding = "10px";
            msg.style.color = "#ff6b6b";
            msg.textContent = `${selectedHeroForAttack.name} is not in melee - cannot attack`;
            enemyList.appendChild(msg);
            document.getElementById("enemyModalTitle").textContent = "Select Enemy (MEL Range)";
            document.getElementById("enemySelectModal").classList.add("show");
            return;
        }
        
        // Hero IS engaged - only allow attacking engaged enemies
        availableEnemies = availableEnemies.filter((e) => e.engaged_target === selectedHeroForAttack.name);
    } else if (attackType === "spell") {
        availableEnemies = availableEnemies.filter((e) => e.rng === "OOM");
    }

    if (availableEnemies.length === 0) {
        const msg = document.createElement("div");
        msg.style.padding = "10px";
        msg.style.color = "#ff6b6b";
        if (attackType === "melee") {
            msg.textContent = `Only enemies engaged with ${selectedHeroForAttack.name} can be attacked`;
        } else if (attackType === "spell") {
            msg.textContent = "No enemies out of melee (OOM)";
        }
        enemyList.appendChild(msg);
    } else {
        availableEnemies.forEach((enemy) => {
            const btn = document.createElement("button");
            btn.className = "option-btn";
            btn.textContent = `${enemy.name} (HP: ${enemy.hp}/${enemy.max_hp}, ${enemy.rng})`;
            btn.onclick = () => selectEnemyForAttack(enemy);
            enemyList.appendChild(btn);
        });
    }

    let title = "Select Enemy";
    if (attackType === "melee") {
        title += " (MEL Range)";
    } else if (attackType === "spell") {
        title += " (OOM Range)";
    }
    
    document.getElementById("enemyModalTitle").textContent = title;
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
    window.selectedSpellIndex = spellIndex;

    // Fireball (index 1) is area spell - multi-select
    if (spellIndex === 1) {
        showAreaSpellTargetSelection();
    } else {
        // Magic Missile (index 0) - single target
        selectedEnemyForAttack = null;
        showEnemySelection("spell");
    }
}

function showAreaSpellTargetSelection() {
    const modal = document.createElement("div");
    modal.className = "modal show";
    modal.id = "areaSpellModal";
    modal.style.zIndex = "1000";

    const content = document.createElement("div");
    content.className = "modal-content";

    const title = document.createElement("h2");
    title.textContent = "Select Targets for Fireball";
    title.style.color = "#4a9eff";
    title.style.marginBottom = "15px";
    content.appendChild(title);

    const enemyList = document.createElement("div");
    enemyList.style.marginBottom = "15px";

    const availableEnemies = gameState.enemies.filter((e) => e.alive && e.rng === "OOM");
    const checkboxes = {};

    if (availableEnemies.length === 0) {
        const msg = document.createElement("div");
        msg.style.color = "#ff6b6b";
        msg.textContent = "No OOM targets available";
        enemyList.appendChild(msg);
    } else {
        availableEnemies.forEach((enemy) => {
            const label = document.createElement("label");
            label.style.display = "block";
            label.style.marginBottom = "8px";
            label.style.cursor = "pointer";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.value = enemy.name;
            checkbox.style.marginRight = "8px";
            checkboxes[enemy.name] = checkbox;

            label.appendChild(checkbox);
            label.appendChild(
                document.createTextNode(
                    `${enemy.name} (HP: ${enemy.hp}/${enemy.max_hp})`
                )
            );
            enemyList.appendChild(label);
        });
    }

    content.appendChild(enemyList);

    const buttonDiv = document.createElement("div");
    buttonDiv.style.marginTop = "20px";
    buttonDiv.style.display = "grid";
    buttonDiv.style.gridTemplateColumns = "1fr 1fr";
    buttonDiv.style.gap = "10px";

    const confirmBtn = document.createElement("button");
    confirmBtn.className = "primary";
    confirmBtn.textContent = "Confirm";
    confirmBtn.onclick = async () => {
        const selected = Object.keys(checkboxes)
            .filter((name) => checkboxes[name].checked)
            .map((name) => name);

        if (selected.length === 0) {
            alert("Select at least one target");
            return;
        }

        const parent = modal.parentElement;
        if (parent) parent.removeChild(modal);
        await executeAreaAttack(selected);
    };
    buttonDiv.appendChild(confirmBtn);

    const cancelBtn = document.createElement("button");
    cancelBtn.textContent = "Cancel";
    cancelBtn.onclick = () => {
        const parent = modal.parentElement;
        if (parent) parent.removeChild(modal);
    };
    buttonDiv.appendChild(cancelBtn);

    content.appendChild(buttonDiv);
    modal.appendChild(content);
    document.body.appendChild(modal);
}

async function executeAreaAttack(targetNames) {
    if (!selectedHeroForAttack) return;

    try {
        const payload = {
            hero_name: selectedHeroForAttack.name,
            enemy_names: targetNames,
            spell_index: window.selectedSpellIndex,
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
        console.error("Area attack error:", error);
        alert("Failed to execute area spell");
    }
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
