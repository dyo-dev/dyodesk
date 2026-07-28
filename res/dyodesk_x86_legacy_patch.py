from pathlib import Path
import base64
import re
import shutil

TARGET_TRAY_ICO = Path("res/tray-icon.ico")
ICON_ICO = Path("res/dyodesk_icon.ico")
ICON_PNG = Path("res/dyodesk_icon.png")

TARGET_ICO = Path("res/icon.ico")
TARGET_PNG = Path("res/icon.png")

COMMON_CSS = Path("src/ui/common.css")
INDEX_CSS = Path("src/ui/index.css")
INDEX_TIS = Path("src/ui/index.tis")
UI_RS = Path("src/ui.rs")


for required in (
    ICON_ICO,
    ICON_PNG,
    COMMON_CSS,
    INDEX_CSS,
    INDEX_TIS,
    UI_RS,
):
    if not required.exists():
        raise FileNotFoundError(
            f"Dosya bulunamadı: {required}"
        )


# Standart uygulama ve EXE ikonlarını değiştir.
shutil.copy2(ICON_ICO, TARGET_ICO)
shutil.copy2(ICON_ICO, TARGET_TRAY_ICO)
shutil.copy2(ICON_PNG, TARGET_PNG)

def replace_once_or_keep(
    content: str,
    old: str,
    new: str,
    description: str,
) -> str:
    if new in content:
        print(f"{description} zaten uygulanmış.")
        return content

    count = content.count(old)

    if count == 1:
        print(f"{description} uygulandı.")
        return content.replace(old, new, 1)

    if count == 0:
        print(
            f"UYARI: {description} için eski ifade "
            "bulunamadı, işlem atlandı."
        )
        return content

    raise RuntimeError(
        f"{description} değiştirilemedi. "
        f"Eşleşme sayısı: {count}"
    )


# ---------------------------------------------------------
# Ortak renk ayarları
# ---------------------------------------------------------

common = COMMON_CSS.read_text(encoding="utf-8")

common = replace_once_or_keep(
    common,
    "var(accent): #0071ff;",
    "var(accent): #E31E24;",
    "DyoDesk vurgu rengi",
)

common = replace_once_or_keep(
    common,
    "var(button): #2C8CFF;",
    "var(button): #D51F26;",
    "DyoDesk buton rengi",
)

common = replace_once_or_keep(
    common,
    "var(menu-hover): #D7E4F2;",
    "var(menu-hover): #F4D8D9;",
    "DyoDesk menü rengi",
)

COMMON_CSS.write_text(
    common,
    encoding="utf-8",
)


# ---------------------------------------------------------
# x86 Legacy ana ekran düzeni
# ---------------------------------------------------------

index_css = INDEX_CSS.read_text(encoding="utf-8")

left_pane_pattern = re.compile(
    r"(\.left-pane\s*\{[^{}]*?\bwidth\s*:\s*)"
    r"\d+(?:\.\d+)?px"
    r"(\s*;)",
    re.IGNORECASE | re.DOTALL,
)

index_css, width_count = left_pane_pattern.subn(
    lambda match: (
        f"{match.group(1)}240px{match.group(2)}"
    ),
    index_css,
    count=1,
)

if width_count == 0:
    index_css += (
        "\n\n"
        ".left-pane {\n"
        "    width: 240px !important;\n"
        "}\n"
    )

    print(
        "Sol panel genişliği bulunamadı; "
        "240px CSS override eklendi."
    )
else:
    print(
        "Sol panel genişliği 240px olarak ayarlandı."
    )


index_css = replace_once_or_keep(
    index_css,
    "background: linear-gradient(left,#e242bc,#f4727c);",
    "background: linear-gradient(left,#E31E24,#55565A);",
    "Kurulum kartı renkleri",
)

INDEX_CSS.write_text(
    index_css,
    encoding="utf-8",
)


# ---------------------------------------------------------
# Telif metni
# ---------------------------------------------------------

index_tis = INDEX_TIS.read_text(encoding="utf-8")

index_tis = index_tis.replace(
    "Copyright © 2026 Purslane Tech Pte. Ltd.",
    "Copyright © 2026 Dyo Bilgi Sistemleri",
)

INDEX_TIS.write_text(
    index_tis,
    encoding="utf-8",
)


# ---------------------------------------------------------
# x86 Sciter pencere başlığı ikonu
# src/ui.rs içindeki get_icon() fonksiyonunun
# Windows/Linux için kullanılan gömülü PNG'sini değiştirir.
# ---------------------------------------------------------

icon_base64 = base64.b64encode(
    ICON_PNG.read_bytes()
).decode("ascii")

icon_data_uri = (
    f"data:image/png;base64,{icon_base64}"
)

ui_rs = UI_RS.read_text(encoding="utf-8")

sciter_icon_pattern = re.compile(
    r'('
    r'pub\s+fn\s+get_icon\(\)\s*->\s*String\s*\{'
    r'.*?'
    r'#\[cfg\('
    r'not\('
    r'target_os\s*=\s*"macos"'
    r'\)'
    r'\)'
    r'\]'
    r'[^\r\n]*'
    r'\s*\{'
    r'\s*"'
    r')'
    r'data:image/png;base64,[^"]+'
    r'('
    r'"\s*\.\s*'
    r'(?:into|to_owned)'
    r'\s*\(\s*\)'
    r')',
    re.IGNORECASE | re.DOTALL,
)

ui_rs, icon_count = sciter_icon_pattern.subn(
    lambda match: (
        f"{match.group(1)}"
        f"{icon_data_uri}"
        f"{match.group(2)}"
    ),
    ui_rs,
    count=1,
)

if icon_count != 1:
    raise RuntimeError(
        "src/ui.rs içindeki x86 Sciter ikonu "
        "değiştirilemedi. "
        f"Eşleşme sayısı: {icon_count}"
    )

UI_RS.write_text(
    ui_rs,
    encoding="utf-8",
)

print(
    "x86 Sciter pencere ikonu "
    "DyoDesk logosuyla değiştirildi."
)

print(
    "DyoDesk x86 Legacy marka ve tema "
    "yaması başarıyla uygulandı."
)
