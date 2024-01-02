from pynput import mouse, keyboard
import threading
import time
import ctypes
import tkinter as tk
from tkinter import simpledialog
import pystray
from PIL import Image, ImageDraw
import sys
import os
import winshell
import win32com.client
import atexit

class IdleMonitor:
    def __init__(self, timeout):
        self.timeout = timeout
        self.last_action = time.time()
        self.locked = False

        self.mouse_listener = mouse.Listener(on_move=self.on_action)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_action)

    def on_action(self, *args):
        self.last_action = time.time()
        if self.locked:
            self.locked = False

    def monitor(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()

        while True:
            if time.time() - self.last_action > self.timeout and not self.locked:
                self.lock_screen()
                self.locked = True
            time.sleep(1)

    def lock_screen(self):
        ctypes.windll.user32.LockWorkStation()

def create_image():
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    d = ImageDraw.Draw(image)
    d.rectangle([0, 0, 64, 64], fill="white")
    return image

def quit_program(icon, item):
    icon.stop()
    remove_lock_file()
    sys.exit()

def show_settings(icon, item):
    def run():
        new_timeout = get_user_input()
        if new_timeout:
            monitor.timeout = new_timeout
    threading.Thread(target=run, daemon=True).start()

def get_user_input():
    root = tk.Tk()
    root.withdraw()
    user_input = simpledialog.askinteger("时间范围5-36000秒", "请输入无操作时间（秒）:", minvalue=5, maxvalue=36000)
    root.destroy()
    return user_input if user_input is not None else 60

def create_shortcut_at_startup():
    startup_dir = winshell.startup()
    shortcut_path = os.path.join(startup_dir, "MyApp.lnk")
    target_path = os.path.abspath(__file__)

    if not os.path.exists(shortcut_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.save()

def set_startup(enable):
    if enable:
        create_shortcut_at_startup()
    else:
        # 如果需要，这里可以添加删除快捷方式的逻辑
        pass

def is_already_running():
    lock_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.lock')
    if os.path.exists(lock_file_path):
        return True
    with open(lock_file_path, 'w') as lock_file:
        lock_file.write(str(os.getpid()))
    return False

def remove_lock_file():
    lock_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.lock')
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)

if __name__ == "__main__":
    if is_already_running():
        new_idle_time = get_user_input()
        # 更新设置的逻辑（如果需要）
        sys.exit(0)

    atexit.register(remove_lock_file)
    idle_time = get_user_input()
    monitor = IdleMonitor(idle_time)
    monitor_thread = threading.Thread(target=monitor.monitor, daemon=True)
    monitor_thread.start()

    icon = pystray.Icon("name", create_image(), "自动锁屏", menu=pystray.Menu(
        #pystray.MenuItem('开机启动', lambda icon, item: set_startup(True)),
        #pystray.MenuItem('取消开机启动', lambda icon, item: set_startup(False)),
        pystray.MenuItem('退出', quit_program),
        pystray.MenuItem('设置', show_settings)
    ))
    icon.run()
