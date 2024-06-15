import uiautomator2 as u2
import time


def test_device_operations(device_id):
    try:
        device = u2.connect(device_id)
        print(f"已连接到设备 {device_id}")

        # 尝试找到并点击吊起输入框的控件
        if device(resourceId="com.ss.android.ugc.aweme:id/f6f").exists:
            print("找到了吊起输入框的控件，恭喜！")
            print("控件信息: ", device(resourceId="com.ss.android.ugc.aweme:id/f6f").info)
            device(resourceId="com.ss.android.ugc.aweme:id/f6f").click()
            time.sleep(2)  # 等待2秒
        else:
            print("未找到吊起输入框的控件")

        # 尝试找到并点击输入框
        if device(resourceId="com.ss.android.ugc.aweme:id/f8w").exists:
            print("找到了输入框，恭喜！")
            print("控件信息: ", device(resourceId="com.ss.android.ugc.aweme:id/f8w").info)
            device(resourceId="com.ss.android.ugc.aweme:id/f8w").set_text("1")
            time.sleep(2)  # 等待2秒
        else:
            print("未找到输入框")

        # 尝试找到并点击发送按钮
        if device(resourceId="com.ss.android.ugc.aweme:id/j_e").exists:
            print("找到了发送按钮，恭喜！")
            print("控件信息: ", device(resourceId="com.ss.android.ugc.aweme:id/j_e").info)
            device(resourceId="com.ss.android.ugc.aweme:id/j_e").click()
            time.sleep(2)  # 等待2秒
        else:
            print("未找到发送按钮")

    except u2.exceptions.ConnectError:
        print(f"无法连接到设备 {device_id}")
    except u2.exceptions.UiObjectNotFoundError as e:
        print(f"未找到UI控件: {e}")


if __name__ == "__main__":
    device_id = "XWX0220A13009539"  # 替换为实际的设备ID
    test_device_operations(device_id)