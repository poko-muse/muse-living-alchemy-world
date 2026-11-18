#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def load(n): return json.loads((ROOT/"world"/n).read_text(encoding="utf-8"))
def validate():
    errors=[]
    state=load("state.json"); residents=load("residents.json"); materials=load("materials.json"); recipes=load("recipes.json"); economy=load("economy.json"); geo=load("geography.json")
    mat_ids={m["id"] for m in materials}; mat_by={m["id"]:m for m in materials}; res_ids={r["id"] for r in residents}
    # population consistency
    if state.get("population")!=len(residents): errors.append(f"人口不一致: state={state.get('population')} residents={len(residents)}")
    # resident relationships reference check (only res_ keys)
    for r in residents:
        for k in r.get("relationships",{}):
            if k.startswith("res_") and k not in res_ids: errors.append(f"存在しない住民参照: {r['id']} -> {k}")
    # economy: stock/price negative, material exists, owner exists
    for shop in economy.get("shops",[]):
        if shop.get("owner_resident_id") not in res_ids: errors.append(f"存在しない店主: {shop['id']}")
        for item in shop.get("inventory",[]):
            if item["material_id"] not in mat_ids: errors.append(f"存在しない素材(在庫): {item['material_id']}")
            if item["stock"]<0: errors.append(f"在庫が負値: {shop['id']} {item['material_id']}")
            if item["price"]<0: errors.append(f"価格が負値: {shop['id']} {item['material_id']}")
    for r in residents:
        if r.get("assets",0)<0: errors.append(f"資産が負値: {r['id']}")
    # recipes: known/researching must not use undiscovered; hypothesis may reference but flagged
    for rec in recipes:
        for m in rec.get("materials",[]):
            if m["material_id"] not in mat_ids: errors.append(f"存在しない素材(レシピ): {rec['id']} {m['material_id']}")
            elif rec["status"] in ("known","researching") and mat_by[m["material_id"]]["discovery_status"]!="discovered":
                errors.append(f"未発見素材を既知/研究中レシピで使用: {rec['id']} {m['material_id']}")
    # history duplicate dates
    hist=(ROOT/"world"/"history.jsonl").read_text(encoding="utf-8").strip().splitlines() if (ROOT/"world"/"history.jsonl").exists() else []
    seen=set()
    for line in hist:
        if not line.strip(): continue
        d=json.loads(line).get("date")
        if d in seen: errors.append(f"日付重複: {d}")
        seen.add(d)
    return errors

if __name__=="__main__":
    errs=validate()
    if errs:
        print("VALIDATE FAILED"); [print("-",e) for e in errs]; sys.exit(1)
    print("VALIDATE OK")
