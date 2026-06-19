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
