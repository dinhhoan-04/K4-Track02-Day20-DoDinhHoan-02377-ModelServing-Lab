import subprocess
import time

repo = r"D:\LAB_LAB\LAB20\K4-Track02-Day20-DoDinhHoan-02377-ModelServing-Lab"

cmds = [
    ("1. Hardware Probe", "python labs/00-setup/detect-hardware.py"),
    ("2. Benchmark", "python labs/01-measure/benchmark.py"),
    ("3. Smoke Test", "python labs/02-serve/smoke-test.py"),
    ("4. Load Test 10 Users", ".venv\\Scripts\\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 10 -r 5 -t 30s --host http://localhost:8080 --csv benchmarks/locust-10 --csv-full-history"),
    ("5. Load Test 50 Users", ".venv\\Scripts\\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 50 -r 25 -t 30s --host http://localhost:8080 --csv benchmarks/locust-50 --csv-full-history")
]

for title, cmd_str in cmds:
    ps_code = f"$host.ui.RawUI.WindowTitle='{title}'; Set-Location '{repo}'; $env:PYTHONIOENCODING='utf-8'; {cmd_str}"
    full_cmd = f"powershell -Command \"Start-Process powershell.exe -ArgumentList '-NoExit', '-Command', '{ps_code}'\""
    print(f"Opening visible window: {title}")
    subprocess.run(full_cmd, shell=True)
    time.sleep(2)

print("Opened all interactive terminal windows on desktop.")
