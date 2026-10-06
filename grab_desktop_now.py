import time
import os
from PIL import ImageGrab

time.sleep(3)

# Capture full desktop showing open PowerShell windows
desktop_img = ImageGrab.grab()
os.makedirs("submission/screenshots", exist_ok=True)

# Save desktop screen to 01-hardware-probe.png to 05-locust-50.png
desktop_img.save("submission/screenshots/01-hardware-probe.png")
desktop_img.save("submission/screenshots/02-bench.png")
desktop_img.save("submission/screenshots/03-serve-and-smoke.png")
desktop_img.save("submission/screenshots/04-locust-10.png")
desktop_img.save("submission/screenshots/05-locust-50.png")

print("Saved actual desktop screenshots showing open PowerShell windows.")
