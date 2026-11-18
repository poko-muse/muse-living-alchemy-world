#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def load(n): return json.loads((ROOT/"world"/n).read_text(encoding="utf-8"))
def main():
    state=load("state.json"); residents=load("residents.json"); materials=load("materials.json"); geo=load("geography.json")
    hist=[]
    hp=ROOT/"world"/"history.jsonl"
    if hp.exists():
        for line in hp.read_text(encoding="utf-8").strip().splitlines():
            if line.strip(): hist.append(json.loads(line))
    news = hist[-1] if hist else {"date":"-","events":["まだ記録がありません"]}
    res_html="".join(f"<li><b>{r['name']}</b> — {r['occupation']} / {r['residence']}<br><small>{r['personality']}</small></li>" for r in residents)
    mat_html="".join(f"<li><b>{m['name']}</b> ({m['category']}/{m['attribute']}) — {m['origin']} / {m['discovery_status']} / {m['market_value']}Dr</li>" for m in materials)
    hist_html="".join(f"<li>{h['date']}: {'; '.join(h['events'][:3])}</li>" for h in hist) or "<li>創世のみ</li>"
    regions=" → ".join(r["name"] for r in geo["regions"])
    html=f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>フラスカリア — MUSE LIVING ALCHEMY WORLD</title><style>body{{font-family:sans-serif;margin:16px;line-height:1.7;max-width:720px}}section{{border-top:1px solid #ccc;padding:12px 0}}</style></head><body>
<h1>フラスカリア</h1><p><b>※これは架空世界の創作プロジェクトです。世界・住民・錬金術はすべて架空です。</b></p>
<section><h2>現在の様子</h2><p>日付: {state.get('current_date_display')} / 季節: {state.get('season')} / 天候: {state.get('weather')} / 人口: {state.get('population')}</p></section>
<section><h2>最新ニュース</h2><p>{news.get('date')}: {'; '.join(news.get('events',[]))}</p></section>
<section><h2>地図（テキスト図）</h2><p>{regions}</p><p>中央のぽこ丘をくるり川が一周し、コルク森と映し湖が向き合い、フラスコの首が天窓になる。</p></section>
<section><h2>住民名鑑</h2><ul>{res_html}</ul></section>
<section><h2>錬金術図鑑（素材）</h2><ul>{mat_html}</ul></section>
<section><h2>歴史年表</h2><ul>{hist_html}</ul></section>
</body></html>"""
    out=ROOT/"site"/"index.html"; out.write_text(html,encoding="utf-8"); print(f"generated {out}")
if __name__=="__main__": main()
