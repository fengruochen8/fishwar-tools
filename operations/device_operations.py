import uiautomator2 as u2
import threading
import random
import time

class DeviceOperations:
    def __init__(self, devices, control_panel):
        self.devices = devices
        self.control_panel = control_panel
        self.stop_event = threading.Event()
        self.threads = []

    def raise_input_field(self, device):
        try:
            print(f"[{device.serial}] 尝试点击新的输入框控件")
            if device(text="说点什么...").exists(timeout=10):
                print(f"[{device.serial}] 找到了新的输入框控件")
                print(f"[{device.serial}] 控件信息: {device(text='说点什么...').info}")
                device(text="说点什么...").click()
                time.sleep(2)
            else:
                print(f"[{device.serial}] 未找到新的输入框控件")
                raise u2.exceptions.UiObjectNotFoundError(
                    {'code': -32002, 'data': "Selector [text='说点什么...']", 'method': 'wait'}
                )
        except u2.exceptions.UiObjectNotFoundError as e:
            print(f"[{device.serial}] 未找到UI控件: {e}")
            raise e

    def enter_text_and_send(self, device, text):
        try:
            print(f"[{device.serial}] 尝试输入内容")
            if device(className="android.widget.EditText").exists(timeout=10):
                device(className="android.widget.EditText").set_text(text)
                print(f"[{device.serial}] 输入内容成功: {text}")
                time.sleep(2)

                print(f"[{device.serial}] 尝试点击发送按钮")
                if device(resourceId="com.ss.android.ugc.aweme:id/j_e").exists(timeout=10):
                    print(f"[{device.serial}] 找到了发送按钮 (com.ss.android.ugc.aweme:id/j_e)")
                    print(f"[{device.serial}] 发送按钮控件信息: {device(resourceId='com.ss.android.ugc.aweme:id/j_e').info}")
                    device(resourceId="com.ss.android.ugc.aweme:id/j_e").click()
                    print(f"[{device.serial}] 点击发送按钮成功 (com.ss.android.ugc.aweme:id/j_e)")
                elif device(resourceId="m.l.live.plugin:id/input_panel_send_view").exists(timeout=10):
                    print(f"[{device.serial}] 找到了发送按钮 (m.l.live.plugin:id/input_panel_send_view)")
                    print(f"[{device.serial}] 发送按钮控件信息: {device(resourceId='m.l.live.plugin:id/input_panel_send_view').info}")
                    device(resourceId="m.l.live.plugin:id/input_panel_send_view").click()
                    print(f"[{device.serial}] 点击发送按钮成功 (m.l.live.plugin:id/input_panel_send_view)")
                else:
                    print(f"[{device.serial}] 未找到发送按钮")
                    raise u2.exceptions.UiObjectNotFoundError(
                        {'code': -32002, 'data': "Selector [resourceId='com.ss.android.ugc.aweme:id/j_e' or 'm.l.live.plugin:id/input_panel_send_view']", 'method': 'wait'}
                    )
                time.sleep(2)
            else:
                print(f"[{device.serial}] 未找到输入框")
                raise u2.exceptions.UiObjectNotFoundError(
                    {'code': -32002, 'data': "Selector [className='android.widget.EditText']", 'method': 'wait'}
                )
        except u2.exceptions.UiObjectNotFoundError as e:
            print(f"[{device.serial}] 未找到UI控件: {e}")
            raise e

    def double_click(self, device, start_time):
        while not self.stop_event.is_set():
            elapsed_time = time.time() - start_time
            if elapsed_time <= 10:
                like_frequency = random.uniform(0.2, 0.5)  # 前10秒每秒点赞2-5次
            elif 10 < elapsed_time <= 25:
                like_frequency = random.uniform(0.25, 1)  # 第11秒到第25秒每秒点赞1-4次
            elif 25 < elapsed_time <= 145:
                like_frequency = random.uniform(0.17, 0.5)  # 第26秒到第145秒每秒点赞2-6次
            else:
                like_frequency = random.uniform(0.14, 0.5)  # 第146秒开始每秒点赞2-7次

            x = random.randint(189, 529)
            y = random.randint(592, 778)
            print(f"[{device.serial}] 开始双击屏幕位置 ({x}, {y})")
            device.double_click(x, y)
            self.control_panel.queue.put(self.control_panel.update_like_count)
            time.sleep(like_frequency)
            if self.stop_event.is_set():
                print(f"[{device.serial}] 收到停止信号")
                break
        print(f"[{device.serial}] 停止点赞操作")

    def start_liking(self, devices):
        self.stop_event.clear()
        self.threads = []
        start_time = time.time()
        for device in devices:
            t = threading.Thread(target=self.double_click, args=(device, start_time))
            t.daemon = True
            self.threads.append(t)
            t.start()
            print(f"[{device.serial}] 点赞线程启动")

    def stop_liking(self):
        self.stop_event.set()
        print("正在停止所有点赞操作...")
        for t in self.threads:
            t.join()
        print("所有点赞操作已停止")