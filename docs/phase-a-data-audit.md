# Googleデータの取扱い調査（公開前）

調査日：2026-10-30（Asia/Tokyo）。削除責任はPersonal Gym Respawnが負う方針。保持期間と具体的な削除方法は未確定です。
この資料には実データ本文、シート・スクリプトID、GBPのAccount/Location/Post ID、認証情報を転載しません。

## 確認範囲と証拠の強さ

- `respawn-hp` は最新main `5afde908cdde8d6aa9128e1be822ed358bd6d466` から新規作業ブランチを作成。
- 既存GBPリポジトリは読み取りのみ。main `f5d298e3ab8b48eded250bd338a9abc3176148c4` とDraft PR #1のhead `ca497cdcd38cfaa1ab75fe198d9c29d7c016345e` を照合した。ローカルは後者で未コミット変更なし。mainだけでは現行GET検証機能を把握できない。
- 読んだファイル：`src/{readonly,review,approval,gas,engine,core}.js`、3プロファイルのmanifest・生成物、`scripts/{dry-run,build,check,deployment,remote-diff}.js`、README、SPEC、OPERATIONS、VERIFICATION、PRODUCTION_CHECKLIST、CI定義、gitignore。
- ローカルのignored `work/` に67ファイルを確認。JSON25、ログ8、ほかコード保全・資料等。シートsnapshotとDRY RUN結果JSONの構造を確認し、本文や秘密値を出力しなかった。
- 10/22の実GET成功・本番無効は既存検証記録。今回はスクリプト実行・clasp pull/push・OAuth token更新をしないため、remote全コードのハッシュ一致やGET再成功は確認していない。
- Google UIはBraveの既存「Respawn」プロファイルと指定運営アカウントを両方照合してから閲覧。Horieプロファイル・個人アカウントは使用しなかった。共有・コード・設定の変更なし。

## 現設定の読み取り結果

| 対象 | 今回UIで確認した事実 | 限界 |
| --- | --- | --- |
| 対象シートの共有 | 制限付き。共有一覧は所有者1名 | 別コピー、エクスポート、過去の共有先まで否定しない |
| シートのタブ | 投稿管理・設定・承認等の5タブ。復旧ジャーナルは表示なし | 隠しタブ・全データの再取得は行わない |
| GASファイル | Code、GbpReadOnly、manifestが存在。Code先頭はDRY RUN専用 | エディターで全コードを取得・実行していない |
| GAS設定 | 標準Cloudに関連付け。未捕捉例外のCloudログ記録は有効。Script Propertiesに登録項目の表示なし | 実行ログ全文・IAMは未監査 |
| GASトリガー | 現在の所有者の一覧は0件 | 他主体や別プロジェクトの全トリガーは対象外 |
| Cloud Logging | `_Default`: global、30 days、Unlocked。`_Required`: global、400 days、Locked | 両者に同じデータが保存されるとは判断しない |
| ログルーター | 表示されたシンクは_Defaultと_Required、送信先はいずれも同一Google Cloud内のログバケット | 過去のエクスポート、別プロジェクト、全IAM・ログ閲覧者は未監査 |

## データ別の取得・処理・保存

| データ | 根拠と使い方 | 永続化の確認 |
| --- | --- | --- |
| Account | readonly Reader.accounts：name、accountName、type、role | GET検証reportへ名称・ID・roleが出力される |
| Location | Reader.locations：name、title、storeCodeをreadMask指定 | reportへ識別子・名称・店舗コード等が出力される |
| LocalPost | Reader.posts：投稿API応答全体をメモリに取得。本文・日時等で照合 | reportは件数・状態・重複候補ID等。通常GETログが本文全文を必ず保存するとは記載しない |
| シート原稿・承認 | 投稿管理A:U、承認A:J、必要時ジャーナルを読取 | 元データはGoogle Sheets。ローカルsnapshotにも保存記録・ファイルあり |
| DRY RUN | reviewは件数・理由・候補ID・日時をconsoleへ出力。返り値は詳細report | Node版dry-runは詳細reportをファイルまたは標準出力に出す。出力先未指定時のツール会話への流入に注意 |
| 将来の投稿結果 | gas/engineの本番コード。EとQ:T、復旧ジャーナルにpayloadJson、parent、postName、baselineNamesJson等 | 未承認の将来機能。現在のremoteで本番稼働しているとは扱わない |
| 設定・token | GAS設定読取、ScriptApp.getOAuthToken()をGoogle要求内で使用 | 独自refresh token保存処理なし。トークン非保存というシステム全体の保証まではしない |

