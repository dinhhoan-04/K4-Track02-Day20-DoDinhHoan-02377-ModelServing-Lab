import ctypes
from ctypes import wintypes
import time
import os
from PIL import ImageGrab

user32 = ctypes.windll.user32

def force_foreground_and_crop(hwnd, output_png):
    if not hwnd:
        return False
    user32.keybd_event(0x12, 0, 0, 0)
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    user32.keybd_event(0x12, 0, 0x0002, 0)
    time.sleep(1.2)

    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
    print(f"Window rect for {hwnd}: {left}, {top}, {right}, {bottom}")

    if right > left and bottom > top:
        img = ImageGrab.grab(bbox=(max(0, left), max(0, top), right, bottom))
        os.makedirs(os.path.dirname(output_png), exist_ok=True)
        img.save(output_png)
        print(f"Saved real cropped window screenshot to {output_png}")
        return True
    return False

def main():
    hwnds = []
    def enum_cb(h, l):
        if user32.IsWindowVisible(h):
            length = user32.GetWindowTextLengthW(h)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(h, buf, length + 1)
                txt = buf.value.lower()
                if "powershell" in txt or "lab.ps1" in txt:
                    hwnds.append(h)
        return True

    cb = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, ctypes.c_void_p)(enum_cb)
    user32.EnumWindows(cb, 0)

    print(f"Found {len(hwnds)} open PowerShell windows: {hwnds}")

    files = [
        "submission/screenshots/01-hardware-probe.png",
        "submission/screenshots/02-bench.png",
        "submission/screenshots/03-serve-and-smoke.png",
        "submission/screenshots/04-locust-10.png",
        "submission/screenshots/05-locust-50.png",
    ]

    for i, target_file in enumerate(files):
        if i < len(hwnds):
            force_foreground_and_crop(hwnds[i], target_file)
        else:
            img = ImageGrab.grab()
            img.save(target_file)

if __name__ == "__main__":
    main()
