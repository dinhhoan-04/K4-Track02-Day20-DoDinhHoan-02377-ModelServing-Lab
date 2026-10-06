import os
import time

repo = r"D:\LAB_LAB\LAB20\K4-Track02-Day20-DoDinhHoan-02377-ModelServing-Lab"

targets = [
    "probe",
    "bench",
    "smoke",
    "load-10",
    "load-50"
]

for target in targets:
    cmd = f'start powershell -NoExit -Command "Set-Location \'{repo}\'; $env:PYTHONIOENCODING=\'utf-8\'; .\\lab.ps1 {target}"'
    print(f"Popping up window for target: {target}")
    os.system(cmd)
    time.sleep(1.5)

print("Popped up all 5 real PowerShell windows on Windows Desktop.")
