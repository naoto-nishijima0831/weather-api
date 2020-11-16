# Weather API

## 概要
  
気象庁の気象データをベースに、指定したリクエストの集計結果を返却します。
  
## 環境構築手順

* Windows OS のローカル環境で動作させることを前提としています。
* Python Ver3.0 以上が既にインストールされていることを前提とします。

リポジトリをローカルにcloneします。

`git clone https://github.com/naoto-nishijima0831/weather-api`

仮想環境を起動します。

`python -m venv myvenv`

`myvenv\Scripts\activate`

必要なライブラリをインストールします。

`python -m pip install --upgrade pip`

`pip install -r ./weather-api/requirements.txt`

データベースをセットアップします。

`cd weather-api`

`python manage.py migrate`

`python manage.py import`

サーバーを起動します。

`python manage.py runserver`

リクエスト例。

`http://127.0.0.1:8000/weather/summary/?from_date=2020-10-01&to_date=2020-10-31&period=daily&target=daylight&area=Yokohama`
