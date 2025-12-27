# CLAUDE.md

## プロジェクト概要

obsidian-moc-exporter は、指定した Obsidian MOC（Map of Content）ノートからリンクを再帰的にたどり、参照されているノートと添付ファイルを標準 Markdown 形式でエクスポートする CLI ツール。NotebookLM へのインポート用。

## 開発環境

- Python 3.11
- Conda 環境名: `obsidian-moc-exporter`
- 実行時依存: なし（標準ライブラリのみ）
- 開発時依存: pytest>=7.0

## プロジェクト構成

```
obsidian-moc-exporter/
├── .gitignore
├── CLAUDE.md
├── README.md
├── requirements.txt
├── main.py                   # CLI エントリーポイント、引数パース
├── config/
│   └── config.example.yaml   # 設定例
├── src/
│   └── moc_exporter/
│       ├── __init__.py
│       └── exporter.py       # メインロジック（ObsidianMOCExporter クラス）
└── tests/
    ├── __init__.py
    └── test_exporter.py      # ユニットテスト
```

## コマンド

```bash
# 環境の有効化
conda activate obsidian-moc-exporter

# エクスポーターの実行
python main.py --vault "path/to/vault" --moc "MOC.md" --output "path/to/output" --depth 2
```

## コーディング規約

- README.md およびソースコメントは英語
- 設定ファイルは日本語可
- 複数行文字列には `textwrap.dedent()` を使用

## 変換ルール

| Obsidian 記法 | 変換後 |
|--------------|--------|
| `[[Page]]` | `[Page](Page.md)` |
| `[[Page\|Alias]]` | `[Alias](Page.md)` |
| `![[Note]]`（埋め込み） | `[Note](Note.md)` |
| `![[image.png]]` | `![image](image.png)` |
| `![[image.png\|alt]]` | `![alt](image.png)` |
| `![[image.png\|alt\|300]]` | `![alt](image.png)` |
| `![[image.png\|300]]` | `![image](image.png)` |
| `%%comment%%` | （削除） |
| `#tag` | （保持） |
| Frontmatter | （保持） |