## 外部への実送信とサービス利用の区別

| サービス | 実際に確認したこと | 未確認・補足 |
| --- | --- | --- |
| Google | GAS・Sheetsで原稿と検証結果を処理。コードのHTTPはGoogle API、将来の画像ホスト確認 | ログの全内容・実保存先の全権限・バックアップを未確認 |
| GitHub | **Google API由来の情報の保存あり**。非公開GBPリポジトリの追跡済みVERIFICATIONにAccount/Location等の識別情報・名称・件数が記載され、remoteのPR資料にも取得件数等がある | gitignoreでworkを除外していても、手で要約した情報はGitに含まれる。非公開は「共有していない」と同義ではない。過去履歴・Actionsログ・artifact・閲覧権限は全監査していない |
| OpenAI / ChatGPT / Work | **取得結果に由来する情報が会話資料に含まれる**。提供されたGBP会話ログにはシート・API検証の内容があり、今回の調査でも既存資料の必要部分・UI表示をツール経由で処理した | Google由来情報が一切送信されなかったとは言えない。全会話・アップロード・Work保存領域・共有リンク・保持条件は確認していない。学習利用の有無や削除完了も断定しない |
| Cloudflare | 今回の静的ページはGoogleデータ取得・送信コードを持たず、Cloudflareへのデプロイも行わない。既存GASにCloudflareへのHTTP送信実装は見つからない | 別システム・手動アップロード・過去運用まで未送信とは証明できない。将来のページ配信ログはWeb閲覧情報で、GBP APIデータと区別 |
| 画像配信先 | 本番用gasに許可ホストへの画像GET確認がある。画像URLをGoogleへ渡す設計 | 現在のGET検証プロファイルでは画像取得を行わない。実ホスト・実取得・共有権限は未確認 |
| その他 | 読んだGASにOpenAI API、広告、解析、外部DBへの送信コードは見つからない。CIは模擬テスト・build/checkのみ | その他の手動作業・拡張機能・別コード・ログ閲覧者の全体は未確認 |

公開HPリポジトリへの転記はこの要約と説明ページに限定し、非公開GBPリポジトリの実データ・識別子・原稿・snapshotをコピーしません。

## 削除手段の調査と残判断（実行していない）

| 保存先 | 技術的な手段・確認候補 | 公開前に決めること |
| --- | --- | --- |
| Sheets | 所有者が対象セル・ファイル・共有を管理。ファイルをゴミ箱へ移動するだけでは完全削除と同義でない。履歴・コピー・バックアップも別対象 | 原稿とAPI取得コンテンツの区分、保持、削除の粒度。Rや復旧履歴を消して重複防止を壊さないこと |
| GAS設定 | Script Propertiesは設定UIで管理可能。現状登録なし。認可取消しとデータ削除は別 | 停止・認可取消し・残存データの削除の順番と責任者 |
| 実行ログ・Cloud Logging | Apps Script実行ログとCloud Loggingを区別。Cloud側はバケット保持・ルーティング・ログ削除の手段があるが、権限・対象ログ・監査ログ制約を確認して計画 | _Default30日設定を全データの削除保証にしない。_Required400日の監査ログを投稿本文と混同しない。期間変更・削除は別途承認 |
| ローカル | 対象ファイル、別ディレクトリのコピー、OSゴミ箱、バックアップ・同期先を特定して削除する手段がある | 保持一覧、担当、期限、再送防止証拠の保全範囲、バックアップ期限。現状、自動削除コードなし |
| GitHub | 新規コミットでファイルを消すだけではGit履歴・PR・Actions・cloneは消えない | 履歴対応が必要か、PR/ログ/artifact/cloneを含めた範囲。今回履歴改変・削除なし |
| OpenAI / Work | 会話・添付・共有リンク・ローカル作業資料をそれぞれ特定。製品・契約上の削除手段と保持条件を本人が確認 | 保存領域の全体、データ区分、削除依頼手段。今回はアカウント設定や会話削除を実施しない |

[Apps Scriptログ](https://developers.google.com/apps-script/guides/logging)、[Cloud Loggingルーティング](https://cloud.google.com/logging/docs/routing/overview)、[Drive削除の仕組み](https://support.google.com/drive/answer/2375102?hl=ja)、[GBPコンテンツ保存条件](https://developers.google.com/my-business/content/policies)を参照。Google側に一般的な保持・削除機能があっても、このアプリの保持運用・削除完了が実装済みという意味ではありません。
