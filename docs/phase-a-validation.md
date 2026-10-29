# Phase A 検証記録

実施日：2026-10-30（Asia/Tokyo）。対象は公開前のローカル成果物。デプロイ・DNS・OAuth設定・GBP投稿は実施していません。

## ビルドと追加テスト

```sh
python3 scripts/build_oauth.py
python3 scripts/check_oauth.py
python3 -m unittest discover -s tests -v
git diff --check
```

全コマンド成功。追加したunittestは **11件成功、失敗0**。

- 正常な草案パッケージと、ビルド出力7ファイル・ソースの一致
- 未完成ページ混入、シンボリックリンク、repoルートへの出力の拒否
- リンク切れ、重複ID、フォーム、外部CSS、認証情報パターンの拒否
- 草案の検索除外ヘッダー欠落の拒否

静的チェッカーは4 HTMLの閉じタグ対応、lang、charset、viewport、見出し・mainの数、canonical、OG、description、ARIA参照、skip link、内部リンク/fragment、CSS外部読込、CSP、robotsを検査します。HTML標準への包括的適合やWCAG全項目の認証を意味しません。

## ブラウザ確認

BraveのRespawnプロファイルで指定Googleアカウントを照合した後、localhostを開きました。

| 確認 | 結果 |
| --- | --- |
| トップ、アプリ説明、privacy、404 | 描画確認。主要ページの文字・ナビゲーションを確認 |
| ホーム→アプリ→privacy | 実際にクリックして正しいURLへ遷移 |
| skip link | Enterで `#main` へ移動しmainにfocus |
| 見出し | H1が1つ、H2/H3の順序とランドマークを確認 |
| 文字コントラスト | ホームの計算スタイルから34要素を検査。最小7.22:1、基準未達0（通常4.5:1/大きな文字3:1で判定） |
| 通常幅 | innerWidth1440pxで横はみ出しなし |
| 320 / 390 / 768px | 4ページ×3幅のローカルiframeで実レイアウト確認、横はみ出し0。スクロールバーを除くclientWidthは主に305/375/753px |
| focus | 可視outlineとキーボード操作を確認 |

ブラウザのviewport overrideが対象タブに適用されなかったため、公開物に含めないローカルHTMLフレームで各レイアウト幅を作って検査しました。実機iPhone/Safari・VoiceOverによる全操作確認は行っていません。

## HTTPと公開境界

ローカルQAサーバーで確認：

| パス | status |
| --- | --- |
| `/`、`/gbp-automation/`、`/privacy/`、`/404.html` | 200 |
| `/missing/`、`/trainer/horie/`、`/booking/` | カスタム404 |
| `/scripts/build_oauth.py`、`/.git/config` | カスタム404 |

通常ページと404に `nosniff` と `X-Robots-Tag: noindex, nofollow` を確認。ローカルサーバーはresponsiveフレーム検証用にframe制限を省略するため、CloudflareのCSP/Headers実適用は公開承認後の確認事項です。DNS/TLS/Cloudflare特有のstatusやpath正規化は未検証です。

配信候補はindex、app/index、privacy/index、404、site.css、_headers、robots.txtの7ファイル。予約フォーム・料金表・仮画像・GBPコード・ログ・snapshotは含みません。認証情報・非公開識別子のパターン検査を実施しました。全形式の秘密値を検出する保証ではありません。

## 既存資産の保全

以下4ファイルは作業開始時のorigin/mainとバイト一致を確認しました。

| 既存ファイル | SHA-256先頭12桁 |
| --- | --- |
| index.html | c3f7be23438d |
| trainer/horie/index.html | f0c5a43bf0bc |
| trainer/ihara/index.html | c4a5221709b6 |
| assets/horie-competition.webp | 95abaeef782c |

既存GBP作業ツリーに変更なし。対象のGoogle UIは閲覧だけで、実行ボタン、共有変更、設定変更、認可・token取得は操作していません。

## Gitと未実施範囲

基準main：`5afde908cdde8d6aa9128e1be822ed358bd6d466`。
作業ブランチ：`codex/phase-a-oauth-pages`。mainへ直接コミットせず、Draft PRをmain向けに作成します。

この作業のコミットには `[CF-Pages-Skip]` を付けます。Cloudflare公式のGit連携が解釈するデプロイスキップ指定で、設定を変更せずに不要な配信を抑止するためです。[公式仕様](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/)。テスト自体は上記のとおりローカルで完了しています。

productionブランチ作成、merge、自動merge、Cloudflare接続/デプロイ、DNS変更、正式公開、OAuth公開、追加認可、GBP通信・投稿・削除、課金設定変更は実施していません。GitHub Pagesの設定詳細は今回のAPIでは読めず、変更もしていません。
