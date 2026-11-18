# AGENTS.md — フラスカリア運営ルール
- 正式な状態は world/*.json、履歴は world/history.jsonl。物語だけを記憶にしない。
- 同一フラスコ日付を二重処理しない。失敗時は last_processed_date の直前から再開。
- 未発見素材を意図的に使わない（知識の門）。
- 過去の出来事を無かったことにしない。
- 外部公開・GitHubアカウント作成は Fuu の事前承認が必要。公開リポジトリ（poko-muse/muse-living-alchemy-world）への push は、2026-11-19 に Fuu の一任で公開決定済み・承認済み（詳細は config/publication_policy.json と docs/github_setup.md）。それ以外の新たな外部公開は引き続き事前承認が必要。
- Cloudflare はこのプロジェクトでは使わない。
