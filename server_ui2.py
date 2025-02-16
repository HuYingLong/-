# author time:2025-01-06

import socket
import cv2
import struct
import threading
import queue
import time
import atexit

# 导入 mechine.py 模块
import mechine

# 创建一个队列用于手势数据的缓冲
gesture_queue = queue.Queue()

# 创建一个事件用于控制摄像头是否开启
camera_active = threading.Event()

def cleanup():
    print("清理资源...")
    # 关闭视频服务器套接字
    try:
        video_socket.close()
        print("视频套接字已关闭")
    except:
        pass
    # 关闭数字交互服务器套接字
    try:
        number_socket.close()
        print("数字套接字已关闭")
    except:
        pass
    # 关闭控制服务器套接字
    try:
        control_socket.close()
        print("控制套接字已关闭")
    except:
        pass
    # 释放摄像头
    try:
        cap.release()
        print("摄像头已释放")
    except:
        pass

atexit.register(cleanup)

# 视频流服务器
def video_server():
    global video_socket, cap
    video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    video_socket.bind(('192.168.1.11', 9980))
    video_socket.listen(5)
    print("视频服务器启动，等待客户端连接...")
    client_socket, addr = video_socket.accept()
    print(f"视频客户端已连接：{addr}")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        client_socket.close()
        video_socket.close()
        return

    frame_skip = 3  # 每三帧发送一次
    frame_count = 0

    try:
        while True:
            if not camera_active.is_set():
                time.sleep(0.1)
                continue  # 等待摄像头开启

            ret, frame = cap.read()
            if not ret:
                print("无法读取帧")
                break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue  # 跳过未满足条件的帧

            # 编码为JPEG格式
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, encoded_image = cv2.imencode('.jpg', frame, encode_param)
            if not result:
                continue

            frame_data = encoded_image.tobytes()
            frame_size = struct.pack("Q", len(frame_data))

            # 发送帧数据
            client_socket.sendall(frame_size + frame_data)
    except Exception as e:
        print(f"视频发送错误：{e}")
    finally:
        cap.release()
        client_socket.close()
        video_socket.close()

# 机械臂动作处理工作线程
def gesture_worker():
    while True:
        gesture = gesture_queue.get()
        if gesture is None:
            break  # 接收到结束信号，退出线程
        try:
            print(f"处理手势：{gesture}")
            # 调用机械臂接口执行动作 gesture是'0'-'9'的字符串
            mechine.move(gesture)
            # 示例：模拟机械臂动作执行
            # time.sleep(5)  # 模拟机械臂动作执行时间
            print(f"机械臂执行动作：{gesture}")
        except Exception as e:
            print(f"机械臂动作执行失败：{e}")
        finally:
            gesture_queue.task_done()

# 数字交互服务器
def number_server():
    global number_socket
    number_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    number_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    number_socket.bind(('192.168.1.11', 9981))
    number_socket.listen(5)
    print("数字交互服务器启动，等待客户端连接...")
    client_socket, addr = number_socket.accept()
    print(f"数字客户端已连接：{addr}")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                print("数字客户端已断开连接")
                break

            # 解码手势数据
            gesture = data.decode()
            print(f"接收到的手势：{gesture}")


            # 将手势数据放入队列
            gesture_queue.put(str(gesture))

            # 回复客户端
            response = f"动作 {gesture} 已接收".encode()
            client_socket.sendall(response)
    except Exception as e:
        print(f"数字交互错误：{e}")
    finally:
        client_socket.close()

# 控制服务器，用于接收打开/关闭摄像头的命令
def control_server():
    global control_socket
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    control_socket.bind(('192.168.1.11', 9982))  # 新的控制端口
    control_socket.listen(5)
    print("控制服务器启动，等待客户端连接...")
    client_socket, addr = control_socket.accept()
    print(f"控制客户端已连接：{addr}")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                print("控制客户端已断开连接")
                break

            command = data.decode().strip().lower()
            print(f"接收到的控制命令：{command}")

            if command == 'open_camera':
                if not camera_active.is_set():
                    camera_active.set()
                    print("摄像头已打开")
                    client_socket.sendall("摄像头已打开".encode())
                else:
                    print("摄像头已在运行")
                    client_socket.sendall("摄像头已在运行".encode())
            elif command == 'close_camera':
                if camera_active.is_set():
                    camera_active.clear()
                    print("摄像头已关闭")
                    client_socket.sendall("摄像头已关闭".encode())
                else:
                    print("摄像头已关闭")
                    client_socket.sendall("摄像头已关闭".encode())
            else:
                print(f"未知命令：{command}")
                client_socket.sendall("未知命令".encode())
    except Exception as e:
        print(f"控制交互错误：{e}")
    finally:
        client_socket.close()
        control_socket.close()

if __name__ == "__main__":
    # 启动手势处理工作线程
    worker_thread = threading.Thread(target=gesture_worker, daemon=True)
    worker_thread.start()

    # 启动视频流、数字交互和控制服务器线程
    video_thread = threading.Thread(target=video_server, daemon=True)
    number_thread = threading.Thread(target=number_server, daemon=True)
    control_thread = threading.Thread(target=control_server, daemon=True)

    video_thread.start()
    number_thread.start()
    control_thread.start()

    video_thread.join()
    number_thread.join()
    control_thread.join()

    # 等待所有手势处理完成
    gesture_queue.put(None)  # 发送结束信号
    worker_thread.join()
