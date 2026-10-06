import subprocess
import time

repo_dir = r"D:\LAB_LAB\LAB20\K4-Track02-Day20-DoDinhHoan-02377-ModelServing-Lab"

cmds = [
    ("01_HARDWARE_PROBE", "python labs/00-setup/detect-hardware.py"),
    ("02_BENCHMARK", "python labs/01-measure/benchmark.py"),
    ("03_SMOKE_TEST", "python labs/02-serve/smoke-test.py"),
    ("04_LOCUST_10", ".venv\\Scripts\\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 10 -r 5 -t 15s --host http://localhost:8080 --csv benchmarks/locust-10"),
    ("05_LOCUST_50", ".venv\\Scripts\\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 50 -r 25 -t 15s --host http://localhost:8080 --csv benchmarks/locust-50")
]

for title, cmd in cmds:
    ps_command = f"$host.ui.RawUI.WindowTitle='{title}'; Set-Location '{repo_dir}'; $env:PYTHONIOENCODING='utf-8'; {cmd}"
    launcher = f"Start-Process powershell -ArgumentList '-NoExit', '-Command', \"{ps_command}\" -WindowStyle Normal"
    print(f"Launching {title}...")
    subprocess.run(["powershell.exe", "-Command", launcher])
    time.sleep(1.5)

print("Done launching all 5 windows.")
