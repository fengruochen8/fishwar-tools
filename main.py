from devices.device_manager import DeviceManager
from gui.control_panel import ControlPanel
import tkinter as tk


def main():
    device_manager = DeviceManager()
    device_manager.update_device_list()  # Initialize the device list

    root = tk.Tk()
    app = ControlPanel(root, device_manager)
    root.mainloop()


if __name__ == "__main__":
    main()