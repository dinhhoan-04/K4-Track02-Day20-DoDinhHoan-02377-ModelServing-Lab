import subprocess
import time
import ctypes
from ctypes import wintypes
import os
from PIL import ImageGrab

user32 = ctypes.windll.user32
repo_dir = r"D:\LAB_LAB\LAB20\K4-Track02-Day20-DoDinhHoan-02377-ModelServing-Lab"

def capture_native_window(title, ps_script, output_png, wait_sec=5):
    print(f"=== Capturing native window for {output_png} ===")
    
    cmd = [
        "powershell.exe",
        "-NoExit",
        "-Command",
        f"$host.ui.RawUI.WindowTitle='{title}'; Set-Location '{repo_dir}'; $env:PYTHONIOENCODING='utf-8'; {ps_script}"
    ]
    
    proc = subprocess.Popen(cmd)
    time.sleep(wait_sec)
    
    hwnd = user32.FindWindowW(None, title)
    if not hwnd:
        # Fallback search by title containment
        def enum_windows_callback(h, l):
            length = user32.GetWindowTextLengthW(h)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(h, buf, length + 1)
                if title in buf.value:
                    l.append(h)
            return True
        
        c_callback = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, ctypes.c_void_p)(enum_windows_callback)
        hwnds = []
        user32.EnumWindows(c_callback, 0)
        if hwnds:
            hwnd = hwnds[0]
            
    print(f"Window handle found for '{title}': {hwnd}")
    
    if hwnd:
        user32.ShowWindow(hwnd, 9) # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        time.sleep(1)
        
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        print(f"Rect: {rect.left}, {rect.top}, {rect.right}, {rect.bottom}")
        
        # Grab screen at window rect
        img = ImageGrab.grab(bbox=(max(0, rect.left), max(0, rect.top), rect.right, rect.bottom))
        os.makedirs(os.path.dirname(output_png), exist_ok=True)
        img.save(output_png)
        print(f"Saved native screenshot: {output_png}")
        
        user32.PostMessageW(hwnd, 0x0010, 0, 0) # WM_CLOSE
    else:
        print(f"Error: Could not find window '{title}'")
        
    try:
        proc.terminate()
    except Exception:
        pass
    time.sleep(1)

def main():
    # 1. Hardware probe
    capture_native_window(
        "PROBE_NATIVE",
        "python labs/00-setup/detect-hardware.py",
        r"submission/screenshots/01-hardware-probe.png",
        wait_sec=4
    )

    # 2. Bench
    capture_native_window(
        "BENCH_NATIVE",
        "python labs/01-measure/benchmark.py",
        r"submission/screenshots/02-bench.png",
        wait_sec=12
    )

    # 3. Serve & Smoke
    capture_native_window(
        "SMOKE_NATIVE",
        "python labs/02-serve/smoke-test.py",
        r"submission/screenshots/03-serve-and-smoke.png",
        wait_sec=6
    )

    # 4. Locust 10
    capture_native_window(
        "LOCUST10_NATIVE",
        ".venv\\Scripts\\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 10 -r 5 -t 30s --host http://localhost:8080 --csv benchmarks/locust-10 --csv-full-history",
        r"submission/screenshots/04-locust-10.png",
        wait_sec=34
    )

    # 5. Locust 50
    capture_native_window(
        "LOCUST50_NATIVE",
        ".venv\\Scripts\\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 50 -r 25 -t 30s --host http://localhost:8080 --csv benchmarks/locust-50 --csv-full-history",
        r"submission/screenshots/05-locust-50.png",
        wait_sec=34
    )

if __name__ == "__main__":
    main()
