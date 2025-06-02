# ソフトウェア仕様書：車速連動ドアロック

## 1. はじめに

### 1.1 目的

本仕様書は、車速連動ドアロック機能のソフトウェア仕様を定義する。

### 1.2 適用範囲

本仕様は車両のドアロック制御モジュールに適用する。

### 1.3 用語・略語の定義

- ドアロック：車両のドア施錠機能
- シフトレンジP：パーキングレンジ

### 1.4 参照資料

（必要に応じて記載）

## 2. システム概要

### 2.1 システムの全体像

車両の走行状態に応じて自動的にドアロック/アンロックを行う。

### 2.2 本モジュールの位置付け

車両制御システムの一部として動作し、車速・シフトレンジ信号を受けてドアロック制御を行う。

### 2.3 モジュール構成

| モジュール名         | ファイル名         | 役割・内容                       |
| -------------------- | ------------------ | -------------------------------- |
| ドアロック制御本体   | doorlock_control.c | ドアロック・チャイルドロック制御 |
| ドアロック制御ヘッダ | doorlock_control.h | インターフェース定義             |
| ログ出力             | door_lock_log.txt  | ロック/アンロック履歴出力        |

## 3. 機能仕様

### 3.1 機能概要

・車速が20km/hを超えた場合に自動で全ドアをロックする。
・車両が完全停止し、かつシフトレンジがPになった場合に自動で全ドアをアンロックする。

### 3.2 入出力仕様

#### 3.2.1 入力

- 車速信号（km/h）
- シフトレンジ信号（P/N/D/R等）
- 運転席ロックスイッチ信号（driver_lock_switch：LOCK/UNLOCK）
- 助手席ロックスイッチ信号（passenger_lock_switch：LOCK/UNLOCK）
- 後席ロックスイッチ信号（rear_lock_switch：LOCK/UNLOCK）

#### 3.2.2 出力

- ドアロック制御信号（ロック/アンロック）

### 3.3 詳細処理仕様

#### 3.3.5 手動操作優先・自動制御無効化

- 運転席・助手席・後席いずれかのロックスイッチ値が「前回値から変化した場合のみ」手動操作とみなす。
- 手動操作検出時、`manual_override_timer`を30,000ms（30秒）にセットし、その間は自動制御（車速連動ロック/アンロック）を無効化する。
- タイマは制御周期ごとに減算し、0になったら自動制御を再開する。
- スイッチ値の前回値はstatic変数で管理する。

#### 3.3.4 制御周期

本制御処理（update_door_lock_state関数）は100ms周期（10Hz）で定期的に実行されるものとする。

#### 3.3.1 各関数の処理フロー

- 車速が20km/hを超えたらロック信号を出力
- 車両が停止し、シフトレンジがPになったらアンロック信号を出力

#### 3.3.2 状態遷移・フラグ管理

- ロック状態・アンロック状態は`door_lock_state`フラグで管理する。
- ロック：`vehicle_speed_kph >= 20` かつ現在アンロック状態のときのみLOCKに遷移。
- アンロック：`vehicle_speed_kph == 0` かつ`shift_position == SHIFT_P` かつ現在ロック状態のときのみUNLOCKに遷移。
- それ以外は状態維持とする。

#### 3.3.3 異常系・例外処理

- 車速が負値、またはシフトレンジが不正値の場合は制御を行わず、現状態を維持する。

## 4. インターフェース仕様

### 4.1 外部インターフェース

- 車速・シフトレンジ信号の受信

### 4.2 内部インターフェース

- `DoorLockCommand update_door_lock_state(int vehicle_speed_kph, ShiftPosition shift_position);`
  - 概要：車速・シフトレンジをもとにロック指令を返す関数
  - 引数：`int vehicle_speed_kph`, `ShiftPosition shift_position`
  - 戻り値：`DoorLockCommand`（LOCKまたはUNLOCK）
  - 処理周期：100ms（10Hz）で周期実行

## 5. データ仕様

### 5.1 変数・構造体・定数一覧

- `int vehicle_speed_kph`：車速 [km/h]
- `ShiftPosition shift_position`：シフトレンジ（enum型、定義例は下記参照）
- `DoorLockCommand door_lock_command`：ドアロック指令（enum型、定義例は下記参照）
- `DoorLockState door_lock_state`：現在のロック状態（enum型、定義例は下記参照）
- `DoorLockCommand driver_lock_switch`：運転席ロックスイッチ信号
- `DoorLockCommand passenger_lock_switch`：助手席ロックスイッチ信号
- `DoorLockCommand rear_lock_switch`：後席ロックスイッチ信号
- `int manual_override_timer`：手動操作後の自動制御無効化タイマ（ms単位、static変数）
- `DoorLockHistory history`：ロック/アンロック操作履歴（static変数、構造体例は下記参照）

#### 履歴構造体例

```c
typedef struct {
    DoorLockCommand last_command; // 最終操作（LOCK/UNLOCK）
    uint32_t last_command_time;   // 操作時刻（ms）
    bool is_manual;               // 手動操作かどうか
} DoorLockHistory;
```

#### enum定義例

```c
typedef enum {
    SHIFT_P,
    SHIFT_N,
    SHIFT_D,
    SHIFT_R
} ShiftPosition;

typedef enum {
    LOCK,
    UNLOCK
} DoorLockCommand;

typedef enum {
    LOCKED,
    UNLOCKED
} DoorLockState;
```

### 5.2 マクロ定義

- `MANUAL_OVERRIDE_PERIOD_MS`（30000ms：手動操作後の自動制御無効化時間、例）

- `LOCK_SPEED_THRESHOLD`（20km/h）

### 5.3 テーブル・パラメータ仕様

（本仕様では特になし）

## 6. 制約事項・注意事項

- 本制御処理の実行周期は100ms（10Hz）とする。
- 本仕様では後席センサ連動チャイルドロック機能、降車時自動チャイルドロック解除機能は実装対象外とする。

## 7. 変更履歴

| 日付       | 版数 | 変更内容                                 | 作成者    |
| ---------- | ---- | ---------------------------------------- | --------- |
| 2025-06-02 | 1.0  | 初版作成                                 | ninokin25 |
| 2025-06-02 | 1.1  | ユーザースイッチ入力・手動優先仕様を追加 | ninokin25 |
