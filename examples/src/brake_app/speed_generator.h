#ifndef SPEED_GENERATOR_H
#define SPEED_GENERATOR_H

#ifdef __cplusplus
extern "C" {
#endif

// コールバック型
typedef void (*SpeedCallback)(int speed);

// 車速生成メインループ
void run_speed_generator(SpeedCallback cb);

#ifdef __cplusplus
}
#endif

#endif // SPEED_GENERATOR_H
