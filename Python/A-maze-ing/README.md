# A-Maze-ing

迷路を生成・探索・可視化する Python プログラムです。
42Tokyo の課題として作成しました。迷路の中央には「42」のピクセルアートが埋め込まれます。

---

## 機能

- **3種類の生成アルゴリズム**: Recursive Backtracker / Kruskal / Prim
- **3種類の探索アルゴリズム**: BFS / 双方向 BFS / A*
- **2種類のディスプレイ**: ASCII（ターミナル）/ MLX（グラフィック、Linux のみ）
- **インタラクティブ操作**: キーボードでリアルタイムに迷路を再生成・色変更・アニメーション再生
- **「42」パターン**: 迷路中央にピクセルアートとして埋め込まれる
- **再現性**: シードを指定することで同じ迷路を再生成可能

---

## 動作環境

- Python 3.10 以上
- MLX 表示を使う場合は Linux 環境と MLX ライブラリが必要（ASCII 表示は macOS でも動作）

---

## セットアップ

仮想環境の使用を推奨します。以下は venv を使った例です。
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Linux（42Tokyo 環境を含む）

```bash
python3 -m venv .venv
source .venv/bin/activate

make install
```

MLX ライブラリを含むすべての依存パッケージが自動でインストールされます。

### macOS（ローカル開発）

macOS では `make install` 内の MLX ビルド処理（Linux 専用）が動作しないため、venv を使って手動でセットアップします。

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -e .
```

> MLX 表示は使用できません。`config.txt` で `DISPLAY=ascii` を指定してください。

---

## 実行

```bash
python3 a_maze_ing.py config.txt
```

### Makefile を使う場合（Linux / 42Tokyo 環境）

```bash
make install   # 依存パッケージと MLX のインストール
make run       # 実行
make debug     # pdb デバッガで実行
make lint      # flake8 + mypy による静的解析
make build     # パッケージビルド（.whl / .tar.gz）
make clean     # キャッシュ・ビルド成果物を削除
```

> macOS では `make install` は動作しません（Linux 専用の MLX ビルド処理が含まれるため）。

---

## 設定ファイル

`KEY=VALUE` 形式のテキストファイルです。`#` で始まる行はコメントとして無視されます。

### 必須項目

| キー | 説明 | 例 |
|------|------|-----|
| `WIDTH` | 迷路の幅（正の整数） | `20` |
| `HEIGHT` | 迷路の高さ（正の整数） | `15` |
| `ENTRY` | 入口座標 `x,y` | `0,0` |
| `EXIT` | 出口座標 `x,y` | `19,14` |
| `OUTPUT_FILE` | 出力ファイルパス | `maze.txt` |
| `PERFECT` | 完全迷路かどうか | `True` / `False` |

### 任意項目

| キー | 説明 | 選択肢 | デフォルト |
|------|------|--------|------------|
| `SEED` | 乱数シード（省略でランダム） | 整数 | なし |
| `ALGORITHM` | 生成アルゴリズム | `recursive_backtracker` / `kruskal` / `prim` | `recursive_backtracker` |
| `DISPLAY` | 表示方式 | `ascii` / `mlx` | `mlx` |
| `SOLVER` | 探索アルゴリズム | `bfs` / `bibfs` / `astar` | `bfs` |

### 設定例

```
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True

SEED=42
ALGORITHM=recursive_backtracker
DISPLAY=ascii
SOLVER=bfs
```

---

## 出力ファイル形式

生成された迷路は以下の形式でテキストファイルに書き出されます。

```
<16進数グリッド（1セル1文字、1行1行）>

<入口座標 x,y>
<出口座標 x,y>
<最短経路文字列（N/E/S/W）>
```

各セルの値は壁の有無をビットフラグで表した 16進数（0〜F）です。

| ビット | 方向 |
|--------|------|
| `0x1` | 北 |
| `0x2` | 東 |
| `0x4` | 南 |
| `0x8` | 西 |

経路文字列は入口から出口までの方向を `N`（北）`E`（東）`S`（南）`W`（西）の連続した文字列で表します。

---

## インタラクティブ操作（ASCII 表示）

| キー | 動作 |
|------|------|
| `r` | 迷路を再生成（シードをインクリメント） |
| `p` | 最短経路の表示切替 |
| `c` | 壁の色を変更 |
| `t` | 「42」パターンの色を変更 |
| `s` | シードを手入力して再生成 |
| `g` | 生成アルゴリズムを切替 |
| `f` | 探索アルゴリズムを切替 |
| `x` | 完全迷路モードの切替 |
| `a` | 生成アニメーションを再生 |
| `v` | 探索アニメーションを再生 |
| `q` | 終了 |

---

## プロジェクト構成

```
A-maze-ing/
├── a_maze_ing.py        # エントリーポイント
├── config.txt           # サンプル設定ファイル
├── mazegen/
│   ├── config.py        # 設定ファイルパーサー
│   ├── generator.py     # 迷路生成・探索エンジン
│   ├── pattern.py       # 「42」パターン埋め込み
│   └── output.py        # 出力ファイル書き込み
├── display/
│   ├── ascii_display.py # ASCII インタラクティブ表示
│   ├── mlx_display.py   # MLX グラフィック表示
│   └── anim.py          # アニメーション処理
└── pyproject.toml
```
