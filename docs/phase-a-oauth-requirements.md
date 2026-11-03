# OAuth要件と実装判断

確認日：2026-10-30（Asia/Tokyo）。公式資料の確認と、対象プロジェクトの実設定の確認は区別します。

## Google公式資料から確認した要件

| 区分 | 要点 | 今回の対応 |
| --- | --- | --- |
| ブランド検証時の要件 | ホームは認証不要で閲覧でき、アプリとの関係・機能が分かること | `/` と `/gbp-automation/` に説明。公開後のHTTPS・到達性は未検証 |
| ブランド検証時の要件 | ポリシーをホームと同じドメインで提供し、ホーム・同意画面からリンク | `/privacy/`。同意画面は未変更 |
| データ開示 | Googleデータへのアクセス・用途・保存・共有を実際と一致させる | 確認できたログ・ローカル保存・開発時の共有も開示。未確定条件は草案扱い |
| ドメイン | Authorized domainsに対象の登録可能ドメインを含め、Search Consoleで所有権を確認 | 候補 `respawn-gym.com`。引継ぎでは確認済み、現権限との照合は公開前に実施 |
| 任意 | 利用規約はホームに置く任意リンクとして説明されている | 下記の理由で `/terms/` は作成しない |
| OAuth公開状態 | Testingの外部アプリで非基本スコープを使う場合、発行されるrefresh tokenに7日期限がある | GASの実行継続が必ず7日で切れると一律に断定しない。長期運用の別途検証が必要 |
| 検証の例外 | 少人数の既知利用者によるpersonal useの例外がある | 自社利用だけで自動的に免除とは扱わない。Console上の区分とGoogleの判断を確認 |

出典：
[ブランド検証・ホーム・ポリシー・任意規約・ドメイン・例外](https://developers.google.com/identity/protocols/oauth2/production-readiness/brand-verification)、
[Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy)、
[OAuth 2.0 Policies](https://developers.google.com/identity/protocols/oauth2/policies)、
[Refresh token expiration](https://developers.google.com/identity/protocols/oauth2#expiration)。

`In production`への変更、Brandingの公開、スコープのData Access検証、GBP API利用承認、実投稿の承認は別々の判断です。Webページ作成だけでこれらが完了するものではありません。実際のAudience、Branding、Data Accessでの `business.manage` の分類、Verification Center、クライアント状態は公開前チェックに残します。今回Google Cloudで読んだのはLogging設定で、OAuth設定全体の再監査ではありません。

## 既存の認証を維持

既存GASは `ScriptApp.getOAuthToken()` で実行ユーザーのアクセストークンを取得し、固定したGoogle APIへのAuthorizationヘッダーにのみ利用します。独自OAuthクライアント、callbackルート、クライアントシークレット、refresh token保管庫は追加しません。

[ScriptApp公式](https://developers.google.com/apps-script/reference/script/script-app#getOAuthToken())は、このアクセストークンの期限と、必要時に再取得する動作を説明しています。通常のrefresh token管理の説明を、そのまま自作ストレージの要件へ置き換えません。今回はトークン取得・更新・再認可・実GETも実行していません。

## 利用規約を作らない理由

今回は自社運営用アプリの情報開示ページです。一般利用者の登録、契約、課金、Google認可の受付を実装しません。Googleの上記ブランド検証資料はtermsを任意としています。したがってOAuth要件のためだけに未確定の店舗利用規約を作らず、リンクも置きません。

これは店舗の契約・予約サービス全体に規約が不要という法的判断ではありません。一般提供、予約・入会、第三者店舗向け機能を追加するときに規約と法務表示を再評価します。

## 公開ブロッカー

ポリシーの保存期間・削除手段・共有先は未確定です。GoogleのAPIポリシーでは、限定的なGBP取得コンテンツの保存目的や最長30暦日等の制限があります。通常ログの30日設定だけで全体の適合を証明できません。取得コンテンツ、監査ログ、運営者が作成した原稿を分類し、ローカル資料・Git履歴・会話への転記も含めて対応を決める必要があります。

[GBP API policies / Content storage](https://developers.google.com/my-business/content/policies)を根拠に、運用者が適用範囲と対応を確認します。このPRでは既存データの削除、保存期間変更、自動削除コードの追加は行いません。
