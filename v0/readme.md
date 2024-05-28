# 使い方

## インストール

1. サンプルのフォルダ内にEchoentLiteフォルダごとコピーする
2. venvつくる
```
python -m venv venv
```
3. venvで動作させる
```
.\venv\Scripts\activate
```
4. netifaces2をインストールする
```
pip install netifaces2
```

## 実行

1. 実行するときはvnevでやる
```
.\venv\Scripts\activate
```
2. 実行コマンド
```
python exmple_GeneralLighting.py
```

## 終わる
1. venvから抜けるには
```
deactivate
```

## venvで使うpythonのバージョンを変える(for Win)

1. まず使用するバージョンのPythonをインストールする。例えばPython 3.4.0をインストールしたとする。インストール先のPathは
デフォルトで```C:\Python34```となる。
2. Pythonを指定してvenvを作る
```
c:\python34\python -m venv venv
```
