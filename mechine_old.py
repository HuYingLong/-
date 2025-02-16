# -- coding: utf-8 --
import cv2
import socket
import struct
import threading
import time
from Arm_Lib import Arm_Device

Arm = Arm_Device()
time.sleep(.1)


def shake_head():
    # 控制 3 号和 4 号舵机上下运行
    Arm.Arm_serial_servo_write(3, 0, 1000)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(4, 180, 1000)
    time.sleep(1)

    # 控制 1 号舵机左右运动
    Arm.Arm_serial_servo_write(1, 180, 500)
    time.sleep(.5)
    Arm.Arm_serial_servo_write(1, 0, 1000)
    time.sleep(1)


def nod():
    Arm.Arm_serial_servo_write(4, 0, 1000)
    time.sleep(0.5)
    Arm.Arm_serial_servo_write(4, 180, 1000)
    time.sleep(1)


def dance():
    time_1 = 500
    time_2 = 1000
    time_sleep = 0.5
    Arm.Arm_serial_servo_write(2, 180 - 120, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(3, 120, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(4, 60, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(2, 180 - 135, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(3, 135, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(4, 45, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(2, 180 - 120, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(3, 120, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(4, 60, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(2, 90, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(3, 90, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(4, 90, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(2, 180 - 80, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(3, 80, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(4, 80, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(2, 180 - 60, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(3, 60, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(4, 60, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(2, 180 - 45, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(3, 45, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(4, 45, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(2, 90, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(3, 90, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(4, 90, time_1)
    time.sleep(.001)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(4, 20, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(6, 150, time_1)
    time.sleep(.001)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(4, 90, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(6, 90, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(4, 20, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(6, 150, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(4, 90, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(6, 90, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(1, 0, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(5, 0, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(3, 180, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(4, 0, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(6, 180, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(6, 0, time_2)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(6, 90, time_2)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(1, 90, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(5, 90, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(3, 90, time_1)
    time.sleep(.001)
    Arm.Arm_serial_servo_write(4, 90, time_1)
    time.sleep(time_sleep)


def scissors():
    time_1 = 500
    time_2 = 500
    time_sleep = 0.5
    Arm.Arm_serial_servo_write(4, 90, time_1)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(5, 180, time_2)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(6, 0, time_2)
    time.sleep(time_sleep)
    Arm.Arm_serial_servo_write(6, 90, time_2)
    time.sleep(time_sleep)


def circle():
    Arm.Arm_serial_servo_write(1, 0, 1000)
    time.sleep(1)
    Arm.Arm_serial_servo_write(1, 180, 1000)
    time.sleep(1)


def switch_case(case):
    switch_dict = {
        '0': 'shake_head()',
        '1': 'nod()',
        '2': 'dance()',
        '3': 'circle()',
        '4': 'scissors()'
    }
    return switch_dict.get(case, 'print("default")')


def move(received_data):
    Arm.Arm_serial_servo_write6(90, 90, 90, 0, 90, 90, 500)
    time.sleep(1)
    code = switch_case(received_data)
    exec(code)
    # 控制舵机恢复初始位置
    Arm.Arm_serial_servo_write6(90, 90, 90, 0, 90, 90, 1000)
    time.sleep(1.5)


class RaspberryPiServer:
    def __init__(self, host_ip, host_port, camera_index=0):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.host_ip = host_ip
        self.host_port = host_port
        self.camera_index = camera_index
        Arm.Arm_serial_servo_write6(90, 90, 90, 0, 90, 90, 500)

        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 20)
        #         self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -20)
        self.client_socket = None

    def start_server(self):
        while True:
            try:
                self.server_socket.bind((self.host_ip, self.host_port))
                self.server_socket.listen(5)
                print(f"[*] 开始监听 {self.host_ip}:{self.host_port}")

                while True:
                    try:
                        self.client_socket, addr = self.server_socket.accept()
                        print(f"[*] 接受来自 {addr} 的连接")

                        # 创建两个线程，一个用于发送视频流，一个用于接收数据
                        send_thread = threading.Thread(target=self.send_video)
                        receive_thread = threading.Thread(target=self.receive_data)

                        # 启动线程
                        send_thread.start()
                        receive_thread.start()

                        # 等待两个线程结束
                        send_thread.join()
                        receive_thread.join()

                    except socket.error as e:
                        print(f"Socket error: {e}")
                        # 关闭连接
                        if self.client_socket:
                            self.client_socket.close()

                    except Exception as e:
                        print(f"Error in start_server: {e}")
                        continue

            except Exception as e:
                print(f"Error in start_server: {e}")

            finally:
                # 关闭旧的服务器套接字
                self.server_socket.close()
                # 创建一个新的服务器套接字
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind((self.host_ip, self.host_port))
                self.server_socket.listen(5)
                print(f"[*] 开始监听 {self.host_ip}:{self.host_port}")

    def send_video(self):
        try:
            while True:
                ret, frame = self.cap.read()
                frame = cv2.resize(frame, (640, 480))
                #                frame = cv2.resize(frame, (int(frame.shape[1]/4), int(frame.shape[0]/4)))

                # 将图像编码为JPEG格式
                _, img_encoded = cv2.imencode('.jpg', frame)

                # 将图像数据转换为字符串
                img_str = img_encoded.tobytes()

                # 计算图像大小
                size = len(img_str)
                self.client_socket.sendall(struct.pack(">L", size) + img_str)
        except Exception as e:
            print(f"Error in send_video: {e}")

    def receive_data(self):
        try:
            while True:
                # 接收客户端发来的数据并打印出来
                received_data = self.client_socket.recv(1024).decode()
                received_data = received_data[0]
                print(f"Received from client: {received_data}")

                move(received_data)
                #                 end_data='0xee'
                #                 self.client_socket.sendall(end_data)

                received_data = '-1'
                # time.sleep(5)
        except Exception as e:
            print(f"Error in receive_data: {e}")

    def save_to_txt(self, data):
        with open('result.txt', 'a') as file:
            file.write(data + '\n')


if __name__ == "__main__":
    host_ip = '192.168.137.249'  # 树莓派的IP地址
    host_port = 9999

    raspberry_pi_server = RaspberryPiServer(host_ip, host_port)
    raspberry_pi_server.start_server()
