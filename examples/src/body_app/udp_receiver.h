#ifndef UDP_RECEIVER_H
#define UDP_RECEIVER_H


// UDP受信スレッドを起動し、最新車速値を保持する
void start_udp_speed_receiver(void);

// 直近で受信した車速値（km/h）を取得する
int get_latest_vehicle_speed(void);

#endif // UDP_RECEIVER_H
