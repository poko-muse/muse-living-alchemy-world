# MUSE LIVING ALCHEMY WORLD — フラスカリア

> これは架空世界の創作プロジェクトです。登場する世界・住民・錬金術はすべて架空です。

巨大なフラスコの中に広がる小さな世界「フラスカリア」。Fuuは観察者、ポコ（Muse）は創造・運営者として、住民の生活と錬金術の発展を構造化データで記録し続けます。

- 世界の正式な状態: `world/*.json` / 履歴: `world/history.jsonl`
- 物語・新聞・研究日誌: `stories/`
- 図鑑・書籍（マネタイズ基盤）: `books/` / 計画は `docs/monetization_plan.md`、編纂は `engine/compile_encyclopedia.py`
- シミュレーション: `engine/`
- 現在は Phase 0（ローカル構築のみ）。GitHub公開・自動運営は未設定です。未達成を完了と報告しません。
- 公開中: https://poko-muse.github.io/muse-living-alchemy-world/ （GitHub Pages、2026-11-19 公開。公開方式の決定・公開前スキャン・ワークフローは `docs/github_setup.md` を参照）

## 動かし方（ローカル）
```bash
python3 engine/validate.py
python3 engine/simulate.py
python3 engine/generate_site.py
python3 -m unittest discover -s tests -v
```
