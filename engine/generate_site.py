#!/usr/bin/env python3
"""フラスカリア公開サイト生成器（複数ページ版）。

見せ方の設計原則（2026-11-19 Fuu、docs/presentation_design.md）:
- 羅列にしない。パッと見て魅力が伝わり、興味を持ったらより深くハマれる画面にする。
- 構成はゲームの図鑑UIモック（assets/visual-samples/reference_ui_*.jpg）に寄せる：
  トップ／図鑑／住民／日誌／世界について の複数ページ＋下部タブ。
- データの正は world/*.json と world/history.jsonl。在庫変動などの機械的な記録は表に出さない。
- 素材・調合品には個別ページを作り、外部（Pinterest等）から直接来られるようにする。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"


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


def story_events(day):
    """履歴の events から、読者向けの物語イベントだけを取り出す。"""
    out = []
    for e in day.get("events", []):
        if "在庫" in e or "素材消費" in e or e.startswith("天候:"):
            continue
        e = re.sub(r"（roll=[^）]*）", "", e)
        out.append(e)
    return out


def display_date(flask_date):
    y, m, d = flask_date.split("-")
    return f"フラスコ暦{int(y)}年{int(m)}月{int(d)}日"


def img_exists(rel):
    return (SITE / rel).exists()


def img_tag(rel, alt, cls="item-img", prefix=""):
    if img_exists(rel):
        return f"<img class=\"{cls}\" src=\"{prefix}{rel}\" alt=\"{esc(alt)}\" loading=\"lazy\">"
    return ""


CSS = """
*{box-sizing:border-box}
body{font-family:"Hiragino Maru Gothic ProN","Hiragino Sans",sans-serif;margin:0;background:#f3e5c3;color:#4a3826;line-height:1.75;padding-bottom:78px}
.wrap{max-width:760px;margin:0 auto;padding:0 12px 32px}
.topbar{background:linear-gradient(180deg,#8a5a2b,#6f451d);color:#ffe9bd;text-align:center;padding:10px 8px 8px;box-shadow:0 2px 8px rgba(90,55,10,.35)}
.topbar .t{font-size:19px;font-weight:800;letter-spacing:.14em}
.topbar .s{font-size:11px;opacity:.85}
.hero{position:relative;margin:12px 0 6px}
.hero img{width:100%;height:auto;display:block;border-radius:18px;box-shadow:0 10px 30px rgba(120,84,30,.25);border:4px solid #a4712f}
.hero .titlebox{position:absolute;left:10px;right:10px;bottom:10px;background:rgba(255,250,240,.93);border-radius:14px;padding:10px 14px;box-shadow:0 4px 14px rgba(120,84,30,.18)}
.hero h1{margin:0;font-size:27px;letter-spacing:.06em;color:#7a4d16}
.hero .sub{margin:2px 0 8px;font-size:12.5px;color:#8a6a45}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{background:#eaf6f3;border:1px solid #bfe0d8;color:#22665c;border-radius:999px;padding:2px 10px;font-size:12.5px;font-weight:700}
.chip.warm{background:#fdeeda;border-color:#f3d3a1;color:#96620f}
section{margin-top:26px}
h2.ribbon{font-size:19px;color:#fff8e6;background:linear-gradient(180deg,#b3813a,#96681f);border-radius:10px;padding:7px 14px;margin:0 0 8px;box-shadow:0 3px 8px rgba(120,84,30,.25);letter-spacing:.05em}
.lead{font-size:13.5px;color:#8a6a45;margin:0 0 12px}
.panel{background:#fffaf0;border:2px solid #d9bd7f;border-radius:16px;padding:14px 16px;box-shadow:0 3px 10px rgba(120,84,30,.10);margin-bottom:12px}
.panel h3{margin:0 0 8px;font-size:16px;color:#7a4d16}
.story .day{font-weight:700;color:#96620f;font-size:14px;margin-bottom:6px}
.story ul{margin:6px 0 0;padding-left:20px}
.story li{margin:4px 0}
.exp{background:#fdf3d8;border:1px solid #f0d48a;border-radius:12px;padding:10px 12px;margin-top:10px}
.exp b{color:#96620f}
.cards{display:flex;flex-wrap:wrap;gap:12px}
"""

CSS2 = """
.card{background:#fffaf0;border:2px solid #e0cd9a;border-radius:14px;padding:10px;width:calc(50% - 6px);box-shadow:0 3px 10px rgba(120,84,30,.07)}
@media(min-width:640px){.card{width:calc(33.333% - 8px)}}
.card a{color:inherit;text-decoration:none}
.card p{margin:6px 0 0;font-size:14px}
.card .meta{font-size:12px;color:#8a6a45}
.item-img{display:block;width:100%;height:auto;border-radius:10px}
.big-img{display:block;width:100%;max-width:420px;height:auto;border-radius:14px;margin:0 auto}
.minis{display:flex;gap:10px;overflow-x:auto;padding:4px 2px 8px}
.mini{flex:0 0 92px;text-align:center;text-decoration:none;color:inherit}
.mini img{width:92px;height:92px;object-fit:cover;border-radius:12px;border:2px solid #e0cd9a;background:#fffaf0}
.mini .n{font-size:11.5px;font-weight:700;margin-top:2px}
.badge{display:inline-block;background:#fdeeda;border:1px solid #f3d3a1;color:#96620f;border-radius:999px;padding:0 8px;font-size:11.5px;font-weight:700;margin-left:6px}
.badge.undis{background:#eee;border-color:#ccc;color:#777}
.dlist{font-size:14px;margin:10px 0;padding:12px 14px;background:#fdf6e0;border-radius:12px}
.dlist div{margin:4px 0}
.dlist .k{font-weight:700;color:#96620f}
.stats{display:flex;flex-wrap:wrap;gap:8px}
.stat{flex:1 1 100px;background:#fdf6e0;border:1px solid #e7dab9;border-radius:12px;padding:8px 10px;text-align:center}
.stat .v{font-size:19px;font-weight:800;color:#7a4d16}
.stat .l{font-size:11.5px;color:#8a6a45}
.btn{display:inline-block;background:linear-gradient(180deg,#e8a93d,#cf8417);color:#fff;font-weight:800;border-radius:999px;padding:8px 18px;text-decoration:none;box-shadow:0 3px 8px rgba(150,100,20,.35);font-size:14px}
.btn.sub{background:linear-gradient(180deg,#5ea79c,#3f8a7f)}
.daylink{display:block;background:#fffaf0;border:2px solid #e0cd9a;border-radius:14px;padding:10px 14px;margin-bottom:10px;text-decoration:none;color:inherit}
.daylink .d{font-weight:800;color:#96620f}
.daylink .t{font-size:13.5px;color:#6b5136}
.pager{display:flex;justify-content:space-between;margin-top:16px}
.tabbar{position:fixed;left:0;right:0;bottom:0;background:rgba(255,250,240,.97);border-top:2px solid #d9bd7f;display:flex;z-index:10;box-shadow:0 -3px 10px rgba(120,84,30,.12)}
.tabbar a{flex:1;text-align:center;padding:7px 0 9px;font-size:11.5px;font-weight:700;color:#8a6a45;text-decoration:none}
.tabbar a .ic{display:block;font-size:19px;line-height:1.2}
.tabbar a.on{color:#b57a17}
footer{margin-top:34px;font-size:12px;color:#a08760;text-align:center}
.bubble{position:relative;background:#fffaf0;border:2px solid #d9bd7f;border-radius:16px;padding:12px 16px;box-shadow:0 3px 10px rgba(120,84,30,.10)}
.bubble::after{content:"";position:absolute;top:-11px;left:36px;border:6px solid transparent;border-bottom:8px solid #d9bd7f}
.bubble .who{font-weight:800;color:#96620f;font-size:13px}
.bubble p{margin:2px 0 0;font-size:14.5px}
.circles{display:flex;gap:10px;overflow-x:auto;padding:6px 2px 10px}
.circle{flex:0 0 76px;text-align:center;text-decoration:none;color:inherit}
.circle img{width:76px;height:76px;object-fit:cover;border-radius:50%;border:3px solid #e8cf8f;background:#fffaf0;box-shadow:0 3px 8px rgba(120,84,30,.15)}
.circle .n{font-size:11px;font-weight:700;margin-top:2px;line-height:1.35}
.bigbtns{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.bigbtn{display:flex;align-items:center;justify-content:center;gap:8px;background:linear-gradient(180deg,#fff6dd,#ffeec2);border:2px solid #d9bd7f;border-radius:16px;padding:14px 6px;font-size:16px;font-weight:800;color:#7a4d16;text-decoration:none;box-shadow:0 3px 8px rgba(120,84,30,.15)}
.bigbtn .ic{font-size:22px}
details{margin-top:8px}
summary{cursor:pointer;font-size:13px;font-weight:700;color:#22665c;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"＋ "}
details[open ] summary::before{content:"－ "}
"""

FULL_CSS = CSS + CSS2

TABS = [
    ("index.html", "トップ", "🏠"),
    ("zukan.html", "図鑑", "📖"),
    ("residents.html", "住民", "🧑‍🤝‍🧑"),
    ("journal.html", "日誌", "📜"),
    ("map.html", "地図", "🗺️"),
]


def page(title, active, body, depth=0):
    prefix = "../" * depth
    nav = "".join(
        f"<a href=\"{prefix}{href}\" class=\"{'on' if href == active else ''}\">"
        f"<span class=\"ic\">{icon}</span>{label}</a>"
        for href, label, icon in TABS
    )
    return (
        "<!DOCTYPE html><html lang=\"ja\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{esc(title)} — フラスカリア</title><style>{FULL_CSS}</style></head><body>"
        "<div class=\"topbar\"><div class=\"t\">フラスカリア</div>"
        "<div class=\"s\">MUSE LIVING ALCHEMY WORLD</div></div>"
        f"<div class=\"wrap\">{body}</div>"
        f"<nav class=\"tabbar\">{nav}</nav>"
        "</body></html>"
    )


def write_page(rel, html):
    out = SITE / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"generated {out}")


def main():
    state = load("state.json")
    residents = load("residents.json")
    materials = load("materials.json")
    geo = load("geography.json")
    recipes = load("recipes.json")
    alchemy = load("alchemy.json")
    economy = load("economy.json")
    hist = []
    hp = ROOT / "world" / "history.jsonl"
    if hp.exists():
        for line in hp.read_text(encoding="utf-8").strip().splitlines():
            if line.strip():
                hist.append(json.loads(line))
    mat_by_id = {m["id"]: m for m in materials}
    rec_by_id = {r["id"]: r for r in recipes}
    status_label = {"known": "既知のレシピ", "researching": "研究中", "hypothesis": "仮説段階"}

    def recipes_using(mid):
        return [r for r in recipes if any(mm["material_id"] == mid for mm in r.get("materials", []))]

    def story_block(day, link=False):
        evs = story_events(day)
        lis = "".join(f"<li>{esc(e)}</li>" for e in evs if "錬金実験" not in e)
        exp_lines = [e for e in evs if "錬金実験" in e]
        exp_html = ""
        if exp_lines:
            exp_html = "<div class=\"exp\">" + "".join(
                f"<div>⚗️ <b>錬金実験</b>：{esc(e.split(':', 1)[-1].strip() if ':' in e else e)}</div>"
                for e in exp_lines
            ) + "</div>"
        more = f"<p style=\"margin-top:10px\"><a class=\"btn sub\" href=\"day/{day['date']}.html\">この日の日誌をひらく</a></p>" if link else ""
        return (
            f"<div class=\"panel story\"><div class=\"day\">📖 {esc(display_date(day['date']))} の記録"
            f"（天気：{esc(day.get('weather', ''))}）</div><ul>{lis}</ul>{exp_html}{more}</div>"
        )

    # ---------- トップ ----------
    hero_rel = "assets/keyvisual.webp" if img_exists("assets/keyvisual.webp") else "assets/maps/flaskaria_overview.webp"
    today = hist[-1] if hist else None
    today_html = story_block(today, link=True) if today else "<div class=\"panel\">まだ記録がありません。</div>"

    # ポコのいま（最新の日の記録から実データで組み立てる）
    poco_html = ""
    if today:
        evs = story_events(today)
        poco_line = next((e for e in evs if "ポコ" in e), "記録小屋で本日の記録を書いた")
        exp_note = ""
        for e in evs:
            mm = re.search(r"ルナが「(.+?)」の実験に(成功|失敗/進展なし)", e)
            if mm:
                exp_note = (
                    f"ルナの「{mm.group(1)}」の実験が成功しました！"
                    if mm.group(2) == "成功"
                    else f"ルナは「{mm.group(1)}」の研究を進めています。"
                )
        poco_html = (
            f"<div class=\"bubble\"><span class=\"who\">🟢 ポコのいま</span>"
            f"<p>{esc(poco_line)}。{esc(exp_note)}</p></div>"
        )

    # 状態パネル（現実の日付は最終処理日から）
    from datetime import date as _date

    real_label = ""
    lrd = state.get("last_processed_real_date", "")
    if lrd:
        try:
            _d = _date.fromisoformat(lrd)
            real_label = f"{_d.month}月{_d.day}日（{'月火水木金土日'[_d.weekday()]}）"
        except ValueError:
            real_label = lrd
    status_html = (
        "<div class=\"panel\"><div class=\"stats\">"
        f"<div class=\"stat\"><div class=\"v\" style=\"font-size:15px\">{esc(real_label)}</div><div class=\"l\">現実の今日</div></div>"
        f"<div class=\"stat\"><div class=\"v\" style=\"font-size:15px\">{esc(display_date(today['date'])) if today else ''}</div><div class=\"l\">世界の今日</div></div>"
        f"<div class=\"stat\"><div class=\"v\">{esc(state.get('weather', ''))}</div><div class=\"l\">天気／{esc(state.get('season', ''))}</div></div>"
        f"<div class=\"stat\"><div class=\"v\">{esc(state.get('population', ''))}人</div><div class=\"l\">人口</div></div>"
        "</div></div>"
    )

    # 注目の素材と調合（丸アイコンの横並び：直近の実験品→その材料→未発見→その他の順）
    circle_ids = []
    if today and today.get("experiment"):
        rid = today["experiment"].get("recipe_id")
        if rid:
            circle_ids.append(rid)
            for mmi in rec_by_id.get(rid, {}).get("materials", []):
                circle_ids.append(mmi["material_id"])
    _und = next((m for m in materials if m.get("discovery_status") != "discovered"), None)
    if _und:
        circle_ids.append(_und["id"])
    for m in materials:
        if len(circle_ids) >= 5:
            break
        if m["id"] not in circle_ids and m.get("discovery_status") == "discovered":
            circle_ids.append(m["id"])
    circles = ""
    for cid in circle_ids[:5]:
        obj = mat_by_id.get(cid) or rec_by_id.get(cid)
        if not obj or not img_exists(f"assets/items/{cid}.webp"):
            continue
        label = esc(obj["name"])
        if obj.get("discovery_status") == "undiscovered" or (
            cid in mat_by_id and mat_by_id[cid].get("discovery_status") != "discovered"
        ):
            label += "<br>（未発見）"
        circles += (
            f"<a class=\"circle\" href=\"item/{cid}.html\">"
            f"<img src=\"assets/items/{cid}.webp\" alt=\"{esc(obj['name'])}\" loading=\"lazy\">"
            f"<div class=\"n\">{label}</div></a>"
        )

    # 今週の調合メモ（直近7日の実験記録）
    memo_lines = []
    for d in hist[-7:]:
        for e in story_events(d):
            if "錬金実験" in e:
                memo_lines.append(f"{esc(display_date(d['date']))}：{esc(e.split(':', 1)[-1].strip() if ':' in e else e)}")
    memo_html = ""
    if memo_lines:
        memo_html = (
            "<div class=\"panel\"><h3>🧪 今週の調合メモ</h3>"
            + "".join(f"<p style=\"margin:4px 0\">{l}</p>" for l in memo_lines)
            + "</div>"
        )
    discovered = sum(1 for m in materials if m.get("discovery_status") == "discovered")
    shop_kinds = len({it["material_id"] for sh in economy.get("shops", []) for it in sh.get("inventory", [])})
    minis = ""
    for m in materials:
        if img_exists(f"assets/items/{m['id']}.webp"):
            minis += (
                f"<a class=\"mini\" href=\"item/{m['id']}.html\">"
                f"<img src=\"assets/items/{m['id']}.webp\" alt=\"{esc(m['name'])}\" loading=\"lazy\">"
                f"<div class=\"n\">{esc(m['name'])}</div></a>"
            )
    feat = rec_by_id.get("rec_002")
    feat_html = ""
    if feat:
        f_mats = " ＋ ".join(
            f"{esc(mat_by_id.get(mm['material_id'], {}).get('name', mm['material_id']))}×{mm['amount']}"
            for mm in feat.get("materials", [])
        )
        feat_html = (
            f"<div class=\"panel\"><h3>🧪 調合レシピの例：{esc(feat['name'])}</h3>"
            f"<div style=\"text-align:center\">{img_tag('assets/items/rec_002.webp', feat['name'], 'big-img')}</div>"
            f"<p style=\"text-align:center;font-weight:700\">{f_mats}</p>"
            f"<p>{esc(feat.get('effect', ''))}</p>"
            f"<p><a class=\"btn\" href=\"item/rec_002.html\">レシピをひらく</a></p></div>"
        )
    undis = next((m for m in materials if m.get("discovery_status") != "discovered"), None)
    undis_html = ""
    if undis:
        undis_html = (
            f"<div class=\"panel\"><h3>🌑 まだ見ぬ素材</h3>"
            f"<div style=\"text-align:center\">{img_tag('assets/items/' + undis['id'] + '.webp', '未発見の素材', 'big-img')}</div>"
            f"<p>まだ正体がわかっていない、幻の素材。いつか誰かが発見する日を、世界は待っています。</p>"
            f"<p><a class=\"btn sub\" href=\"item/{undis['id']}.html\">手がかりを見る</a></p></div>"
        )
    bigbtns = (
        "<div class=\"bigbtns\">"
        "<a class=\"bigbtn\" href=\"zukan.html\"><span class=\"ic\">📖</span>図鑑</a>"
        "<a class=\"bigbtn\" href=\"journal.html\"><span class=\"ic\">📜</span>世界日誌</a>"
        "<a class=\"bigbtn\" href=\"map.html\"><span class=\"ic\">🗺️</span>世界地図</a>"
        "<a class=\"bigbtn\" href=\"residents.html\"><span class=\"ic\">🧑‍🤝‍🧑</span>住民</a>"
        "</div>"
    )
    top_body = f"""
<div class="hero">{img_tag(hero_rel, 'フラスカリア', '')}
<div class="titlebox"><h1>フラスカリア</h1><p class="sub">小さな世界の観察記 — 机の上の箱庭で営まれる錬金術の世界。フラスコの理のもとに生まれ、毎日、少しずつ物語が進んでいます。</p>
</div></div>
<section style="margin-top:14px">{poco_html}</section>
<section>{status_html}</section>
<section><h2 class="ribbon">注目の素材と調合</h2><div class="circles">{circles}</div></section>
<section><h2 class="ribbon">世界の出来事</h2>{today_html}</section>
<section>{memo_html}</section>
<section><h2 class="ribbon">世界のようす</h2><div class="panel"><div class="stats">
<div class="stat"><div class="v">{discovered} / {len(materials)}</div><div class="l">発見した素材</div></div>
<div class="stat"><div class="v">{len(hist)}日</div><div class="l">記録された日々</div></div>
<div class="stat"><div class="v">{shop_kinds}種</div><div class="l">市場に出回る素材</div></div>
</div></div></section>
<section>{feat_html}</section>
<section>{undis_html}</section>
<section>{bigbtns}</section>
<footer>※これは架空世界の創作プロジェクトです。世界・住民・錬金術はすべて架空です。<br>MUSE LIVING ALCHEMY WORLD — フラスカリア</footer>
"""
    write_page("index.html", page("トップ", "index.html", top_body))

    # ---------- 図鑑 ----------
    def item_card(it, kind):
        badge = ""
        if kind == "mat" and it.get("discovery_status") != "discovered":
            badge = "<span class=\"badge undis\">未発見</span>"
        meta = (
            f"{esc(it['category'])}／属性：{esc(it['attribute'])}" if kind == "mat"
            else esc(status_label.get(it.get("status", ""), ""))
        )
        return (
            f"<div class=\"card\"><a href=\"item/{it['id']}.html\">"
            f"{img_tag('assets/items/' + it['id'] + '.webp', it['name'])}"
            f"<p><b>{esc(it['name'])}</b>{badge}<br><span class=\"meta\">{meta}</span></p></a></div>"
        )

    zukan_body = (
        "<section><h2 class=\"ribbon\">素材図鑑</h2>"
        "<p class=\"lead\">気になる素材をタップすると、産地や性質、使われる調合まで見られます。</p>"
        f"<div class=\"cards\">{''.join(item_card(m, 'mat') for m in materials)}</div></section>"
        "<section><h2 class=\"ribbon\">調合品図鑑</h2>"
        "<p class=\"lead\">素材を組み合わせて生まれる錬金品。レシピの中身も見られます。</p>"
        f"<div class=\"cards\">{''.join(item_card(r, 'rec') for r in recipes)}</div></section>"
    )
    write_page("zukan.html", page("図鑑", "zukan.html", zukan_body))

    # ---------- アイテム詳細 ----------
    for m in materials:
        undis_m = m.get("discovery_status") != "discovered"
        rows = [
            ("産地", m.get("origin", "")), ("性質", "・".join(m.get("properties", []))),
            ("使いみち", "・".join(m.get("uses", []))), ("採取", m.get("gathering_condition", "")),
            ("珍しさ", m.get("rarity", "")), ("安定度", m.get("stability", "")),
            ("市場価格", f"{m.get('market_value', '')} Dr"),
        ]
        dlist = "".join(f"<div><span class=\"k\">{esc(k)}</span>：{esc(v)}</div>" for k, v in rows if v != "")
        using = recipes_using(m["id"])
        using_html = ""
        if using:
            using_html = "<h3>この素材を使う調合</h3>" + "".join(
                f"<p><a class=\"btn sub\" href=\"{r['id']}.html\">{esc(r['name'])}</a></p>" for r in using
            )
        note = "<p>まだ正体がわかっていない、幻の素材。発見の記録はまだありません。</p>" if undis_m else ""
        body = (
            f"<section><h2 class=\"ribbon\">{esc(m['name'])}</h2>"
            f"{img_tag('assets/items/' + m['id'] + '.webp', m['name'], 'big-img', prefix='../')}"
            f"<div class=\"chips\" style=\"margin-top:10px\"><span class=\"chip\">{esc(m['category'])}</span>"
            f"<span class=\"chip\">属性：{esc(m['attribute'])}</span>"
            f"<span class=\"chip warm\">{'未発見' if undis_m else '発見済み'}</span></div>"
            f"{note}<div class=\"dlist\">{dlist}</div>{using_html}"
            f"<p><a class=\"btn\" href=\"../zukan.html\">図鑑にもどる</a></p></section>"
        )
        write_page(f"item/{m['id']}.html", page(m["name"], "zukan.html", body, depth=1))

    for r in recipes:
        mats_html = "".join(
            f"<a class=\"mini\" href=\"{mm['material_id']}.html\">"
            f"<img src=\"../assets/items/{mm['material_id']}.webp\" alt=\"{esc(mat_by_id.get(mm['material_id'], {}).get('name', ''))}\" loading=\"lazy\">"
            f"<div class=\"n\">{esc(mat_by_id.get(mm['material_id'], {}).get('name', mm['material_id']))}×{mm['amount']}</div></a>"
            for mm in r.get("materials", [])
        )
        rows = [
            ("器具", r.get("equipment", "")), ("条件", r.get("condition", "")),
            ("効果", r.get("effect", "")), ("状態", status_label.get(r.get("status", ""), "")),
        ]
        dlist = "".join(f"<div><span class=\"k\">{esc(k)}</span>：{esc(v)}</div>" for k, v in rows if v != "")
        body = (
            f"<section><h2 class=\"ribbon\">{esc(r['name'])}</h2>"
            f"{img_tag('assets/items/' + r['id'] + '.webp', r['name'], 'big-img', prefix='../')}"
            f"<h3>材料</h3><div class=\"minis\">{mats_html}</div>"
            f"<div class=\"dlist\">{dlist}</div>"
            f"<p><a class=\"btn\" href=\"../zukan.html\">図鑑にもどる</a></p></section>"
        )
        write_page(f"item/{r['id']}.html", page(r["name"], "zukan.html", body, depth=1))


    # ---------- 住民 ----------
    res_cards = []
    for r in residents:
        rows = [
            ("性格", r.get("personality", "")), ("いまの活動", r.get("current_activity", "")),
            ("目標", r.get("goal", "")), ("所属", r.get("organization", "")),
            ("大切な出来事", "／".join(r.get("past_important_events", []))),
        ]
        dlist = "".join(f"<div><span class=\"k\">{esc(k)}</span>：{esc(v)}</div>" for k, v in rows if v != "")
        res_cards.append(
            f"<div class=\"card\">{img_tag('assets/residents/' + r['id'] + '.webp', r['name'])}"
            f"<p><b>{esc(r['name'])}</b><br><span class=\"meta\">{esc(r['occupation'])}／{esc(r['residence'])}</span></p>"
            f"<details><summary>人となり</summary><div class=\"dlist\">{dlist}</div></details></div>"
        )
    res_body = (
        "<section><h2 class=\"ribbon\">住民名鑑</h2>"
        "<p class=\"lead\">この世界に暮らす8人。それぞれの目標や、いま取り組んでいることがあります。</p>"
        f"<div class=\"cards\">{''.join(res_cards)}</div></section>"
    )
    write_page("residents.html", page("住民名鑑", "residents.html", res_body))

    # ---------- 日誌 ----------
    day_links = ""
    for d in reversed(hist):
        evs = story_events(d)
        teaser = evs[0] if evs else ""
        day_links += (
            f"<a class=\"daylink\" href=\"day/{d['date']}.html\">"
            f"<span class=\"d\">{esc(display_date(d['date']))}（{esc(d.get('weather', ''))}）</span><br>"
            f"<span class=\"t\">{esc(teaser)}</span></a>"
        )
    journal_body = (
        "<section><h2 class=\"ribbon\">世界の歩み（日誌）</h2>"
        "<p class=\"lead\">創世からの記録です。失敗も成功も、消さずに残しています。</p>"
        f"{day_links if day_links else '<div class=\"panel\">創世のみ</div>'}</section>"
    )
    write_page("journal.html", page("日誌", "journal.html", journal_body))

    for i, d in enumerate(hist):
        prev_link = f"<a class=\"btn sub\" href=\"{hist[i - 1]['date']}.html\">← 前の日</a>" if i > 0 else "<span></span>"
        next_link = f"<a class=\"btn sub\" href=\"{hist[i + 1]['date']}.html\">次の日 →</a>" if i < len(hist) - 1 else "<span></span>"
        body = (
            f"<section><h2 class=\"ribbon\">{esc(display_date(d['date']))}</h2>"
            f"{story_block(d)}"
            f"<div class=\"pager\">{prev_link}{next_link}</div>"
            f"<p style=\"margin-top:14px\"><a class=\"btn\" href=\"../journal.html\">日誌一覧にもどる</a></p></section>"
        )
        write_page(f"day/{d['date']}.html", page(display_date(d["date"]), "journal.html", body, depth=1))

    # ---------- 世界について ----------
    regions_html = "".join(
        f"<div><span class=\"k\">{esc(r['name'])}</span>：{esc(r['description'])}</div>" for r in geo["regions"]
    )
    laws_html = "".join(
        f"<div><span class=\"k\">{esc(l['name'])}</span>：{esc(l['principle'])}</div>" for l in alchemy.get("laws", [])
    )
    about_body = (
        "<section><h2 class=\"ribbon\">この世界について</h2>"
        f"<div class=\"panel\"><h3>器と理</h3><p>{esc(geo.get('container', ''))}</p>"
        f"<p>{esc(geo.get('climate', ''))}</p></div>"
        f"<div class=\"panel\"><h3>主な場所</h3><div class=\"dlist\" style=\"margin:0\">{regions_html}</div></div>"
        f"<div class=\"panel\"><h3>錬金の五法則</h3><div class=\"dlist\" style=\"margin:0\">{laws_html}</div></div>"
        "</section>"
        "<footer>※これは架空世界の創作プロジェクトです。世界・住民・錬金術はすべて架空です。</footer>"
    )
    write_page("about.html", page("世界について", "about.html", about_body))

    # ---------- 世界地図 ----------
    fac_html = ""
    for t in geo.get("towns", []):
        facs = "、".join(f["name"] for f in t.get("facilities", []))
        fac_html += f"<div><span class=\"k\">{esc(t['name'])}</span>：{esc(facs)}</div>"
    map_body = (
        "<section><h2 class=\"ribbon\">世界地図</h2>"
        f"{img_tag('assets/maps/flaskaria_overview.webp', 'フラスカリア全景', 'big-img')}"
        "<p class=\"lead\" style=\"margin-top:8px\">箱庭の全景です。フラスコ時代の姿は「第1章」として記録に残っています。</p>"
        f"<div class=\"panel\"><h3>主な場所</h3><div class=\"dlist\" style=\"margin:0\">{regions_html}</div></div>"
        f"<div class=\"panel\"><h3>街と施設</h3><div class=\"dlist\" style=\"margin:0\">{fac_html}</div></div>"
        "<p><a class=\"btn sub\" href=\"about.html\">世界の成り立ちと五法則</a></p>"
        "</section>"
    )
    write_page("map.html", page("世界地図", "map.html", map_body))


if __name__ == "__main__":
    main()
