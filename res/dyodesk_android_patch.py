from pathlib import Path
import shutil


MANIFEST = Path(
    "flutter/android/app/src/main/AndroidManifest.xml"
)
BUILD_GRADLE = Path(
    "flutter/android/app/build.gradle"
)
STRINGS = Path(
    "flutter/android/app/src/main/res/values/strings.xml"
)

ICON_SOURCE = Path("res/dyodesk_icon.png")
RES_ICON = Path("res/icon.png")
FLUTTER_ICON = Path("flutter/assets/icon.png")


for required in (
    MANIFEST,
    BUILD_GRADLE,
    STRINGS,
    ICON_SOURCE,
):
    if not required.exists():
        raise FileNotFoundError(
            f"Dosya bulunamadı: {required}"
        )


def replace_required(
    content: str,
    old: str,
    new: str,
    description: str,
) -> str:
    count = content.count(old)

    if count != 1:
        raise RuntimeError(
            f"{description} değiştirilemedi. "
            f"Eşleşme sayısı: {count}"
        )

    print(f"{description} uygulandı.")
    return content.replace(old, new, 1)


manifest = MANIFEST.read_text(encoding="utf-8")

manifest = replace_required(
    manifest,
    'android:label="RustDesk"',
    'android:label="DyoDesk"',
    "Android uygulama adı",
)

manifest = replace_required(
    manifest,
    'android:label="RustDesk Input"',
    'android:label="DyoDesk Giriş Hizmeti"',
    "Android erişilebilirlik hizmeti adı",
)

manifest = replace_required(
    manifest,
    'android:scheme="rustdesk"',
    'android:scheme="dyodesk"',
    "DyoDesk bağlantı şeması",
)

MANIFEST.write_text(
    manifest,
    encoding="utf-8",
)


build_gradle = BUILD_GRADLE.read_text(
    encoding="utf-8"
)

build_gradle = replace_required(
    build_gradle,
    'applicationId "com.carriez.flutter_hbb"',
    'applicationId "com.dyo.dyodesk"',
    "Android applicationId",
)

BUILD_GRADLE.write_text(
    build_gradle,
    encoding="utf-8",
)


strings = STRINGS.read_text(encoding="utf-8")

strings = replace_required(
    strings,
    '<string name="app_name">RustDesk</string>',
    '<string name="app_name">DyoDesk</string>',
    "Android app_name",
)

strings = strings.replace(
    "when RustDesk screen sharing is established",
    "DyoDesk ekran paylaşımı kurulduğunda",
)

STRINGS.write_text(
    strings,
    encoding="utf-8",
)


shutil.copy2(
    ICON_SOURCE,
    RES_ICON,
)

FLUTTER_ICON.parent.mkdir(
    parents=True,
    exist_ok=True,
)

shutil.copy2(
    ICON_SOURCE,
    FLUTTER_ICON,
)

print("DyoDesk Android marka yaması uygulandı.")
print("Application ID: com.dyo.dyodesk")
print("APK adı workflow sonunda DyoDesk-Android.apk olacak.")
