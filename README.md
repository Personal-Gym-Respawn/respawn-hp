# Respawn HP · Phase A（公開前レビュー）

既存HPのルート `index.html`、`trainer/`、`assets/` は制作・GitHub Pagesプレビュー用として維持します。
OAuthの公開候補は **`oauth-public/` のみ**です。このブランチは公開・OAuth設定変更・GBP送信を実行しません。

| 場所 | 用途 |
| --- | --- |
| `oauth-public/index.html` | Respawn・運営者・アプリ・問い合わせ候補 |
| `oauth-public/gbp-automation/index.html` | 目的、機能、Googleデータ、権限 |
| `oauth-public/privacy/index.html` | 確認した動作に即したポリシー草案 |
| `oauth-public/404.html` | 不明なURLの案内。PagesのSPAフォールバックを防ぐ |
| `oauth-public/assets/site.css` | 外部読込みのない共通スタイル |
| `oauth-public/_headers`、`robots.txt` | CSP・検索除外の草案設定 |
| `scripts/`、`tests/`、`docs/` | ローカル検証・運用資料。配信対象外 |
| `dist/oauth-public/` | 7ファイル限定のビルド出力。Git対象外 |

Python 3.9以上、標準ライブラリのみ。追加依存・APIキー・課金・OAuth認可は不要です。

```sh
python3 scripts/build_oauth.py
python3 scripts/check_oauth.py
python3 -m unittest discover -s tests -v
python3 scripts/serve_oauth.py
```

ローカル確認は `http://127.0.0.1:8764/`。サーバーはループバックのみで待受け、終了はCtrl+C。
`/__qa__/` はローカル専用のレスポンシブ検証用フレームです。公開用ファイルには含まれません。
このサーバーはフレーム検証のためCSPの `frame-ancestors` と `X-Frame-Options` を省略します。Cloudflare実配信と同一の検証ではありません。

現時点は草案表示・`noindex, nofollow`・robots拒否を維持します。これらはアクセス制限ではありません。
公開可能なポリシーが確定した状態でもなく、ビルド成功は公開承認ではありません。

- [データ取扱い調査](docs/phase-a-data-audit.md)
- [OAuth要件と実装判断](docs/phase-a-oauth-requirements.md)
- [公開前チェックリスト](docs/phase-a-release-checklist.md)
- [デプロイ・運用・ロールバック](docs/phase-a-operations.md)
- [検証記録](docs/phase-a-validation.md)
