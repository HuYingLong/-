# author time:2025-01-06
# author time:2025-01-06
# author time:2025-01-06
import socket
import cv2
import struct
import numpy as np
from ultralytics import YOLO
from PyQt5 import QtCore, QtGui, QtWidgets
import threading
import queue
import time
import sys

# 手势名称与数字映射
class_name_mapping = {
    0: "fist",
    1: "love",
    2: "six",
    3: "eight",
    4: "pray",
    5: "five",
    6: "ok",
    7: "one",
    8: "frame",
    9: "yeat"
}

# 加载YOLO模型
model = YOLO('yolov11/yolo11-keshe4.yaml')
model.load('yolov11/best.pt')

class VideoReceiverThread(QtCore.QThread):
    frame_received = QtCore.pyqtSignal(QtGui.QImage)
    gesture_detected = QtCore.pyqtSignal(str)

    def __init__(self, server_ip, server_port, gesture_queue, parent=None):
        super(VideoReceiverThread, self).__init__(parent)
        self.server_ip = server_ip
        self.server_port = server_port
        self.gesture_queue = gesture_queue
        self.running = False
        self.previous_name = None
        self.repeat_count = 0
        self.last_sent_time = 0
        self.cooldown_period = 2  # 秒

    def run(self):
        self.running = True
        video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            video_socket.connect((self.server_ip, self.server_port))
            print("成功连接到视频服务器，开始接收视频流...")
        except Exception as e:
            print(f"无法连接到视频服务器: {e}")
            return

        payload_size = struct.calcsize("Q")
        data = b""

        while self.running:
            try:
                # 接收视频数据包
                while len(data) < payload_size:
                    packet = video_socket.recv(4 * 1024)
                    if not packet:
                        print("视频服务器断开连接")
                        self.running = False
                        break
                    data += packet
                if not self.running:
                    break

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size:
                    packet = video_socket.recv(4 * 1024)
                    if not packet:
                        print("视频服务器断开连接")
                        self.running = False
                        break
                    data += packet
                if not self.running:
                    break

                frame_data = data[:msg_size]
                data = data[msg_size:]

                # 解码图像并进行手势识别
                np_data = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                if frame is None:
                    print("解码失败")
                    continue

                # 模型推理并处理结果
                results = model(frame, verbose=False)
                detected_gesture = self.process_results(results)

                # 显示图像及检测结果
                annotated_frame = results[0].plot()
                rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                self.frame_received.emit(qt_image)

                # 如果检测到手势，应用连续检测逻辑并放入队列
                if detected_gesture:
                    if detected_gesture == self.previous_name:
                        self.repeat_count += 1
                    else:
                        self.repeat_count = 1
                        self.previous_name = detected_gesture

                    if self.repeat_count >= 3:  # 连续检测三次相同手势
                        current_time = time.time()
                        if current_time - self.last_sent_time >= self.cooldown_period:
                            print(f"检测到稳定手势: {detected_gesture}")
                            gesture_index = list(class_name_mapping.values()).index(detected_gesture)
                            self.gesture_queue.put(str(gesture_index))
                            self.last_sent_time = current_time
                            self.repeat_count = 0  # 重置计数
                else:
                    self.previous_name = None
                    self.repeat_count = 0

            except Exception as e:
                print(f"视频流错误：{e}")
                self.running = False
                break

        video_socket.close()
        print("视频接收线程已关闭")

    def stop(self):
        self.running = False

    def process_results(self, results):
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = box.conf[0].item()
            if conf > 0.85:  # 置信度阈值
                return class_name_mapping.get(cls_id)
        return None

class GestureSenderThread(QtCore.QThread):
    def __init__(self, server_ip, server_port, gesture_queue, parent=None):
        super(GestureSenderThread, self).__init__(parent)
        self.server_ip = server_ip
        self.server_port = server_port
        self.gesture_queue = gesture_queue
        self.running = False
        self.socket = None

    def run(self):
        self.running = True
        self.connect_server()

        while self.running:
            try:
                gesture = self.gesture_queue.get(timeout=1)
                if gesture is None:
                    break  # 接收到结束信号，退出线程
                self.send_gesture(gesture)
                self.gesture_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"发送线程错误：{e}")
                self.connect_server()

        if self.socket:
            self.socket.close()
        print("手势发送线程已关闭")

    def connect_server(self):
        while self.running:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.server_ip, self.server_port))
                print("成功连接到数字交互服务器")
                break
            except Exception as e:
                print(f"无法连接到数字交互服务器: {e}")
                time.sleep(5)  # 等待5秒后重试

    def send_gesture(self, gesture):
        try:
            self.socket.sendall(gesture.encode())
            response = self.socket.recv(1024).decode()
            print(f"机械臂响应：{response}")
        except Exception as e:
            print(f"发送手势错误：{e}")
            self.socket.close()
            self.connect_server()
            # 重新发送手势
            try:
                self.socket.sendall(gesture.encode())
                response = self.socket.recv(1024).decode()
                print(f"机械臂响应：{response}")
            except Exception as re:
                print(f"重新发送手势失败: {re}")

    def stop(self):
        self.running = False
        self.gesture_queue.put(None)  # 发送结束信号
        if self.socket:
            self.socket.close()

