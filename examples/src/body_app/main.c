#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#endif

#include "doorlock_childlock_control.h"

#define UDP_PORT 50000
#define UDP_BUFSIZE 4

#include "udp_receiver.h"

int main(void) {
    udp_receive_speed();
    return 0;
}
