---
title: "テストガイド（テンプレート）"
status: "draft"
version: "0.1.0"
last_updated: "2026-02-10"
---

# テストガイド

このドキュメントは、`docs/INDEX.md` の **TESTING.md** エントリに対応するテンプレートです。
ユニットテスト / 結合テスト / E2E テスト方針をここにまとめます。

## 1. Node 側テスト

- テストランナー: Vitest
- 例: `server/utils/asyncHandler.test.ts`, `server/storage.test.ts`

## 2. Python 側テスト

- テストフレームワーク: pytest
- 例: `libral-core/tests/test_*.py`

> TODO: 実際のコマンド・カバレッジポリシー・CI との連携方法を追記する。

