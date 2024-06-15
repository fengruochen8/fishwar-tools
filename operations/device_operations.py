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
                    print(f"[{device.serial}] 找到了发送按钮")
                    print(
                        f"[{device.serial}] 发送按钮控件信息: {device(resourceId='com.ss.android.ugc.aweme:id/j_e').info}")
                    device(resourceId="com.ss.android.ugc.aweme:id/j_e").click()
                    print(f"[{device.serial}] 点击发送按钮成功")
                    time.sleep(2)
                else:
                    print(f"[{device.serial}] 未找到发送按钮")
                    raise u2.exceptions.UiObjectNotFoundError(
                        {'code': -32002, 'data': "Selector [resourceId='com.ss.android.ugc.aweme:id/j_e']",
                         'method': 'wait'}
                    )
            else:
                print(f"[{device.serial}] 未找到输入框")
                raise u2.exceptions.UiObjectNotFoundError(
                    {'code': -32002, 'data': "Selector [className='android.widget.EditText']", 'method': 'wait'}
                )
        except u2.exceptions.UiObjectNotFoundError as e:
            print(f"[{device.serial}] 未找到UI控件: {e}")
            raise e

    def double_click(self, device):
        while not self.stop_event.is_set():
            x = random.randint(390, 742)
            y = random.randint(942, 1335)
            print(f"[{device.serial}] 开始双击屏幕位置 ({x}, {y})")
            device.double_click(x, y)
            self.control_panel.queue.put(self.control_panel.update_like_count)
            time.sleep(random.uniform(1, 2))
            if self.stop_event.is_set():
                print(f"[{device.serial}] 收到停止信号")
                break
        print(f"[{device.serial}] 停止点赞操作")

    def start_liking(self, devices):
        self.stop_event.clear()
        self.threads = []
        for device in devices:
            t = threading.Thread(target=self.double_click, args=(device,))
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