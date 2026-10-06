import os
import time

repo = r"D:\LAB_LAB\LAB20\K4-Track02-Day20-DoDinhHoan-02377-ModelServing-Lab"

cmd = f'start powershell -NoExit -Command "Set-Location \'{repo}\'; $env:PYTHONIOENCODING=\'utf-8\'; .\\lab.ps1 probe"'
print("Executing:", cmd)
os.system(cmd)
time.sleep(2)
