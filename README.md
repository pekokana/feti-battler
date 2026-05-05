# フェチバトル：デュエル (Feti-Battler Duel)

画像からステータスを生成して戦わせる、バーコードバトラー風の対戦型Webアプリです。
Flet (Python) を使用し、GitHub Pages 上で WASM として動作します。

## デモ
[フェチバトル](https://pekokana.github.io/feti-battler/)

## 特徴
- **画像ハッシュ化アルゴリズム**: 画像のバイナリデータを `SHA256` でハッシュ化し、その値をシードとして HP/ATK/SPD および「素材」を決定します。
- **再現性**: 同じ画像からは常に同じステータスが生成されます。
- **モダンな技術スタック**: 
  - [Flet](https://flet.dev/): Flutter のパワーを Python で利用できるフレームワーク。
  - [Pyodide](https://pyodide.org/): ブラウザ上で Python を動かす技術。
- **非同期バトルエンジン**: `asyncio` を活用し、リアルタイムでログとHPが更新されるバトル演出を実装。

## 制作のきっかけ
友人たちと「フェチ」と「バーコードバトラー」の話で盛り上がった際、「自分の好きな画像がどれくらい強いか可視化できたら面白くない？」というエンジニア特有のノリから誕生しました。

## ローカルでの実行方法

このプロジェクトは `uv` または `pip` で実行できます。

```bash
# 依存関係のインストール
pip install flet

# アプリの起動
python main.py
```

## Web版のビルド方法
GitHub Pages 用にビルドする場合は、以下のコマンドを使用します。

```bash
uv run flet publish ./main.py --base-url /feti-battler/

又は

uv run flet publish ./main.py --base-url /feti-battler/ --web-renderer canvaskit
```

## uv publishでFailed to canonicalize script pathエラーが発生したら・・・

```bash
rm venv

uv vnev
```

## おまけ：つよつよコード

* ea544deaef5dfa721e4e
* 

## ライセンス
このプロジェクトは [MIT License](LICENSE) のもとで公開されています。

---
Produced by [pekokana]
