import uiautomator2 as u2

device_id = "XWX0220A13009539"  # 替换为实际的设备ID
try:
    device = u2.connect(device_id)
    print(f"设备 {device_id} 连接成功")
except u2.exceptions.ConnectError:
    print(f"设备 {device_id} 无法连接")