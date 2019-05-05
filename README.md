# RC-S380を用いてFelicaカードの製造IDを読み込むPython3スクリプト

## 概要

カードリーダー[RC-S380](https://www.sony.co.jp/Products/felica/consumer/products/RC-S380.html)を用いて、Felicaカードの製造ID(IDm)、製造パラメータ(PMm)、システムコードを読み込んで表示するプログラム。
Python3で動作する。Python2では動作しない。

* RC-S380限定
* Felica限定
* Python3限定

## 準備

あらかじめ[libusb1ライブラリ](https://pypi.org/project/libusb1/)を[インストール](https://pypi.org/project/libusb1/#installation)しておく。

```bash
$ pip install libusb1
```

## 使い方

1. RC-S380をコンピュータに接続する
2. コンピュータのターミナルから以下を実行する

	```bash
	$ python felica_reader.py
	```
3. FelicaカードをRC-S380の上に置く
