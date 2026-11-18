# GitHub 公開準備 — 2026-11-19

この文書は、リポジトリ作成・push・Pages 有効化を実際に行う前の「準備完了」記録です。
2026-11-19 時点で、外部への push・リポジトリ作成・公開はまだ行っていません。
`automatic_operation_configured` は引き続き `false` です（Actions の動作確認後に更新します）。

## 1. 公開方式の決定

- 決定: **公開リポジトリ**で進める
- 経緯: Fuu が公開範囲をポコに一任し、ポコが公開と決定した（2026-11-19）
- 理由:
  1. GitHub Pages を無料で使うには公開リポジトリが必要。
  2. この世界は公開する架空世界の創作資産であり、公開が本来の形である。
  3. 下記スキャンで個人情報・秘密情報が含まれないことを確認済みである。
- リポジトリ候補: `poko-muse/muse-living-alchemy-world`
- 公開予定の Pages URL: https://poko-muse.github.io/muse-living-alchemy-world/ （準備中・未公開）
- 方針の記録先: `config/publication_policy.json`
  - `github_push_approved_by_fu: true`
  - `github_push_requires_fu_approval: false`（承認済みの公開リポジトリへの push について）
  - `repository_visibility_decided_by_poko: "public"`
  - `decision_date: "2026-11-19"`
  - 本リポジトリ以外の新たな外部公開は、引き続き事前承認が必要。

## 2. 公開前スキャン結果（2026-11-19 実施）

対象: リポジトリ全体（`.git` を除く全ファイル）を `grep -RIn` で確認。

| チェック項目 | パターン例 | 結果 |
|---|---|---|
| 岸和田 / Kishiwada | `岸和田\|Kishiwada\|kishiwada` | 一致なし |
| メールアドレス全般 | `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}` | 一致なし |
| ポコ用 Gmail の混入 | `poko.muse` / `poko_muse` / `pokopoko` | 一致なし（置換が必要な箇所は無かった） |
| 秘密情報の語 | `password\|secret\|token\|api_key\|credential\|private_key`（大小無視） | 一致なし |
| 秘密情報の代入らしい記述 | `(key\|token\|secret) = "..."` 形式 | 一致なし |
| 電話番号らしい形式 | 日本の市外局番・携帯形式、`+81` | 一致なし |
| 住所らしい記述 | `住所\|電話\|大阪府\|Osaka\|〒` | 一致なし |

補足:
- 「Fuu」という表記は複数ファイルにあるが、これは本名ではなく、観察者の呼び名として世界設定に意図的に使っているもの（`README.md`、`world/geography.json`、`docs/world_overview.md` 等）。住所・本名・連絡先は含まれていない。
- 架空コンテンツ内の架空のメールアドレス等は存在しなかった。
- 結論: **個人情報・秘密情報は検出されず、公開リポジトリに載せて問題ない状態**と判断した。

## 3. ワークフロー

### 3.1 `.github/workflows/daily-world.yml`（日次シミュレーション）

- 起動: `schedule` 毎日 `37 0 * * *`（00:37 UTC = 09:37 JST）＋ `workflow_dispatch`（手動）
- `permissions: contents: write`（結果コミットの push 用）
- `concurrency: daily-world` で同時実行を防止
- 手順:
  1. `actions/checkout@v4`
  2. `actions/setup-python@v5`（Python 3.12）
  3. **二重実行防止ガード**: `world/state.json` の `last_processed_real_date` が Asia/Tokyo の今日と一致したら、以降をスキップして正常終了する
  4. `python3 engine/simulate.py`
  5. `python3 engine/validate.py`
  6. `python3 engine/generate_site.py`
  7. 変更がある場合のみ、`github-actions[bot]` 名義で `World day <last_processed_date>: auto simulation` というメッセージでコミットして push
- 失敗時: ワークフローはそのステップで停止し、コミット・push ステップには進まない（＝失敗時はコミットしない）。

注記: `engine/simulate.py` 自体にもフラスコ日付・履歴ベースの二重実行防止があり、ガードと二重に効く。

### 3.2 `.github/workflows/pages.yml`（GitHub Pages デプロイ）

- 起動: `main` ブランチへの push のうち `site/**`、`world/**`、`stories/**`、`engine/generate_site.py` の変更時 ＋ `workflow_dispatch`
- `permissions: pages: write` / `id-token: write` / `contents: read`
- 標準構成: `actions/configure-pages@v5` → `actions/upload-pages-artifact@v3`（path: `site`）→ `actions/deploy-pages@v4`
- `concurrency: pages` でデプロイの競合を防止

注記: ローカルの現在のブランチは `master`。リポジトリ作成時はデフォルトブランチを `main` に揃える（リポジトリ作成時に指定するか、初回 push 前に `git branch -M main` する）こと。Pages ワークフローは `main` を前提にしている。

## 4. Pages 有効化手順（想定）

リポジトリ作成・初回 push の後に、GitHub API で Pages の build type を `workflow` に設定する想定:

```bash
gh api --method POST /repos/poko-muse/muse-living-alchemy-world/pages \
  -f build_type=workflow
# 既に Pages が存在する場合は PUT で更新:
gh api --method PUT /repos/poko-muse/muse-living-alchemy-world/pages \
  -f build_type=workflow
```

その後、`pages.yml` を手動実行（または `site/**` 等への push）してデプロイが成功し、
https://poko-muse.github.io/muse-living-alchemy-world/ が表示できることを確認する。

## 5. 残りの手順（親／運営者が実施）

1. `gh` 認証（アカウント `poko-muse`、Secure Vault のログインを使用。認証自体はこの準備作業では未実施）
2. リポジトリ作成: `gh repo create poko-muse/muse-living-alchemy-world --public`（デフォルトブランチは `main` に揃える）
3. ローカルから初回 push（`git remote add origin ...` → `git push -u origin main`）
4. Pages 有効化（上記 4 の API で `build_type=workflow`）
5. `daily-world.yml` を `workflow_dispatch` で手動実行し、(a) ガードが正しく働くこと、(b) コミットが bot 名義で push されること、(c) 失敗時にコミットされないことを確認
6. `pages.yml` の初回デプロイ成功と Pages URL の表示を確認
7. ここまで確認できたら `config/publication_policy.json` と `world/state.json` の `automatic_operation_configured` を `true` に更新し、README の「未設定」表記も実態に合わせて更新する

## 6. ローカル検証（この準備作業で実施、2026-11-19）

- `python3 engine/validate.py`: **VALIDATE OK**
- `python3 engine/generate_site.py`: **生成成功**（`site/index.html` を再生成。内容に変更がなければ git 上も差分なし）
- ワークフロー YAML パース: PyYAML 6.0.1 で `daily-world.yml` / `pages.yml` ともに **PARSE OK**（ジョブ定義まで読み込み確認）
- `config/publication_policy.json`: JSON パース OK、`automatic_operation_configured` は `false` のままであることを確認
- 追加後の再スキャン: メールアドレス形式の一致なし。地名・秘密情報の語については、この文書自身が「検査パターンの説明」としてその文字列を含んでいるため自己言及の一致が出るが、実データとしての個人情報・秘密情報の混入ではない。ワークフロー中の `id-token: write` は GitHub Actions の権限名であり、秘密情報ではない。ワークフローのコミット名義に使う bot の noreply アドレスは GitHub 公式の公開アドレスである。
