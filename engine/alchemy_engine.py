import random

def attempt_research(rng, resident, recipe, materials_by_id):
    """Return (success: bool, reason: str). Enforces Knowledge Gate."""
    # Knowledge gate: undiscovered material cannot be intentionally used
    for m in recipe.get("materials", []):
        mat = materials_by_id.get(m["material_id"])
        if mat is None:
            return False, f"存在しない素材 {m['material_id']}"
        if mat.get("discovery_status") != "discovered":
            return False, "知識の門: 未発見素材は意図的に使えない"
    required = recipe.get("knowledge_required", [])
    missing = [k for k in required if k not in resident.get("knowledge", [])]
    if missing:
        return False, f"知識不足: {','.join(missing)}"
    skill = resident.get("skills", {}).get("錬金術", 30)
    # stability average
    stabilities = [materials_by_id[m["material_id"]]["stability"] for m in recipe["materials"]]
    avg_stability = sum(stabilities)/len(stabilities) if stabilities else 50
    chance = 0.35 + skill/200 + avg_stability/500  # 0.35-~0.9
    if recipe.get("status") == "known":
        chance += 0.25
    roll = rng.random()
    return (roll < chance), f"roll={roll:.3f} chance={chance:.3f} avg_stability={avg_stability:.1f}"
