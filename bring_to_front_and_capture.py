import ctypes
from ctypes import wintypes
import time
import os
from PIL import ImageGrab

user32 = ctypes.windll.user32
repo_dir = r"D:\LAB_LAB\LAB20\K4-Track02-Day20-DoDinhHoan-02377-ModelServing-Lab"

# Alt key event trick to allow SetForegroundWindow on Windows 10/11
def force_foreground(hwnd):
    user32.keybd_event(0x12, 0, 0, 0) # Alt down
    user32.ShowWindow(hwnd, 3)        # SW_MAXIMIZE
    user32.SetForegroundWindow(hwnd)
    user32.keybd_event(0x12, 0, 0x0002, 0) # Alt up
    time.sleep(1.5)

def capture_target(title_keyword, output_png):
    hwnds = []
    def enum_callback(hwnd, extra):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            if title_keyword.lower() in buf.value.lower() and 'powershell' in buf.value.lower():
                hwnds.append(hwnd)
        return True
    
    cb = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, ctypes.c_void_p)(enum_callback)
    user32.EnumWindows(cb, 0)
    
    if hwnds:
        hwnd = hwnds[0]
        print(f"Found window for {title_keyword}: {hwnd}")
        force_foreground(hwnd)
        img = ImageGrab.grab()
        os.makedirs(os.path.dirname(output_png), exist_ok=True)
        img.save(output_png)
        print(f"Captured real screen for {output_png}")
    else:
        print(f"Could not find window matching {title_keyword}")

def main():
    capture_target("HARDWARE_PROBE", "submission/screenshots/01-hardware-probe.png")
    capture_target("BENCHMARK", "submission/screenshots/02-bench.png")
    capture_target("SMOKE_TEST", "submission/screenshots/03-serve-and-smoke.png")
    capture_target("LOAD_10_USERS", "submission/screenshots/04-locust-10.png")
    capture_target("LOAD_50_USERS", "submission/screenshots/05-locust-50.png")

if __name__ == "__main__":
    main()
