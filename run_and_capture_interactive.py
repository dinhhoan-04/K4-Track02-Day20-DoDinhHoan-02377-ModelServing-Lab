import subprocess
import time
import ctypes
from ctypes import wintypes
import os
from PIL import ImageGrab

user32 = ctypes.windll.user32
repo_dir = r"D:\LAB_LAB\LAB20\K4-Track02-Day20-DoDinhHoan-02377-ModelServing-Lab"

def run_command_in_interactive_powershell(ps_cmd, output_png, title="PowerShell Lab"):
    print(f"\n=== Executing and capturing for {output_png} ({title}) ===")
    
    full_script = f"""
    $host.ui.RawUI.WindowTitle = '{title}';
    Set-Location '{repo_dir}';
    $env:PYTHONIOENCODING = 'utf-8';
    Write-Host '==> Running: {ps_cmd}' -ForegroundColor Green;
    {ps_cmd};
    """
    
    p = subprocess.Popen(["powershell.exe", "-NoExit", "-Command", full_script])
    
    wait_time = 15 if "benchmark" in ps_cmd or "locust" in ps_cmd else 4
    time.sleep(wait_time)
    
    hwnd = 0
    def enum_cb(h, l):
        nonlocal hwnd
        length = user32.GetWindowTextLengthW(h)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(h, buf, length + 1)
            if title in buf.value:
                hwnd = h
        return True

    cb = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, ctypes.c_void_p)(enum_cb)
    user32.EnumWindows(cb, 0)
    
    if hwnd:
        print(f"Found handle {hwnd} for {title}")
        user32.keybd_event(0x12, 0, 0, 0)
        user32.ShowWindow(hwnd, 3) # SW_MAXIMIZE
        user32.SetForegroundWindow(hwnd)
        user32.keybd_event(0x12, 0, 0x0002, 0)
        time.sleep(1.5)
        
        img = ImageGrab.grab()
        os.makedirs(os.path.dirname(output_png), exist_ok=True)
        img.save(output_png)
        print(f"Saved real screen capture to {output_png}")
        
        user32.PostMessageW(hwnd, 0x0010, 0, 0)
    else:
        print(f"Could not find window {title}, capturing active desktop fallback")
        img = ImageGrab.grab()
        img.save(output_png)

    try:
        p.terminate()
    except Exception:
        pass
    time.sleep(1)

def main():
    # 1. Hardware probe
    run_command_in_interactive_powershell(
        "python labs/00-setup/detect-hardware.py",
        "submission/screenshots/01-hardware-probe.png",
        "01-Hardware-Probe"
    )

    # 2. Bench
    run_command_in_interactive_powershell(
        "python labs/01-measure/benchmark.py",
        "submission/screenshots/02-bench.png",
        "02-Bench-Latency"
    )

    # 3. Serve and smoke
    run_command_in_interactive_powershell(
        "python labs/02-serve/smoke-test.py",
        "submission/screenshots/03-serve-and-smoke.png",
        "03-Serve-And-Smoke"
    )

    # 4. Locust 10
    run_command_in_interactive_powershell(
        ".venv\\Scripts\\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 10 -r 5 -t 15s --host http://localhost:8080 --csv benchmarks/locust-10 --csv-full-history",
        "submission/screenshots/04-locust-10.png",
        "04-Locust-10-Users"
    )

    # 5. Locust 50
    run_command_in_interactive_powershell(
        ".venv\\Scripts\\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 50 -r 25 -t 15s --host http://localhost:8080 --csv benchmarks/locust-50 --csv-full-history",
        "submission/screenshots/05-locust-50.png",
        "05-Locust-50-Users"
    )

if __name__ == "__main__":
    main()
