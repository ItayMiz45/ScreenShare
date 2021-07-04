import mss
import socket
from threading import Thread
from zlib import compress
from win32api import GetSystemMetrics

WIDTH, HEIGHT = int(GetSystemMetrics(0)), int(GetSystemMetrics(1))
WIDTH_BIT_LEN = len(str(WIDTH)).bit_length()
HEIGHT_BIT_LEN = len(str(HEIGHT)).bit_length()

RECT = {"top": 0, "left": 0, "width": WIDTH, "height": HEIGHT}

COMPRESSION_LEVEL = 9

LISTENING_PORT = 1234
IP = "192.168.1.18"


def get_img_rgb():
    with mss.mss() as sct:
        img = sct.grab(RECT)

        compress_rgb = compress(img.rgb, COMPRESSION_LEVEL)

    return compress_rgb


def create_listening_socket():
    listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    listening_sock.bind((IP, LISTENING_PORT))

    return listening_sock


def connect_sock(listening_sock: socket.socket):
    listening_sock.listen(1)

    conn, addr = listening_sock.accept()

    return conn, addr


def send_img_data(conn):
    with mss.mss() as sct:
        last = 0

        while True:
            img = sct.grab(RECT)

            img_data = compress(img.rgb, COMPRESSION_LEVEL)

            if img_data == last:
                continue

            last = img_data

            data_len = len(img_data)
            data_bit_len = data_len.bit_length()

            conn.sendall(bytes([data_bit_len]))
            conn.sendall(data_len.to_bytes(data_bit_len, "big"))
            conn.sendall(img_data)


def main():
    # region Creating a socket and waiting for connection
    listening_sock = create_listening_socket()
    print(type(listening_sock))

    print("Waiting for a connection...")

    conn, addr = connect_sock(listening_sock)

    print(f"Connected to {addr[0]}")
    # endregion

    conn.sendall(WIDTH.to_bytes(WIDTH_BIT_LEN, "big"))
    conn.sendall(HEIGHT.to_bytes(HEIGHT_BIT_LEN, "big"))

    last = 0

    # while True:
    thread = Thread(target=send_img_data, args=(conn,))
    thread.start()


if __name__ == '__main__':
    main()

