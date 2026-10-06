import ctypes
import ctypes.wintypes
import time

user32 = ctypes.windll.user32

def enum_windows_cb(hwnd, extra):
    if user32.IsWindowVisible(hwnd):
        buf = ctypes.create_unicode_buffer(1024)
        user32.GetWindowTextW(hwnd, buf, 1024)
        title = buf.value
        if any(k in title for k in ["01_", "02_", "03_", "04_", "05_", "HARDWARE", "BENCHMARK", "SMOKE", "LOCUST", "PowerShell"]):
            print(f"Bringing window to front: {title} ({hwnd})")
            user32.keybd_event(0x12, 0, 0, 0) # Alt down
            user32.ShowWindow(hwnd, 9)       # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
            user32.keybd_event(0x12, 0, 0x0002, 0) # Alt up
            time.sleep(0.3)
    return True

cb = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.c_void_p)(enum_windows_cb)
user32.EnumWindows(cb, 0)
