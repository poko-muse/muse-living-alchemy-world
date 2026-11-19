#!/usr/bin/env python3
"""フラスカリア錬金術図鑑の原稿を編纂する。

正式状態（world/*.json）と履歴（world/history.jsonl）、stories/ を読み、
指定期間の Markdown 原稿を生成する。

原則（AGENTS.md / docs/monetization_plan.md）:
- 生成前に engine/validate.py の検証を行い、NG なら原稿を生成しない。
- 未発見素材は性質を捏造せず「未発見」として存在だけを記載する。
- 実験記録は history.jsonl の experiment 実績のみを使う。記録にない成功は書かない。
- 出力は決定的にする（生成日時や乱数を埋め込まない）。同じ入力からは同じ原稿が出る。

使い方:
  python3 engine/compile_encyclopedia.py \
    --from 0001-01-01 --to 0001-01-30 \
    --out books/encyclopedia_vol1.md --edition "Vol.1"
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))

from validate import validate  # noqa: E402

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RECIPE_STATUS = {
    "known": "既知",
    "researching": "研究中",
    "hypothesis": "仮説（未検証）",
}


def load(name):
    return json.loads((ROOT / "world" / name).read_text(encoding="utf-8"))


def load_history():
    path = ROOT / "world" / "history.jsonl"
    entries = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entries.append(json.loads(line))
    entries.sort(key=lambda e: e["date"])
    return entries


def display_date(flask_date):
    """'0001-01-02' -> 'フラスコ暦1年1月2日'"""
    dt = datetime.strptime(flask_date, "%Y-%m-%d")
    return f"フラスコ暦{dt.year}年{dt.month}月{dt.day}日"


def check_date(value, option):
    if not DATE_RE.match(value):
        raise SystemExit(f"{option} の形式が不正です（YYYY-MM-DD）: {value}")
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise SystemExit(f"{option} が日付として不正です: {value}")
    return value


def story_index(date_from, date_to):
    """対象期間の stories/ を索引化する（ファイル名の日付で判定）。"""
    items = []
    stories_dir = ROOT / "stories"
    if not stories_dir.exists():
        return items
    for path in sorted(stories_dir.rglob("*.md")):
        name = path.name
        story_date = None
        m = re.match(r"^(\d{4}-\d{2}-\d{2})", name)
        if m:
            story_date = m.group(1)
        else:
            m = re.match(r"^exp_(\d{4})(\d{2})(\d{2})", name)
            if m:
                story_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        if story_date is None or not (date_from <= story_date <= date_to):
            continue
        title = ""
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        rel = path.relative_to(ROOT).as_posix()
        items.append((story_date, rel, title))
    items.sort(key=lambda x: (x[0], x[1]))
    return items


def build(args):
    state = load("state.json")
    alchemy = load("alchemy.json")
    materials = load("materials.json")
    recipes = load("recipes.json")
    residents = load("residents.json")
    geography = load("geography.json")
    economy = load("economy.json")
    history = load_history()

    mat_by_id = {m["id"]: m for m in materials}
    res_by_id = {r["id"]: r for r in residents}
    rec_by_id = {r["id"]: r for r in recipes}
    period_history = [h for h in history if args.date_from <= h["date"] <= args.date_to]

    lines = []
    add = lines.append

    # ---- タイトルページ ----
    add(f"# フラスカリア錬金術図鑑 {args.edition}")
    add("")
    add("MUSE LIVING ALCHEMY WORLD — 公式図鑑（書籍版）原稿")
    add("")
    add(f"- 対象期間: {display_date(args.date_from)}（{args.date_from}）〜 {display_date(args.date_to)}（{args.date_to}）")
    add(f"- 世界名: {state.get('world_name', 'フラスカリア')}")
    add("- 編者: ポコ（界守／記録者）")
    add("- 原稿の出所: 世界の正式状態 `world/*.json` と履歴 `world/history.jsonl` から自動編纂")
    add("")
    add("> これは架空世界の創作プロジェクトの図鑑です。登場する世界・住民・錬金術はすべて架空です。")
    add("")

    # ---- 本書について ----
    add("## 本書について")
    add("")
    add("本書は、フラスコの世界フラスカリアで実際に記録された出来事と知識だけを編んだ図鑑である。")
    add("編纂にあたっては次の原則を守っている。")
    add("")
    add("- 素材・住民・地理などの記述は、世界の正式状態（構造化データ）に基づく。")
    add("- 実験の成否は履歴に残された実験実績のとおりに記す。成功も失敗も、記録どおりに載せる。")
    add("- 未発見の素材については、性質や用途を推測で書かず、「未発見」として存在だけを示す（知識の門の法則）。")
    add("- 仮説と、再現性が確認された発見は、はっきり区別して記す。")
    add("")

    # ---- 第1章 世界と地理 ----
    add("## 第1章 世界と地理")
    add("")
    add(f"### 器としての世界")
    add("")
    add(geography.get("container", ""))
    add("")
    add(f"気候: {geography.get('climate', '')}")
    add("")
    add("### 地域")
    add("")
    for region in sorted(geography.get("regions", []), key=lambda r: r["id"]):
        add(f"#### {region['name']}（{region['type']}）")
        add("")
        add(region.get("description", ""))
        add("")
    add("### 街と施設")
    add("")
    for town in sorted(geography.get("towns", []), key=lambda t: t["id"]):
        add(f"#### {town['name']}")
        add("")
        add(f"登録人口: {town.get('population_registered', '')}名")
        add("")
        for fac in sorted(town.get("facilities", []), key=lambda f: f["id"]):
            add(f"- **{fac['name']}**（{fac['type']}）— {fac['location']}")
        add("")

    # ---- 第2章 錬金五法則 ----
    add("## 第2章 錬金五法則")
    add("")
    add("フラスカリアの錬金術は、万能の魔法ではなく、次の法則と代償を持つ技術である。")
    add("")
    for law in sorted(alchemy.get("laws", []), key=lambda x: x["id"]):
        add(f"### {law['name']}")
        add("")
        add(law.get("principle", ""))
        add("")
    add("### 属性")
    add("")
    add("、".join(alchemy.get("attributes", [])))
    add("")
    add("### 失敗の形態")
    add("")
    for mode in alchemy.get("failure_modes", []):
        add(f"- {mode}")
    add("")
    add("### 発見の扱い")
    add("")
    add(alchemy.get("discovery_rule", ""))
    add("")

    # ---- 第3章 素材図鑑 ----
    add("## 第3章 素材図鑑")
    add("")
    discovered = [m for m in materials if m.get("discovery_status") == "discovered"]
    undiscovered = [m for m in materials if m.get("discovery_status") != "discovered"]
    discovered.sort(key=lambda m: m["id"])
    undiscovered.sort(key=lambda m: m["id"])
    add(f"発見済み {len(discovered)} 種 / 未発見 {len(undiscovered)} 種（対象期間末時点の正式状態による）。")
    add("")
    add("### 発見済み素材")
    add("")
    for m in discovered:
        add(f"#### {m['name']}（{m['id']}）")
        add("")
        add(f"- 分類: {m.get('category', '')}")
        add(f"- 産地: {m.get('origin', '')}")
        add(f"- 希少性: {m.get('rarity', '')}")
        add(f"- 性質: {'、'.join(m.get('properties', []))}")
        add(f"- 属性: {m.get('attribute', '')}")
        add(f"- 安定度: {m.get('stability', '')}")
        add(f"- 用途: {'、'.join(m.get('uses', []))}")
        add(f"- 採取・生産条件: {m.get('gathering_condition', '')}")
        add(f"- 市場価値: {m.get('market_value', '')} Dr")
        add("")
    add("### 未発見素材")
    add("")
    add("以下は存在が言い伝え・仮説の形で記録されているだけで、まだ発見されていない素材である。")
    add("知識の門の法則により、性質・産地・用途は未確認のため記載しない。")
    add("")
    if undiscovered:
        for m in undiscovered:
            add(f"- **{m['name']}**（{m['id']}）— 未発見")
    else:
        add("- （なし）")
    add("")

    # ---- 第4章 レシピと調合 ----
    add("## 第4章 レシピと調合")
    add("")
    for rec in sorted(recipes, key=lambda r: r["id"]):
        status_label = RECIPE_STATUS.get(rec.get("status"), rec.get("status", ""))
        add(f"### {rec['name']}（{rec['id']} / {status_label}）")
        add("")
        mats = []
        for item in rec.get("materials", []):
            mat = mat_by_id.get(item["material_id"])
            if mat is None:
                mats.append(f"{item['material_id']} x{item.get('amount', '')}")
            else:
                suffix = "" if mat.get("discovery_status") == "discovered" else "（未発見）"
                mats.append(f"{mat['name']} x{item.get('amount', '')}{suffix}")
        add(f"- 素材: {'、'.join(mats)}")
        add(f"- 設備: {rec.get('equipment', '')}")
        add(f"- 条件: {rec.get('condition', '')}")
        add(f"- 効果・目的: {rec.get('effect', '')}")
        add(f"- 必要な知識: {'、'.join(rec.get('knowledge_required', []))}")
        if rec.get("status") == "hypothesis":
            add("- 備考: 未検証の仮説である。素材が未発見の場合は、知識の門の法則により意図的な実験はできない。")
        add("")

    # ---- 第5章 実験記録 ----
    add("## 第5章 実験記録")
    add("")
    add("対象期間に履歴へ記録された実験の実績のみを載せる。記録にない実験・成功は存在しないものとして扱う。")
    add("")
    experiments = [h for h in period_history if h.get("experiment")]
    if experiments:
        for h in experiments:
            exp = h["experiment"]
            rec = rec_by_id.get(exp.get("recipe_id"))
            rec_name = rec["name"] if rec else exp.get("recipe_id", "")
            result = "成功" if exp.get("success") else "失敗／進展なし"
            add(f"### {exp.get('id', '')} — {display_date(h['date'])}")
            add("")
            add(f"- 対象レシピ: {rec_name}（{exp.get('recipe_id', '')}）")
            add(f"- 結果: {result}")
            add(f"- 判定詳細: {exp.get('reason', '')}")
            add(f"- その日の天候: {h.get('weather', '')}")
            add("")
    else:
        add("対象期間に記録された実験はありません。")
        add("")

    # ---- 第6章 住民名鑑 ----
    add("## 第6章 住民名鑑")
    add("")
    for r in sorted(residents, key=lambda x: x["id"]):
        add(f"### {r['name']}（{r['id']}）")
        add("")
        age = r.get("age")
        add(f"- 年齢: {age if age is not None else '記録なし'}")
        add(f"- 職業: {r.get('occupation', '')}")
        add(f"- 居住地: {r.get('residence', '')}")
        add(f"- 所属: {r.get('organization', '')}")
        add(f"- 性格: {r.get('personality', '')}")
        add(f"- 目標: {r.get('goal', '')}")
        add(f"- 知識: {'、'.join(r.get('knowledge', []))}")
        skills = r.get("skills", {})
        if skills:
            add("- 技術: " + "、".join(f"{k} {v}" for k, v in sorted(skills.items())))
        rels = r.get("relationships", {})
        if rels:
            add("- 人間関係:")
            for other_id in sorted(rels):
                other = res_by_id.get(other_id)
                other_name = other["name"] if other else other_id
                add(f"  - {other_name}: {rels[other_id]}")
        add(f"- 健康状態: {r.get('health', '')}")
        add(f"- 現在の活動: {r.get('current_activity', '')}")
        past = r.get("past_important_events", [])
        if past:
            add("- 過去の重要な出来事:")
            for ev in past:
                add(f"  - {ev}")
        add("")

    # ---- 第7章 歴史年表 ----
    add("## 第7章 歴史年表")
    add("")
    add(f"{display_date(args.date_from)}から{display_date(args.date_to)}までの、履歴に記録された出来事である。")
    add("")
    if period_history:
        for h in period_history:
            add(f"### {display_date(h['date'])}（{h['date']}）")
            add("")
            add(f"天候: {h.get('weather', '')}")
            add("")
            for ev in h.get("events", []):
                add(f"- {ev}")
            add("")
    else:
        add("対象期間に記録された出来事はありません。")
        add("")

    # ---- 付録A 通貨と市場 ----
    add("## 付録A 通貨と市場")
    add("")
    currency = economy.get("currency", {})
    add(f"通貨は「{currency.get('name', '')}（{currency.get('symbol', '')}）」。{currency.get('note', '')}")
    add("")
    add("以下は編纂時点の正式状態（`world/economy.json`）に基づく市場のスナップショットである。")
    add("")
    for shop in sorted(economy.get("shops", []), key=lambda s: s["id"]):
        owner = res_by_id.get(shop.get("owner_resident_id"))
        owner_name = owner["name"] if owner else shop.get("owner_resident_id", "")
        add(f"### {shop['name']}（店主: {owner_name}）")
        add("")
        for item in sorted(shop.get("inventory", []), key=lambda i: i["material_id"]):
            mat = mat_by_id.get(item["material_id"])
            mat_name = mat["name"] if mat else item["material_id"]
            add(f"- {mat_name}: 在庫 {item.get('stock', '')} / 価格 {item.get('price', '')} Dr")
        add("")

    # ---- 付録B 関連記録への索引 ----
    add("## 付録B 関連記録への索引")
    add("")
    add("対象期間に書かれた新聞・研究日誌など（`stories/`）への索引である。本文の事実関係は正式記録（履歴）に基づく。")
    add("")
    stories = story_index(args.date_from, args.date_to)
    if stories:
        for story_date, rel, title in stories:
            label = f" — {title}" if title else ""
            add(f"- {display_date(story_date)}: `{rel}`{label}")
    else:
        add("- （対象期間の記録物はありません）")
    add("")

    # ---- 編者あとがき ----
    add("## 編者あとがき")
    add("")
    add("（編者枠: 発売版では、編者ポコがこの期間の世界を振り返って記す。")
    add("ここに書けるのは正式記録に基づく振り返りだけであり、記録にない出来事をあとがきで追加することはしない。）")
    add("")
    add("ポコ（界守／記録者・編者）")
    add("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="フラスカリア錬金術図鑑の原稿を編纂する")
    parser.add_argument("--from", dest="date_from", default="0001-01-01", help="対象期間の開始（フラスコ日付 YYYY-MM-DD）")
    parser.add_argument("--to", dest="date_to", default=None, help="対象期間の終了（フラスコ日付 YYYY-MM-DD）。省略時は state の last_processed_date")
    parser.add_argument("--out", required=True, help="出力先 Markdown のパス")
    parser.add_argument("--edition", default="Vol.1", help="タイトルページに記す版名（例: Vol.1）")
    args = parser.parse_args()

    # 検証が通らなければ生成しない
    errors = validate()
    if errors:
        print("VALIDATE FAILED — 原稿を生成しません")
        for e in errors:
            print("-", e)
        sys.exit(1)

    check_date(args.date_from, "--from")
    if args.date_to is None:
        args.date_to = load("state.json").get("last_processed_date") or args.date_from
    check_date(args.date_to, "--to")
    if args.date_from > args.date_to:
        raise SystemExit(f"期間が逆転しています: --from {args.date_from} > --to {args.date_to}")

    text = build(args)
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(f"generated {out_path} ({args.date_from} .. {args.date_to}, edition={args.edition})")


if __name__ == "__main__":
    main()
