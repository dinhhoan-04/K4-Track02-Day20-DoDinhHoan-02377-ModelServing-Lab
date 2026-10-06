@echo off
cd /d "D:\LAB_LAB\LAB20\K4-Track02-Day20-DoDinhHoan-02377-ModelServing-Lab"
echo Opening 5 PowerShell windows on your desktop...
start "01_HARDWARE_PROBE" powershell -NoExit -Command "$host.ui.RawUI.WindowTitle='01_HARDWARE_PROBE'; set PYTHONIOENCODING=utf-8; python labs/00-setup/detect-hardware.py"
start "02_BENCHMARK" powershell -NoExit -Command "$host.ui.RawUI.WindowTitle='02_BENCHMARK'; set PYTHONIOENCODING=utf-8; python labs/01-measure/benchmark.py"
start "03_SMOKE_TEST" powershell -NoExit -Command "$host.ui.RawUI.WindowTitle='03_SMOKE_TEST'; set PYTHONIOENCODING=utf-8; python labs/02-serve/smoke-test.py"
start "04_LOCUST_10" powershell -NoExit -Command "$host.ui.RawUI.WindowTitle='04_LOCUST_10'; set PYTHONIOENCODING=utf-8; .venv\Scripts\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 10 -r 5 -t 15s --host http://localhost:8080 --csv benchmarks/locust-10"
start "05_LOCUST_50" powershell -NoExit -Command "$host.ui.RawUI.WindowTitle='05_LOCUST_50'; set PYTHONIOENCODING=utf-8; .venv\Scripts\python.exe -m locust -f labs/02-serve/load-test.py --headless -u 50 -r 25 -t 15s --host http://localhost:8080 --csv benchmarks/locust-50"
