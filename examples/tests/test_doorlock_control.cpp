#include "gtest/gtest.h"
extern "C" {
#include "doorlock_control.h"
}

// テスト用: 手動操作なしで自動ロック/アンロック
TEST(DoorLockControlTest, AutoLockUnlock) {
    // 初期状態: UNLOCKED
    // 20km/h未満→LOCKしない
    EXPECT_EQ(update_door_lock_state(10, SHIFT_D, UNLOCK, UNLOCK, UNLOCK, 0), UNLOCK);
    // 20km/h到達→LOCK
    EXPECT_EQ(update_door_lock_state(20, SHIFT_D, UNLOCK, UNLOCK, UNLOCK, 100), LOCK);
    // 20km/h超→LOCK維持
    EXPECT_EQ(update_door_lock_state(35, SHIFT_D, UNLOCK, UNLOCK, UNLOCK, 200), LOCK);
    // 0km/h+P以外→LOCK維持
    EXPECT_EQ(update_door_lock_state(0, SHIFT_D, UNLOCK, UNLOCK, UNLOCK, 300), LOCK);
    // 0km/h+P→UNLOCK
    EXPECT_EQ(update_door_lock_state(0, SHIFT_P, UNLOCK, UNLOCK, UNLOCK, 400), UNLOCK);
}

// 手動操作でLOCK→30秒間自動制御無効
TEST(DoorLockControlTest, ManualOverrideLock) {
    // LOCKスイッチ操作
    EXPECT_EQ(update_door_lock_state(0, SHIFT_D, LOCK, UNLOCK, UNLOCK, 0), LOCK);
    // 30秒間は自動制御無効
    for (int i = 1; i <= 299; ++i) {
        EXPECT_EQ(update_door_lock_state(35, SHIFT_D, LOCK, UNLOCK, UNLOCK, i*100), LOCK);
    }
    // 30秒経過後は自動制御再開
    EXPECT_EQ(update_door_lock_state(35, SHIFT_D, LOCK, UNLOCK, UNLOCK, 30000), LOCK);
}

// 手動操作でUNLOCK→30秒間自動制御無効
TEST(DoorLockControlTest, ManualOverrideUnlock) {
    // UNLOCKスイッチ操作
    EXPECT_EQ(update_door_lock_state(0, SHIFT_D, UNLOCK, LOCK, UNLOCK, 0), UNLOCK);
    // 30秒間は自動制御無効
    for (int i = 1; i <= 299; ++i) {
        EXPECT_EQ(update_door_lock_state(35, SHIFT_D, UNLOCK, LOCK, UNLOCK, i*100), UNLOCK);
    }
    // 30秒経過後は自動制御再開
    EXPECT_EQ(update_door_lock_state(35, SHIFT_D, UNLOCK, LOCK, UNLOCK, 30000), LOCK);
}

// 異常系: 負の車速や不正シフト
TEST(DoorLockControlTest, AbnormalInput) {
    // LOCK状態にしてから異常値
    update_door_lock_state(25, SHIFT_D, UNLOCK, UNLOCK, UNLOCK, 0);
    EXPECT_EQ(update_door_lock_state(-1, SHIFT_D, UNLOCK, UNLOCK, UNLOCK, 100), LOCK);
    EXPECT_EQ(update_door_lock_state(10, (ShiftPosition)99, UNLOCK, UNLOCK, UNLOCK, 200), LOCK);
}
