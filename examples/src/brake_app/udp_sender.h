#ifndef UDP_SENDER_H
#define UDP_SENDER_H

#ifdef _WIN32
#include <winsock2.h>
#else
#include <netinet/in.h>
#endif

// UDP送信構造体
typedef struct {
#ifdef _WIN32
    SOCKET sock;
#else
    int sock;
#endif
    struct sockaddr_in addr;
} UdpSender;

// 初期化（IPアドレス・ポート指定）
int udp_sender_init(UdpSender *sender, const char *ip, int port);
// 終了処理
void udp_sender_close(UdpSender *sender);
// 速度送信
int udp_send_speed(UdpSender *sender, int speed);

#endif // UDP_SENDER_H
