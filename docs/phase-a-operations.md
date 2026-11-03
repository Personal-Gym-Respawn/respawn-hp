# 運用・デプロイ・ロールバック手順

この文書は将来の手順です。今回実行するのはローカル検証と作業ブランチのコミット・Draft PRのみです。
Cloudflareプロジェクト作成・Git接続・デプロイ、DNS変更、OAuth公開、GBP投稿、有料契約は行いません。

## 公開対象の境界

```text
repository/
  index.html, trainer/, assets/   # 既存制作HP・GitHub Pages（不変）
  oauth-public/                  # 公開候補の静的ページだけ
  scripts/, tests/, docs/         # 公開しない
  dist/oauth-public/             # buildが明示リスト7ファイルだけ生成
```

ビルドは既存HPからコピーしません。公開元に未知ファイル・シンボリックリンクがあれば失敗します。
出力先は固定で、repoルートを指定するCLIオプションはありません。`dist/oauth-public`以外をPagesの出力先にしないことが最重要です。
secretパターン検査は一部の形式を検出する補助であり、秘密情報がない完全な保証ではありません。変更内容と出力一覧のレビューも必要です。

## ローカル検証

READMEの4コマンドを使用します。公開対象の全リンク、404、キーボード、スマートフォン幅、メタ情報を確認します。
サーバーはloopbackのみ、repoルートを配信せず、ディレクトリ一覧を表示しません。`/__qa__/` はローカル用で配信成果物に入りません。
HTTPのローカル確認ではTLS、DNS、Cloudflare固有ルーティング・ヘッダーの適用までは保証できません。

## 承認後のCloudflare Pages Free設定案

| 項目 | 指定値 |
| --- | --- |
| Git repository | Personal-Gym-Respawn/respawn-hp |
| Production branch | **production**（今回作らない。レビュー・承認されたcommitから将来作成） |
| Framework preset | None |
| Root directory | リポジトリルート（空欄） |
| Build command | `python3 scripts/build_oauth.py && python3 scripts/check_oauth.py` |
| Build output directory | **dist/oauth-public** |
| Preview branch deployments | **None** |
| Automatic production branch deployments | 初期は無効。リリースごとに本人承認したcommitのみ手動で配信 |
| Environment / secrets | 不要。OAuth token・Googleクライアント情報を設定しない |
| Functions / bindings | 使用しない |
| Plan | Free。上位プラン・有料オプションを有効にしない |

Cloudflareのビルド環境でPython3が使えることとバージョンを初回承認後に確認します。追加依存のインストールは不要です。
[Static HTML](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/)、[Branch deployment controls](https://developers.cloudflare.com/pages/configuration/branch-build-controls/)、[Free limits](https://developers.cloudflare.com/pages/platform/limits/)を確認済み（2026-10-30）。Freeは月500 builds等の上限があるため、無制限とは案内しません。

mainや作業ブランチをCloudflareの本番に指定しません。previewは既定で非本番ブランチ全件が対象になり得るため、必ずNoneを明示します。新規プロジェクト設定完了時の初回deployは自動本番設定無効とは別に発生し得ます。Git接続・初回セットアップの実行自体に別途公開承認が必要です。

## 初回リリースの順番（未実施）

1. 公開前チェックリストの運用条件を確定し、ページ本文・施行日・問い合わせ先をレビューする。
2. リリース専用差分で草案表示を解消する。検索除外は本人判断で変更し、HTML・_headers・robotsの整合をテストする。canonicalの本番URLも確定する。
3. 承認済みcommitを起点にproductionを作成。既存mainの制作資産を移動・削除せず、GitHub Pagesの公開元・設定も変更しない。
4. 現在のDNS・SSL・本番サイト・GitHub Pagesを記録する。Cloudflare Pages Freeの設定値と出力一覧を二人で確認する。
5. 別途承認後にPages初回デプロイ。pages.dev公開も公開行為として扱う。正常な過去デプロイがない場合の復旧先を先に決める。
6. `pages.dev`上でHTTP status、3ページ、404、CSS、CSP、noindex方針、予約ページ等が存在しないことを確認する。
7. ドメイン・DNSの個別承認後にカスタムドメインを関連付ける。MX/TXT等の既存レコードを保全し、www/HTTPS/証明書と旧URLの維持を確認する。
8. Web公開が完了した後にのみ、別承認で既存Google OAuthのホーム・ポリシーURL等を設定する。本番公開、Branding、Data Accessの各状態を記録する。

mainにPRをマージするとGitHub Pagesのroot公開により追加パスが見える可能性があります。今回マージせず、既存4ファイルとPages設定は不変です。directory分離はCloudflare向けの公開境界であり、同じrepo内のファイルをGitHub全体から非公開にする仕組みではありません。

## 通常運用

- ページの変更は新規ブランチ・レビュー・検証を経由する。productionは承認済みリリースのみ。自動merge禁止。
- 実行者、commit、テスト結果、承認、Cloudflare deployment ID、公開日時、ロールバック先をリリース記録に残す。
- データの保存先・共有・削除ルールやアプリの機能を変える前にポリシーを更新し、OAuth側に必要な手続きを確認する。
- 公開HTML・ログ・PRへtoken、原稿、実行ログ全文、シートsnapshotを貼らない。
- Googleサービス操作前にBrave Respawnと指定アカウントを毎回照合する。権限エラー時は再確認し、OAuth同意や権限拡張で迂回しない。

## ロールバック（別途承認後）

1. 新規デプロイを止め、問題のcommitとdeployment IDを記録する。
2. Cloudflare PagesのDeploymentsから、成功済みの**production** deploymentを選び「Rollback to this deployment」を確認・実行する。preview deploymentは対象外。
3. ホーム・privacy・アプリ説明・404・ヘッダーと旧プレビューを確認する。通常の復旧でDNS・OAuth・GBPデータを変更しない。
4. Gitでは原因コミットをrevertするレビュー差分を作り、テスト後にproductionへ反映する。force push、既存mainのreset、GBP履歴削除は行わない。
5. 初回公開には成功済みproductionがないため、このrollbackは使えない。承認前に旧公開物・DNSを保全し、初回失敗時の停止・旧構成復元の対象を本人が決める。未承認の旧HPを代わりに公開しない。

[Cloudflare Rollbacks](https://developers.cloudflare.com/pages/configuration/rollbacks/)に基づく手順です。ページのrollbackはGoogle認可の取消しや、Google上の投稿・シートデータの復元/削除を意味しません。
