import tkinter as tk
from tkinter import messagebox
from operations.device_operations import DeviceOperations
import threading
import random
import uiautomator2 as u2
import queue
import time


class ControlPanel:
    def __init__(self, root, device_manager):
        self.root = root
        self.device_manager = device_manager
        self.device_vars = []
        self.liking_running = False
        self.like_count = 0
        self.queue = queue.Queue()
        self.operations = None

        self.create_widgets()
        self.update_device_list()
        self.process_queue()

    def create_widgets(self):
        # 创建设备区域
        self.device_frame = tk.LabelFrame(self.root, text="连接的设备", padx=10, pady=10)
        self.device_frame.pack(fill="x", padx=10, pady=10)

        # 创建按钮区域
        self.button_frame = tk.LabelFrame(self.root, text="控制", padx=10, pady=10)
        self.button_frame.pack(fill="x", padx=10, pady=10)

        self.update_button = tk.Button(self.button_frame, text="更新设备列表", command=self.update_device_list)
        self.update_button.pack(side="left", padx=5)

        self.select_all_button = tk.Button(self.button_frame, text="全选", command=self.select_all)
        self.select_all_button.pack(side="left", padx=5)

        self.random_assign_button = tk.Button(self.button_frame, text="随机分配", command=self.random_assign)
        self.random_assign_button.pack(side="left", padx=5)

        self.raise_input_button = tk.Button(self.button_frame, text="吊起输入框", command=self.raise_input_fields)
        self.raise_input_button.pack(side="left", padx=5)

        tk.Label(self.button_frame, text="输入1或2").pack(side="left", padx=5)
        self.input_entry = tk.Entry(self.button_frame)
        self.input_entry.pack(side="left", padx=5)

        self.send_button = tk.Button(self.button_frame, text="发送", command=self.send)
        self.send_button.pack(side="left", padx=5)

        # 创建点赞区域
        self.like_frame = tk.LabelFrame(self.root, text="点赞控制", padx=10, pady=10)
        self.like_frame.pack(fill="x", padx=10, pady=10)

        self.start_button = tk.Button(self.like_frame, text="开始点赞", command=self.start_liking)
        self.start_button.pack(side="left", padx=5)

        self.like_label = tk.Label(self.like_frame, text="点赞次数: 0")
        self.like_label.pack(side="left", padx=5)

        self.stop_button = tk.Button(self.like_frame, text="停止点赞", command=self.stop_liking)
        self.stop_button.pack(side="left", padx=5)

    def update_device_list(self):
        self.device_manager.update_device_list()
        for widget in self.device_frame.winfo_children():
            widget.destroy()

        self.device_vars = [tk.IntVar() for _ in self.device_manager.devices]

        for i, (device, var) in enumerate(zip(self.device_manager.devices, self.device_vars)):
            if self.device_manager.device_status[device.serial]:
                tk.Checkbutton(self.device_frame, text=f"设备 {i + 1} ({device.serial})", variable=var).pack(
                    anchor=tk.W)
            else:
                tk.Checkbutton(self.device_frame, text=f"设备 {i + 1} ({device.serial}) - 未在线", variable=var,
                               state=tk.DISABLED).pack(anchor=tk.W)

        tk.Label(self.device_frame, text=f"设备总数: {len(self.device_manager.devices)}").pack(anchor=tk.W)

    def select_all(self):
        for var in self.device_vars:
            if var._name != "disabled":
                var.set(1)

    def random_assign(self):
        num_devices = len([var for var in self.device_vars if var._name != "disabled"])
        assignment = [1] * (num_devices // 2) + [2] * (num_devices // 2)
        if num_devices % 2:
            assignment.append(1)
        random.shuffle(assignment)
        index = 0
        for var in self.device_vars:
            if var._name != "disabled":
                var.set(assignment[index])
                index += 1

    def raise_input_fields(self):
        selected_devices = [device for device, var in zip(self.device_manager.devices, self.device_vars) if var.get()]
        if not selected_devices:
            messagebox.showwarning("警告", "未选择任何设备")
            return

        self.operations = DeviceOperations(selected_devices, self)
        for device in selected_devices:
            try:
                self.operations.raise_input_field(device)
            except u2.exceptions.UiObjectNotFoundError as e:
                messagebox.showerror("错误", f"在设备 {device.serial} 上未找到UI元素: {str(e)}")
                return

    def send(self):
        selected_devices = [device for device, var in zip(self.device_manager.devices, self.device_vars) if var.get()]
        if not selected_devices:
            messagebox.showwarning("警告", "未选择任何设备")
            return

        try:
            index = self.input_entry.get()
        except ValueError:
            messagebox.showwarning("警告", "无效的输入")
            return

        self.operations = DeviceOperations(selected_devices, self)
        for device in selected_devices:
            try:
                self.operations.enter_text_and_send(device, index)
            except u2.exceptions.UiObjectNotFoundError as e:
                messagebox.showerror("错误", f"在设备 {device.serial} 上未找到UI元素: {str(e)}")
                return

    def start_liking(self):
        if self.liking_running:
            return

        selected_devices = [device for device, var in zip(self.device_manager.devices, self.device_vars) if var.get()]
        if not selected_devices:
            messagebox.showwarning("警告", "未选择任何设备")
            return

        self.like_count = 0
        self.liking_running = True
        self.operations = DeviceOperations(selected_devices, self)
        self.liking_threads = []
        for device in selected_devices:
            t = threading.Thread(target=self.like_worker, args=(self.operations, device))
            t.daemon = True  # 将线程设置为守护线程
            self.liking_threads.append(t)
            t.start()
            print(f"[{device.serial}] 点赞线程启动")

    def like_worker(self, operations, device):
        start_time = time.time()
        while not operations.stop_event.is_set():
            elapsed_time = time.time() - start_time
            if elapsed_time <= 10:
                like_frequency = random.uniform(0.2, 0.5)  # 前10秒每秒点赞2-5次
            elif 10 < elapsed_time <= 25:
                like_frequency = random.uniform(0.25, 1)  # 第11秒到第25秒每秒点赞1-4次
            elif 25 < elapsed_time <= 145:
                like_frequency = random.uniform(0.17, 0.5)  # 第26秒到第145秒每秒点赞2-6次
            else:
                like_frequency = random.uniform(0.14, 0.5)  # 第146秒开始每秒点赞2-7次

            operations.double_click(device)
            self.queue.put(self.update_like_count)
            time.sleep(like_frequency)
        print(f"[{device.serial}] 点赞线程已停止")

    def update_like_count(self):
        self.like_count += 1
        self.like_label.config(text=f"点赞次数: {self.like_count}")

    def process_queue(self):
        try:
            while True:
                task = self.queue.get_nowait()
                task()
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)

    def stop_liking(self):
        print("停止点赞按钮点击")
        self.liking_running = False
        self.operations.stop_liking()
        for t in self.liking_threads:
            print(f"正在停止线程 {t}")
            t.join()
        print("所有点赞操作已停止")