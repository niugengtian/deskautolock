因为没锁屏挨了骂，所以写一个自动锁屏工具，无毒无害，源码奉献。



#安装需要的包


pip install pynput pyinstaller winshell freeze pystray pywin32



#编译成exe文件


pyinstaller --onefile --noconsole --hidden-import=win32con .\autolockdesk.py
