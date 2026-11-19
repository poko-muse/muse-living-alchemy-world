#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def load(n): return json.loads((ROOT/"world"/n).read_text(encoding="utf-8"))
def item_img(item_id, name):
    # 図鑑アイテム画像が存在する場合だけ <img> を返す（無ければ文字のみ表示）
    if (ROOT/"site"/"assets"/"items"/f"{item_id}.webp").exists():
        return f"<div class=\"card-imgwrap\"><img class=\"item-img\" src=\"assets/items/{item_id}.webp\" alt=\"{name}\" loading=\"lazy\"></div>"
    return ""
def res_img(res_id, name):
    # 住民イラストが存在する場合だけ <img> を返す（無ければ文字のみ表示）
    if (ROOT/"site"/"assets"/"residents"/f"{res_id}.webp").exists():
        return f"<div class=\"card-imgwrap\"><img class=\"item-img\" src=\"assets/residents/{res_id}.webp\" alt=\"{name}\" loading=\"lazy\"></div>"
    return ""
def main():
    state=load("state.json"); residents=load("residents.json"); materials=load("materials.json"); geo=load("geography.json"); recipes=load("recipes.json")
    hist=[]
    hp=ROOT/"world"/"history.jsonl"
    if hp.exists():
        for line in hp.read_text(encoding="utf-8").strip().splitlines():
            if line.strip(): hist.append(json.loads(line))
    news = hist[-1] if hist else {"date":"-","events":["まだ記録がありません"]}
    res_html="".join(f"<div class=\"card\">{res_img(r['id'], r['name'])}<p><b>{r['name']}</b> — {r['occupation']} / {r['residence']}<br><small>{r['personality']}</small></p></div>" for r in residents)
    mat_html="".join(f"<div class=\"card\">{item_img(m['id'], m['name'])}<p><b>{m['name']}</b> ({m['category']}/{m['attribute']}) — {m['origin']} / {m['discovery_status']} / {m['market_value']}Dr</p></div>" for m in materials)
    rec_html="".join(f"<div class=\"card\">{item_img(r['id'], r['name'])}<p><b>{r['name']}</b> ({r['status']})<br><small>{r['effect']}</small></p></div>" for r in recipes)
    hist_html="".join(f"<li>{h['date']}: {'; '.join(h['events'][:3])}</li>" for h in hist) or "<li>創世のみ</li>"
    regions=" → ".join(r["name"] for r in geo["regions"])
    map_img="<div class=\"card-imgwrap\"><img class=\"map-img\" src=\"assets/maps/flaskaria_overview.webp\" alt=\"フラスカリア全景\" loading=\"lazy\"></div>" if (ROOT/"site"/"assets"/"maps"/"flaskaria_overview.webp").exists() else ""
    html=f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>フラスカリア — MUSE LIVING ALCHEMY WORLD</title><style>body{{font-family:sans-serif;margin:16px;line-height:1.7;max-width:720px}}section{{border-top:1px solid #ccc;padding:12px 0}}.cards{{display:flex;flex-wrap:wrap;gap:12px}}.card{{background:#fffaf0;border:1px solid #e7dab9;border-radius:12px;padding:10px;width:208px;box-sizing:border-box}}.card p{{margin:6px 0 0}}.card-imgwrap{{animation:floaty 5s ease-in-out infinite}}.item-img{{display:block;width:100%;height:auto;border-radius:8px;transition:transform .3s ease}}.map-img{{display:block;width:100%;max-width:560px;height:auto;border-radius:12px;margin:0 auto 8px}}.card:hover .item-img{{transform:scale(1.04)}}@keyframes floaty{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}@media (prefers-reduced-motion: reduce){{.card-imgwrap{{animation:none}}.item-img{{transition:none}}}}</style></head><body>
<h1>フラスカリア</h1><p><b>※これは架空世界の創作プロジェクトです。世界・住民・錬金術はすべて架空です。</b></p>
<section><h2>現在の様子</h2><p>日付: {state.get('current_date_display')} / 季節: {state.get('season')} / 天候: {state.get('weather')} / 人口: {state.get('population')}</p></section>
<section><h2>最新ニュース</h2><p>{news.get('date')}: {'; '.join(news.get('events',[]))}</p></section>
<section><h2>地図</h2>{map_img}<p>{regions}</p><p>中央のぽこ丘をくるり川が一周し、コルク森と映し湖が向き合い、フラスコの首が天窓になる。</p></section>
<section><h2>住民名鑑</h2><div class="cards">{res_html}</div></section>
<section><h2>錬金術図鑑（素材）</h2><div class="cards">{mat_html}</div></section>
<section><h2>錬金術図鑑（調合品）</h2><div class="cards">{rec_html}</div></section>
<section><h2>歴史年表</h2><ul>{hist_html}</ul></section>
</body></html>"""
    out=ROOT/"site"/"index.html"; out.write_text(html,encoding="utf-8"); print(f"generated {out}")
if __name__=="__main__": main()
