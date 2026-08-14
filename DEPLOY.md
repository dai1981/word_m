# ロリポップへ「ワンボタン」アップロード設定（r- 用 / 共有 /word/word/）

GitHub の `word/word/` を、ボタン1つでロリポップの `/word/word/` へアップロードします。
s- 用リポジトリと同じフォルダに配信しますが、**「アップロードのみ・削除しない」方式**なので、
互いのページを消しません。

## 1. GitHub に Secrets を3つ登録

リポジトリの **Settings → Secrets and variables → Actions → New repository secret**:

| 名前 | 値 |
|------|----|
| `FTP_SERVER`   | ロリポップのFTPサーバー（ホスト名。先頭に $ は付けない） |
| `FTP_USERNAME` | FTPアカウント |
| `FTP_PASSWORD` | FTPパスワード |

s- 用リポジトリと同じFTP情報でOKです。

## 2. 実行（ワンボタン）

GitHub の **Actions タブ → 「Deploy to Lolipop」→「Run workflow」** を押すだけ。

## 重要

- このデプロイは `mirror -R`（アップロード）で、**`--delete` を付けていません**。
  そのため、同じ `/word/word/` にある s- のページは削除されません。安心して共存できます。
- `protocol`（FTPS）でうまくいかない場合は、deploy.yml の `set ftp:ssl-allow true;` を
  `set ftp:ssl-allow false;` に変えて再実行してください。

---

# 古典（古文単語辞典）のアップロード

同じワークフロー内で、古文用語ページを `/exam/koten/` へアップロードします。

- 生成: `python3 generate_koten.py`（`koten_data/*.json` → `exam/koten/*.html`）
- アップロード先: ローカル `./exam/koten/` → サーバ `/exam/koten/`
- 状態ファイル: `.ftp-deploy-koten.json`（**英単語 `.ftp-deploy-r.json` とは別名**）
- ハブページ `/exam/kotenindex` は **既存のものを使う**ため、このデプロイでは
  アップロード対象に含めません（`/exam/koten/` の外なので触りません）。
- `exam/koten/koten.css` と `exam/koten/koten.js` も同じフォルダにあるので一緒に上がります。

### kotenindex へのリンク追加

`generate_koten.py` は `exam/koten/_links_snippet.html`（各語ページへのリンク集）を
出力します。新しい語を追加したら、この中身を既存 `kotenindex` の一覧箇所へ貼り付けてください
（ハブ本体は自動では書き換えません）。
