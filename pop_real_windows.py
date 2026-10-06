import subprocess
import time

repo = r"D:\LAB_LAB\LAB20\K4-Track02-Day20-DoDinhHoan-02377-ModelServing-Lab"

cmds = [
    ("HARDWARE_PROBE", "python labs/00-setup/detect-hardware.py"),
    ("BENCHMARK", "python labs/01-measure/benchmark.py"),
    ("SMOKE_TEST", "python labs/02-serve/smoke-test.py"),
    ("LOAD_10_USERS", ".venv\\Scripts\\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 10 -r 5 -t 30s --host http://localhost:8080 --csv benchmarks/locust-10 --csv-full-history"),
    ("LOAD_50_USERS", ".venv\\Scripts\\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 50 -r 25 -t 30s --host http://localhost:8080 --csv benchmarks/locust-50 --csv-full-history")
]

for title, cmd_str in cmds:
    full_cmd = f'cmd /c start "{title}" powershell -NoExit -Command "Set-Location \'{repo}\'; $env:PYTHONIOENCODING=\'utf-8\'; {cmd_str}"'
    print(f"Opening window for: {title}")
    subprocess.run(full_cmd, shell=True)
    time.sleep(1.5)

print("Popped up all 5 real PowerShell windows on Windows Desktop.")
