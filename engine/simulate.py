#!/usr/bin/env python3
"""Simulate one flask day. Duplicate processing is forbidden."""
import json, sys, random, hashlib
from pathlib import Path
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/"engine"))
from alchemy_engine import attempt_research
from economy_engine import daily_economy

def load(name):
    return json.loads((ROOT/"world"/name).read_text(encoding="utf-8"))
def save(name, data):
    (ROOT/"world"/name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def seed_for(world_seed, flask_date_str):
    h = hashlib.sha256(f"{world_seed}:{flask_date_str}".encode()).hexdigest()
    return int(h[:8], 16)

def next_date(flask_date_str):
    y,m,d = map(int, flask_date_str.split("-"))
    # simple calendar: 30-day months, 12 months
    d+=1
    if d>30: d=1; m+=1
    if m>12: m=1; y+=1
    return f"{y:04d}-{m:02d}-{d:02d}"

def process_day(state, target_date):
    if state.get("last_processed_date") == target_date:
        raise RuntimeError(f"二重実行防止: {target_date} は既に処理済みです")
    # also guard via history file check is done in main

def main():
    state = load("state.json")
    target = state["current_date"]
    # duplicate check
    try:
        process_day(state, target)
    except RuntimeError as e:
        print(str(e)); sys.exit(2)
    # check history for duplicate
    hist_path = ROOT/"world"/"history.jsonl"
    existing = hist_path.read_text(encoding="utf-8") if hist_path.exists() else ""
    if f'"date": "{target}"' in existing:
        print(f"二重実行防止: history に {target} が既にあります"); sys.exit(2)

    seed = seed_for(state["world_seed"], target)
    rng = random.Random(seed)
    residents = load("residents.json")
    materials = load("materials.json")
    materials_by_id = {m["id"]: m for m in materials}
    recipes = load("recipes.json")
    economy = load("economy.json")

    weathers = ["晴れ","朝霧のち晴れ","曇り","小雨（首の雲から）","流れ星の気配"]
    weather = rng.choice(weathers)
    events = [f"天候: {weather}"]

    # resident actions (simple, based on goal/occupation)
    actor = rng.choice([r for r in residents if r["id"]!="res_001"])
    events.append(f"{actor['name']}は「{actor['goal']}」に向けて活動した（{actor['occupation']}）")
    poco = next(r for r in residents if r["id"]=="res_001")
    events.append("ポコは丘から街を観察し、記録小屋で本日の記録を書いた")

    # economy
    eco_events = daily_economy(rng, economy, residents)
    events.extend(eco_events[:3])

    # alchemy research: Luna attempts researching recipe if she has knowledge
    luna = next(r for r in residents if r["id"]=="res_002")
    researching = [r for r in recipes if r["status"] in ("researching","known")]
    recipe = rng.choice(researching)
    success, reason = attempt_research(rng, luna, recipe, materials_by_id)
    exp_id = f"exp_{target.replace('-','')}_001"
    if success:
        events.append(f"錬金実験 {exp_id}: ルナが「{recipe['name']}」の実験に成功（{reason}）")
        # consume 1 of first material from workshop inventory if present, never negative
        for shop in economy["shops"]:
            for item in shop["inventory"]:
                if item["material_id"]==recipe["materials"][0]["material_id"] and item["stock"]>0:
                    item["stock"]-=1; events.append(f"素材消費: {item['material_id']} -1"); break
    else:
        events.append(f"錬金実験 {exp_id}: ルナが「{recipe['name']}」の実験に失敗/進展なし（{reason}）")

    # update state
    state["weather"]=weather
    state["last_processed_date"]=target
    state["last_processed_real_date"]=datetime.now(ZoneInfo("Asia/Tokyo")).date().isoformat()
    nxt = next_date(target)
    state["current_date"]=nxt
    state["current_day_index"]=state.get("current_day_index",1)+1
    state["current_date_display"]=f"フラスコ暦{int(nxt.split('-')[0])}年{int(nxt.split('-')[1])}月{int(nxt.split('-')[2])}日"
    save("state.json", state)
    save("economy.json", economy)

    record={"date":target,"seed":seed,"weather":weather,"events":events,"experiment":{"id":exp_id,"recipe_id":recipe["id"],"success":success,"reason":reason}}
    with hist_path.open("a",encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False)+"\n")
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return record

if __name__=="__main__":
    main()
