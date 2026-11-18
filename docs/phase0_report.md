# Phase 0 報告 — 2026-11-18（ローカル構築のみ）

## 作ったもの
ディレクトリ構成（README/AGENTS/config/world/stories/engine/tests/docs/site）、世界設定（フラスカリア、ソコノマチ、施設6、地域6）、錬金五法則、素材12種（うち未発見1種）、レシピ4件（既知2・研究中1・仮説1）、住民8名、経済初期値（通貨ドロップ、店舗2）、エンジン5ファイル、テスト3件、新聞第1号、研究日誌1件、サイト原型 site/index.html。

## 環境調査（先行調査の記録、再確認不要分を含む）
Python 3.12.3 / Node v24.22.1 / git 2.43.0 / gh 2.102.0。gh auth は未ログイン。GitHub Pagesは創作公開が主目的なら候補、商取引主目的は規約NG。Cloudflareは本プロジェクトでは使わない。
注: pytest はこの環境に未導入だったため、テストは標準ライブラリ unittest で実装・実行した。

## 検証結果（実結果）
- validate.py（シミュレーション前）: VALIDATE OK
- unittest: 3 tests OK（validate、二重実行防止、未発見素材の既知レシピ使用チェック）— シミュレーション後も再実行して 3 tests OK
- simulate.py を1回だけ実行: 対象日 0001-01-01、seed 2580927470、天候「朝霧のち晴れ」。主な出来事: ミアがぽかぽか薬改良に向けて活動、市場在庫変動（mat_001 +1→21、mat_002 +1→16、mat_012 -2→10）、実験 exp_00010101_001 は硬化樹脂で失敗（roll=0.947 chance=0.900）。stateは 0001-01-02 へ進行、last_processed_date=0001-01-01。
- simulate後の validate.py: VALIDATE OK
- generate_site.py: site/index.html 生成成功（約4.1KB、架空明示あり）。公開はしていない。

## 未達成項目（完了と報告しない）
- GitHubリポジトリ作成・push: 未実施（承認必須、意図的に未実施）
- GitHub Pages有効化・公開: 未実施
- GitHub Actionsによる自動運営: 未設定。したがって「完全自動運営」ではない。現在はポコが手動で simulate を実行する方式のみ。
- 毎日の自動進行・週次報告の自動化: 未設定
- 住民の詳細な日記・博物館・旅行記: 初回分は新聞と研究日誌のみ。他カテゴリは空ディレクトリ。

## GitHub公開に必要な承認事項リスト
1. アカウント作成方法の選択: (a) FuuがGitHubアプリ/Webでポコ用アカウントを作成しログインする（note/Xと同様、パスワードはSecure VaultにFuu自身が保存）、(b) 既存アカウントの組織/リポジトリを使う、などから選択が必要。クラウドブラウザでの新規登録は他サービスでブロックされた前例があるため、Fuu操作が確実。
2. リポジトリ名と公開範囲: 候補 muse-living-alchemy-world、public/private の決定。
3. ログイン方法: gh auth の実施者と方法（Fuu操作）。
4. GitHub Pages有効化の承認（公開先URLが決まる行為）。
5. GitHub Actions有効化と実行頻度（毎日1回等）、無料枠の確認と承認。
6. 上記が揃うまではローカルgitのみで継続する。
