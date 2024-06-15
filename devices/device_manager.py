import uiautomator2 as u2
import subprocess


class DeviceManager:
    def __init__(self):
        self.devices = []
        self.device_status = {}

    def update_device_list(self):
        # 获取当前连接的设备列表
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        device_ids = [line.split()[0] for line in result.stdout.splitlines() if line.endswith("device")]

        self.devices = []
        self.device_status = {}

        for device_id in device_ids:
            try:
                device = u2.connect(device_id)
                self.devices.append(device)
                self.device_status[device_id] = True
            except u2.exceptions.ConnectError:
                self.device_status[device_id] = False

    def check_devices(self):
        for device in self.devices:
            try:
                device.healthcheck()
                self.device_status[device.serial] = True
            except:
                self.device_status[device.serial] = False

    def get_connected_devices(self):
        return [device for device in self.devices if self.device_status[device.serial]]