from pathlib import Path
import base64
import re
import shutil

ICON_ICO = Path("res/dyodesk_icon.ico")
ICON_PNG = Path("res/dyodesk_icon.png")

TARGET_ICO = Path("res/icon.ico")
TARGET_PNG = Path("res/icon.png")

COMMON_CSS = Path("src/ui/common.css")
INDEX_CSS = Path("src/ui/index.css")
INDEX_TIS = Path("src/ui/index.tis")

CONFIG_RS = Path("libs/hbb_common/src/config.rs")


for required in (
    ICON_ICO,
    ICON_PNG,
    COMMON_CSS,
    INDEX_CSS,
    INDEX_TIS,
    CONFIG_RS,
):
    if not required.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {required}")


# EXE ve standart uygulama ikonlarını değiştir.
shutil.copy2(ICON_ICO, TARGET_ICO)
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
            f"UYARI: {description} için eski ifade bulunamadı, "
            "işlem atlandı."
        )
        return content

    raise RuntimeError(
        f"{description} değiştirilemedi. Eşleşme sayısı: {count}"
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

COMMON_CSS.write_text(common, encoding="utf-8")


# ---------------------------------------------------------
# x86 Legacy ana ekran düzeni
# ---------------------------------------------------------

index_css = INDEX_CSS.read_text(encoding="utf-8")

# .left-pane içindeki mevcut width değerini,
# dosyanın boşluk biçiminden bağımsız değiştir.
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
        "Sol panel width tanımı bulunamadı; "
        "240px CSS override eklendi."
    )
else:
    print("Sol panel genişliği 240px olarak ayarlandı.")


index_css = replace_once_or_keep(
    index_css,
    "background: linear-gradient(left,#e242bc,#f4727c);",
    "background: linear-gradient(left,#E31E24,#55565A);",
    "Kurulum kartı renkleri",
)

INDEX_CSS.write_text(index_css, encoding="utf-8")


# ---------------------------------------------------------
# Telif ve arayüz metni
# ---------------------------------------------------------

index_tis = INDEX_TIS.read_text(encoding="utf-8")

index_tis = index_tis.replace(
    "Copyright © 2026 Purslane Tech Pte. Ltd.",
    "Copyright © 2026 Dyo Bilgi Sistemleri",
)

INDEX_TIS.write_text(index_tis, encoding="utf-8")


# ---------------------------------------------------------
# Windows x86 Sciter pencere başlığı ikonu
# ---------------------------------------------------------

icon_base64 = base64.b64encode(
    ICON_PNG.read_bytes()
).decode("ascii")

icon_data_uri = (
    f"data:image/png;base64,{icon_base64}"
)

config_rs = CONFIG_RS.read_text(encoding="utf-8")

# Sadece #[cfg(windows)] altında bulunan ICON sabitini değiştirir.
# macOS ve Linux ikonlarına dokunmaz.
windows_icon_pattern = re.compile(
    r'('
    r'#\[cfg\('
    r'(?:windows|target_os\s*=\s*"windows")'
    r'\)\]'
    r'[^\r\n]*'
    r'\r?\n'
    r'\s*pub\s+const\s+ICON\s*:\s*'
    r"&(?:'static\s+)?str"
    r'\s*=\s*"'
    r')'
    r'data:image/png;base64,[^"]*'
    r'(";)'
    ,
    re.IGNORECASE | re.DOTALL,
)

config_rs, icon_count = windows_icon_pattern.subn(
    lambda match: (
        f"{match.group(1)}"
        f"{icon_data_uri}"
        f"{match.group(2)}"
    ),
    config_rs,
    count=1,
)

if icon_count != 1:
    raise RuntimeError(
        "Windows x86 Sciter pencere ikonu değiştirilemedi. "
        f"Eşleşme sayısı: {icon_count}"
    )

CONFIG_RS.write_text(
    config_rs,
    encoding="utf-8",
)

print(
    "Windows x86 Sciter pencere ikonu "
    "DyoDesk logosuyla değiştirildi."
)

print(
    "DyoDesk x86 Legacy marka ve tema "
    "yaması başarıyla uygulandı."
)
