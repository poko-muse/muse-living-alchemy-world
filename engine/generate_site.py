#!/usr/bin/env python3
"""フラスカリア公開サイト生成器。

見せ方の設計原則（2026-11-19 Fuu）:
- 羅列にしない。パッと見て魅力が伝わる画面にする（ヒーロー＝世界全景＋今日の出来事）。
- 興味を持った人がより深くハマれるよう、詳細はカードを開くと出てくる二段構えにする。
- データの正は world/*.json と world/history.jsonl。在庫変動などの機械的な記録は表に出さない。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(n):
    return json.loads((ROOT / "world" / n).read_text(encoding="utf-8"))


def esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def item_img(item_id, name):
    if (ROOT / "site" / "assets" / "items" / f"{item_id}.webp").exists():
        return f"<div class=\"card-imgwrap\"><img class=\"item-img\" src=\"assets/items/{item_id}.webp\" alt=\"{esc(name)}\" loading=\"lazy\"></div>"
    return ""


def res_img(res_id, name):
    if (ROOT / "site" / "assets" / "residents" / f"{res_id}.webp").exists():
        return f"<div class=\"card-imgwrap\"><img class=\"item-img\" src=\"assets/residents/{res_id}.webp\" alt=\"{esc(name)}\" loading=\"lazy\"></div>"
    return ""


def story_events(day):
    """履歴の events から、読者向けの物語イベントだけを取り出す。"""
    out = []
    for e in day.get("events", []):
        if "在庫" in e or "素材消費" in e or e.startswith("天候:"):
            continue
        e = re.sub(r"（roll=[^）]*）", "", e)
        out.append(e)
    return out


CSS = """
*{box-sizing:border-box}
body{font-family:"Hiragino Maru Gothic ProN","Hiragino Sans",sans-serif;margin:0;background:#f7ecd2;color:#4a3826;line-height:1.75}
.wrap{max-width:760px;margin:0 auto;padding:0 14px 40px}
.hero{position:relative;margin:14px 0 6px}
.hero img{width:100%;height:auto;display:block;border-radius:20px;box-shadow:0 10px 30px rgba(120,84,30,.25)}
.hero .titlebox{position:absolute;left:12px;right:12px;bottom:12px;background:rgba(255,250,240,.92);border-radius:16px;padding:12px 16px;box-shadow:0 4px 14px rgba(120,84,30,.18)}
.hero h1{margin:0;font-size:30px;letter-spacing:.08em;color:#7a4d16}
.hero .sub{margin:2px 0 8px;font-size:13px;color:#8a6a45}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{background:#eaf6f3;border:1px solid #bfe0d8;color:#22665c;border-radius:999px;padding:2px 10px;font-size:12.5px;font-weight:700}
.chip.warm{background:#fdeeda;border-color:#f3d3a1;color:#96620f}
section{margin-top:30px}
h2{font-size:21px;color:#7a4d16;border-left:6px solid #e8a93d;padding-left:10px;margin:0 0 6px}
.lead{font-size:13.5px;color:#8a6a45;margin:0 0 12px}
.story{background:#fffaf0;border:1px solid #e7dab9;border-radius:16px;padding:14px 16px;box-shadow:0 3px 10px rgba(120,84,30,.08)}
.story .day{font-weight:700;color:#96620f;font-size:14px;margin-bottom:6px}
.story ul{margin:6px 0 0;padding-left:20px}
.story li{margin:4px 0}
.exp{background:#fdf3d8;border:1px solid #f0d48a;border-radius:12px;padding:10px 12px;margin-top:10px}
.exp b{color:#96620f}
.cards{display:flex;flex-wrap:wrap;gap:12px}
.card{background:#fffaf0;border:1px solid #e7dab9;border-radius:14px;padding:10px;width:calc(50% - 6px);box-shadow:0 3px 10px rgba(120,84,30,.07)}
@media(min-width:640px){.card{width:calc(33.333% - 8px)}}
.card p{margin:6px 0 0;font-size:14px}
.card .meta{font-size:12px;color:#8a6a45}
.card-imgwrap{animation:floaty 5s ease-in-out infinite}
.item-img{display:block;width:100%;height:auto;border-radius:10px}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
@media (prefers-reduced-motion: reduce){.card-imgwrap{animation:none}}
details{margin-top:8px}
summary{cursor:pointer;font-size:13px;font-weight:700;color:#22665c;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"＋ "}
details[open ] summary::before{content:"－ "}
.dlist{font-size:13px;margin:8px 0 0;padding:10px 12px;background:#fdf6e0;border-radius:10px}
.dlist div{margin:3px 0}
.dlist .k{font-weight:700;color:#96620f}
.badge{display:inline-block;background:#fdeeda;border:1px solid #f3d3a1;color:#96620f;border-radius:999px;padding:0 8px;font-size:11.5px;font-weight:700;margin-left:6px}
.badge.undis{background:#eee;border-color:#ccc;color:#777}
.journal{background:#fffaf0;border:1px solid #e7dab9;border-radius:14px;padding:12px 16px;margin-bottom:10px}
.journal .day{font-weight:700;color:#96620f;font-size:14px}
.journal ul{margin:4px 0 0;padding-left:20px;font-size:14px}
.about{background:#eef7f4;border:1px solid #cfe6df;border-radius:14px;padding:12px 16px;font-size:14px}
footer{margin-top:36px;font-size:12px;color:#a08760;text-align:center}
"""


def main():
    state = load("state.json")
    residents = load("residents.json")
    materials = load("materials.json")
    geo = load("geography.json")
    recipes = load("recipes.json")
    hist = []
    hp = ROOT / "world" / "history.jsonl"
    if hp.exists():
        for line in hp.read_text(encoding="utf-8").strip().splitlines():
            if line.strip():
                hist.append(json.loads(line))
    mat_by_id = {m["id"]: m for m in materials}

    # --- ヒーロー＋今日の出来事 ---
    today = hist[-1] if hist else None
    today_html = ""
    if today:
        evs = story_events(today)
        lis = "".join(f"<li>{esc(e)}</li>" for e in evs if "錬金実験" not in e)
        exp_html = ""
        exp_lines = [e for e in evs if "錬金実験" in e]
        if exp_lines:
            exp_html = "<div class=\"exp\">" + "".join(f"<div>⚗️ <b>錬金実験</b>：{esc(e.split(':', 1)[-1].strip() if ':' in e else e)}</div>" for e in exp_lines) + "</div>"
        today_html = f"<div class=\"story\"><div class=\"day\">📖 {esc(today.get('date',''))} の記録（天気：{esc(today.get('weather',''))}）</div><ul>{lis}</ul>{exp_html}</div>"
    else:
        today_html = "<div class=\"story\">まだ記録がありません。</div>"

    map_img = ""
    if (ROOT / "site" / "assets" / "maps" / "flaskaria_overview.webp").exists():
        map_img = "<img src=\"assets/maps/flaskaria_overview.webp\" alt=\"フラスカリア全景\" >"

    # --- 素材図鑑（詳細は開いて読む） ---
    def recipes_using(mid):
        names = []
        for r in recipes:
            if any(mm["material_id"] == mid for mm in r.get("materials", [])):
                names.append(r["name"])
        return names

    mat_cards = []
    for m in materials:
        undis = m.get("discovery_status") != "discovered"
        badge = "<span class=\"badge undis\">未発見</span>" if undis else ""
        uses_rec = recipes_using(m["id"])
        rows = [
            ("産地", m.get("origin", "")),
            ("性質", "・".join(m.get("properties", []))),
            ("使いみち", "・".join(m.get("uses", []))),
            ("採取", m.get("gathering_condition", "")),
            ("珍しさ", m.get("rarity", "")),
            ("安定度", m.get("stability", "")),
            ("市場価格", f"{m.get('market_value','')} Dr"),
        ]
        if uses_rec:
            rows.append(("使われる調合", "、".join(uses_rec)))
        dlist = "".join(f"<div><span class=\"k\">{esc(k)}</span>：{esc(v)}</div>" for k, v in rows if v != "")
        mat_cards.append(
            f"<div class=\"card\">{item_img(m['id'], m['name'])}<p><b>{esc(m['name'])}</b>{badge}<br>"
            f"<span class=\"meta\">{esc(m['category'])}／属性：{esc(m['attribute'])}</span></p>"
            f"<details><summary>くわしく見る</summary><div class=\"dlist\">{dlist}</div></details></div>"
        )
    mat_html = "".join(mat_cards)

    # --- 調合品図鑑 ---
    status_label = {"known": "既知のレシピ", "researching": "研究中", "hypothesis": "仮説段階"}
    rec_cards = []
    for r in recipes:
        mats = "、".join(
            f"{esc(mat_by_id.get(mm['material_id'], {}).get('name', mm['material_id']))}×{mm['amount']}"
            for mm in r.get("materials", [])
        )
        rows = [
            ("材料", mats),
            ("器具", r.get("equipment", "")),
            ("条件", r.get("condition", "")),
            ("効果", r.get("effect", "")),
            ("状態", status_label.get(r.get("status", ""), r.get("status", ""))),
        ]
        dlist = "".join(f"<div><span class=\"k\">{esc(k)}</span>：{esc(v)}</div>" for k, v in rows if v != "")
        rec_cards.append(
            f"<div class=\"card\">{item_img(r['id'], r['name'])}<p><b>{esc(r['name'])}</b><br>"
            f"<span class=\"meta\">{esc(status_label.get(r.get('status',''), ''))}</span></p>"
            f"<details><summary>レシピを見る</summary><div class=\"dlist\">{dlist}</div></details></div>"
        )
    rec_html = "".join(rec_cards)

    # --- 住民名鑑 ---
    res_cards = []
    for r in residents:
        rows = [
            ("性格", r.get("personality", "")),
            ("いまの活動", r.get("current_activity", "")),
            ("目標", r.get("goal", "")),
            ("所属", r.get("organization", "")),
            ("大切な出来事", "／".join(r.get("past_important_events", []))),
        ]
        dlist = "".join(f"<div><span class=\"k\">{esc(k)}</span>：{esc(v)}</div>" for k, v in rows if v != "")
        res_cards.append(
            f"<div class=\"card\">{res_img(r['id'], r['name'])}<p><b>{esc(r['name'])}</b><br>"
            f"<span class=\"meta\">{esc(r['occupation'])}／{esc(r['residence'])}</span></p>"
            f"<details><summary>人となり</summary><div class=\"dlist\">{dlist}</div></details></div>"
        )
    res_html = "".join(res_cards)

    # --- 歴史（日誌） ---
    def journal_entry(day):
        evs = story_events(day)[:4]
        lis = "".join(f"<li>{esc(e)}</li>" for e in evs)
        return f"<div class=\"journal\"><div class=\"day\">{esc(day.get('date',''))}（{esc(day.get('weather',''))}）</div><ul>{lis}</ul></div>"

    recent = hist[-4:][::-1]
    older = hist[:-4][::-1] if len(hist) > 4 else []
    journal_html = "".join(journal_entry(d) for d in recent)
    if older:
        journal_html += (
            "<details><summary>もっと古い記録を読む</summary>"
            + "".join(journal_entry(d) for d in older)
            + "</details>"
        )
    if not journal_html:
        journal_html = "<div class=\"journal\">創世のみ</div>"

    regions = " → ".join(r["name"] for r in geo["regions"])
    container = esc(geo.get("container", ""))

    html = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>フラスカリア — MUSE LIVING ALCHEMY WORLD</title><style>{CSS}</style></head><body>
<div class="wrap">
<div class="hero">{map_img}
<div class="titlebox"><h1>フラスカリア</h1><p class="sub">机の上の箱庭で営まれる、小さな錬金術の世界。フラスコの理のもとに生まれ、毎日、少しずつ物語が進んでいます。</p>
<div class="chips"><span class="chip warm">📅 {esc(state.get('current_date_display',''))}</span><span class="chip">季節：{esc(state.get('season',''))}</span><span class="chip">天気：{esc(state.get('weather',''))}</span><span class="chip">人口：{esc(state.get('population',''))}人</span></div>
</div></div>
<section><h2>今日のフラスカリア</h2><p class="lead">世界で今日起きたことを、記録者のポコが書き留めています。</p>{today_html}</section>
<section><h2>素材図鑑</h2><p class="lead">フラスカリアで採れる素材たち。気になる素材は開いてみてください。</p><div class="cards">{mat_html}</div></section>
<section><h2>調合品図鑑</h2><p class="lead">素材を組み合わせて生まれる錬金品。レシピの中身も見られます。</p><div class="cards">{rec_html}</div></section>
<section><h2>住民名鑑</h2><p class="lead">この世界に暮らす8人。それぞれの目標や、いま取り組んでいることがあります。</p><div class="cards">{res_html}</div></section>
<section><h2>世界の歩み</h2><p class="lead">創世からの記録です。失敗も成功も、消さずに残しています。</p>{journal_html}</section>
<section><h2>この世界について</h2><div class="about"><p>{container}</p><p>主な場所：{esc(regions)}</p><p>中央のぽこ丘をくるり川が一周し、コルク森と映し湖が向き合い、空は光を通すガラスの天蓋になっています。</p></div></section>
<footer>※これは架空世界の創作プロジェクトです。世界・住民・錬金術はすべて架空です。<br>MUSE LIVING ALCHEMY WORLD — フラスカリア</footer>
</div>
</body></html>"""
    out = ROOT / "site" / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"generated {out}")


if __name__ == "__main__":
    main()
