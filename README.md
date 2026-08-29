# Kids Athletics

本プロジェクトは、カメラでプレイヤーの動きを認識しながら遊ぶ体を使ったミニゲームです。
画面上を動く卵やボールに手や体を近づけて触ると、反応が起きる仕組みになっています。

## 概要
- Web カメラを使って身体の位置を検出するゲーム
- MediaPipe を利用した姿勢認識
- タイトル画面からゲームを開始できる
- 卵に触れると回転し、ひよこへ変化してスコアが加算される
- ボールに触れると弾かれる演出がある
- ゲーム中の様子を MP4 形式で録画できる

## ディレクトリ構成
- `main.py`: 実行用の入口
- `src/kids_athletics/`
  - `game.py`: ゲーム本体、生成・更新・当たり判定・描画・録画処理
  - `pose_detector.py`: カメラからの姿勢検出とランドマーク描画
  - `settings.py`: 画面サイズ、速度、判定範囲、音声・画像パスなどの設定
  - `sprite.py`: PNG 画像の重ね合わせ処理
  - `top.py`: タイトル画面と開始処理
  - `__init__.py`: パッケージ定義
- `images/`: 画像素材
  - `egg.png`
  - `hiyoko.png`
- `sounds/`: 音声素材
  - `egg_spin.wav`
  - `bgm.wav`
- `records/`: 録画ファイルの保存先

## 必要な環境
- Python 3.8 以上
- Web カメラ
- OpenCV / MediaPipe / NumPy / pygame

## セットアップ
依存パッケージをインストールしてください。

```powershell
pip install -r requirements.txt
```

## 実行方法
プロジェクトのルートで次を実行します。

```powershell
python main.py
```

`main.py` 側で `src` を読み込む設定をしているため、追加で `PYTHONPATH` を設定する必要はありません。

## PyInstallerでexe化（Windows）
PyInstallerをインストールします。

```powershell
pip install pyinstaller
```

プロジェクトのルートで次のコマンドを実行すると、画像・音声・MediaPipeの姿勢検出モデルを同梱したexeを `exe/` フォルダーに作成できます。

```powershell
python -m PyInstaller --noconfirm --clean --onefile --name kids_athletics --distpath exe --workpath build --paths "src" --add-data "images;images" --add-data "src;src" --add-data "venv\Lib\site-packages\mediapipe\modules;mediapipe/modules" main.py
```

生成された `exe/kids_athletics.exe` と同じフォルダーに `sounds/` を配置し、その中に `bgm.wav` と `egg_spin.wav` を置いてください。実行時はその `sounds/` を優先して読み込みます。

生成された `exe/kids_athletics.exe` を実行してください。`exe/` と `build/` はGitの対象外です。

## 操作方法
- タイトル画面
  - `SPACE`: ゲーム開始
  - `ESC`: 終了
- ゲーム中
  - `ESC`: 終了
  - `r`: 録画開始 / 停止

## ゲームの流れ
- 画面の左右から卵が流れてきます
- 卵に触れると回転アニメーションが始まり、ひよこへ変化します
- 変化が完了するとスコアが加算されます
- 画面上のボールに触れると跳ね返ります
- 手首の座標が検出できない場合は、体のランドマークを代わりに利用します

## 画像と音声の管理
- 画像や音声のパスは `src/kids_athletics/settings.py` で管理しています
- ローカルの固定パスをコードに書き込まず、プロジェクト内の `images/` と `sounds/` を基準に読み込むようにしています
- もしファイルが見つからなくても、ゲーム本体の処理は止まらないように配慮されています

## 録画機能
- ゲーム中に `r` を押すと MP4 形式で保存できます
- 保存先は `records/` フォルダです
- ファイル名は次の形式になります

```text
record_YYYYMMDD_HHMMSS.mp4
```

- 録画中は画面右上に赤い `REC` 表示が出ます

## 設定の変更
主な設定は以下のファイルで調整できます。

- `src/kids_athletics/settings.py`

調整できる項目の例:
- 画面サイズ
- フルスクリーン設定
- 卵の出現間隔
- ボールの落下速度
- 当たり判定の大きさ
- BGM の音量
- Pose 検出の閾値

## 補足
- `SHOW_BODY_POINTS = False` にすると、姿勢の検出点を画面に描画しません
- 録画用の `records/` フォルダは自動で作成されます
- BGM や効果音はファイルが存在する場合にのみ再生されます

## ライセンス
このリポジトリの利用条件については `LICENSE` を参照してください。
