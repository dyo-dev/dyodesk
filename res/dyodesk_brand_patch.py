from pathlib import Path
import shutil


SOURCE_DIR = Path("res")

FILES = {
    SOURCE_DIR / "dyodesk_logo.png": [
        Path("flutter/assets/logo.png"),
        Path("flutter/assets/logo_light.png"),
        Path("flutter/assets/logo_dark.png"),
    ],
    SOURCE_DIR / "dyodesk_icon.png": [
        Path("flutter/assets/icon.png"),
        Path("res/icon.png"),
    ],
    SOURCE_DIR / "dyodesk_icon.ico": [
        Path("flutter/windows/runner/resources/app_icon.ico"),
    ],
}


for source, destinations in FILES.items():
    if not source.exists():
        raise FileNotFoundError(
            f"DyoDesk marka dosyası bulunamadı: {source}"
        )

    for destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        print(f"Uygulandı: {source} -> {destination}")

print("DyoDesk logo ve Windows ikonları başarıyla uygulandı.")