class ControlCommandThread(QtCore.QThread):
    def __init__(self, server_ip, server_port, parent=None):
        super(ControlCommandThread, self).__init__(parent)
        self.server_ip = server_ip
        self.server_port = server_port
        self.command_queue = queue.Queue()
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                command = self.command_queue.get(timeout=1)
                if command is None:
                    break
                self.send_command(command)
                self.command_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"控制命令线程错误：{e}")

    def send_command(self, command):
        try:
            control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            control_socket.connect((self.server_ip, self.server_port))
            control_socket.sendall(command.encode())
            response = control_socket.recv(1024).decode()
            print(f"服务器响应: {response}")
            control_socket.close()
        except Exception as e:
            print(f"发送控制命令失败: {e}")

    def enqueue_command(self, command):
        self.command_queue.put(command)

    def stop(self):
        self.running = False
        self.command_queue.put(None)  # 发送结束信号

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("手势识别客户端")
        self.setGeometry(100, 100, 1000, 800)

        # 布局
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        # 视频显示区域
        self.video_label = QtWidgets.QLabel("视频流未开启")
        self.video_label.setFixedSize(800, 600)
        self.video_label.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.video_label)

        # 右侧按钮区域
        self.button_layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.button_layout)

        # 打开摄像头按钮
        self.open_button = QtWidgets.QPushButton("打开摄像头")
        self.open_button.clicked.connect(self.open_camera)
        self.button_layout.addWidget(self.open_button)

        # 关闭摄像头按钮
        self.close_button = QtWidgets.QPushButton("关闭摄像头")
        self.close_button.clicked.connect(self.close_camera)
        self.close_button.setEnabled(False)
        self.button_layout.addWidget(self.close_button)

        # 添加数字按钮
        self.number_button_layout = QtWidgets.QGridLayout()
        self.button_layout.addLayout(self.number_button_layout)

        self.number_buttons = {}
        for i in range(10):
            button = QtWidgets.QPushButton(str(i))
            button.setFixedSize(50, 50)
            button.clicked.connect(self.on_number_button_clicked)
            self.number_buttons[i] = button
            row = i // 3
            col = i % 3
            if i == 9:
                # 将数字9放在最后一行中间
                self.number_button_layout.addWidget(button, 3, 1)
            else:
                self.number_button_layout.addWidget(button, row, col)

        # 发送控制命令线程
        self.control_thread = ControlCommandThread('192.168.1.11', 9982)
        self.control_thread.start()

        # 手势队列
        self.gesture_queue = queue.Queue()

        # 线程
        self.video_thread = None
        self.sender_thread = None

    def open_camera(self):
        # 发送 'open_camera' 命令
        self.control_thread.enqueue_command('open_camera')
        self.open_button.setEnabled(False)
        self.close_button.setEnabled(True)
        print("已发送打开摄像头命令")

        # 启动视频接收线程和手势发送线程
        if not self.video_thread or not self.video_thread.isRunning():
            self.video_thread = VideoReceiverThread('192.168.1.11', 9980, self.gesture_queue)
            self.video_thread.frame_received.connect(self.update_image)
            self.video_thread.start()

            self.sender_thread = GestureSenderThread('192.168.1.11', 9981, self.gesture_queue)
            self.sender_thread.start()
            print("视频接收线程和手势发送线程已启动")

    def close_camera(self):
        # 发送 'close_camera' 命令
        self.control_thread.enqueue_command('close_camera')
        self.open_button.setEnabled(True)
        self.close_button.setEnabled(False)
        print("已发送关闭摄像头命令")

        # 停止视频接收线程
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread.wait()
            self.video_thread = None
            print("视频接收线程已停止")

        # 停止手势发送线程
        if self.sender_thread and self.sender_thread.isRunning():
            self.sender_thread.stop()
            self.sender_thread.wait()
            self.sender_thread = None
            print("手势发送线程已停止")

        # 清空视频显示区域
        self.video_label.clear()
        self.video_label.setText("视频流已关闭")
        self.video_label.setStyleSheet("background-color: black;")

    def on_number_button_clicked(self):
        sender = self.sender()
        if sender:
            number = sender.text()
            print(f"数字按钮 {number} 被点击")
            # 将数字加入手势队列
            self.gesture_queue.put(number)

    def update_image(self, qt_image):
        self.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image).scaled(
            self.video_label.width(),
            self.video_label.height(),
            QtCore.Qt.KeepAspectRatio
        ))

    def closeEvent(self, event):
        # 关闭摄像头和线程
        self.close_camera()
        # 停止控制命令线程
        self.control_thread.stop()
        self.control_thread.wait()
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
