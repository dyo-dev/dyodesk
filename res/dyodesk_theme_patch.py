from pathlib import Path
import re


COMMON_FILE = Path("flutter/lib/common.dart")
HOME_FILE = Path(
    "flutter/lib/desktop/pages/desktop_home_page.dart"
)


def replace_once(
    content: str,
    pattern: str,
    replacement: str,
    description: str,
) -> str:
    updated, count = re.subn(
        pattern,
        replacement,
        content,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )

    if count != 1:
        raise RuntimeError(
            f"{description} değiştirilemedi. "
            f"Eşleşme sayısı: {count}"
        )

    return updated


if not COMMON_FILE.exists():
    raise FileNotFoundError(COMMON_FILE)

if not HOME_FILE.exists():
    raise FileNotFoundError(HOME_FILE)


# Genel uygulama renkleri
common = COMMON_FILE.read_text(encoding="utf-8")

changes = [
    (
        r"static const Color grayBg = "
        r"Color\(0xFFEFEFF2\);",
        "static const Color grayBg = "
        "Color(0xFFF3F3F5);",
        "Açık arka plan",
    ),
    (
        r"static const Color accent = "
        r"Color\(0xFF0071FF\);",
        "static const Color accent = "
        "Color(0xFFE31E24);",
        "Dyo kırmızısı",
    ),
    (
        r"static const Color accent50 = "
        r"Color\(0x770071FF\);",
        "static const Color accent50 = "
        "Color(0x77E31E24);",
        "Şeffaf vurgu",
    ),
    (
        r"static const Color accent80 = "
        r"Color\(0xAA0071FF\);",
        "static const Color accent80 = "
        "Color(0xAAE31E24);",
        "Yoğun vurgu",
    ),
    (
        r"static const Color idColor = "
        r"Color\(0xFF00B6F0\);",
        "static const Color idColor = "
        "Color(0xFFE31E24);",
        "DyoDesk ID rengi",
    ),
    (
        r"static const Color button = "
        r"Color\(0xFF2C8CFF\);",
        "static const Color button = "
        "Color(0xFFD51F26);",
        "Buton rengi",
    ),
]

for pattern, replacement, description in changes:
    common = replace_once(
        common,
        pattern,
        replacement,
        description,
    )

common, primary_count = re.subn(
    r"primary:\s*Colors\.blue,",
    "primary: accent,",
    common,
)

if primary_count != 2:
    raise RuntimeError(
        "Açık ve koyu tema ana renkleri değiştirilemedi. "
        f"Eşleşme sayısı: {primary_count}"
    )

COMMON_FILE.write_text(common, encoding="utf-8")


# Ana ekran düzeni
home = HOME_FILE.read_text(encoding="utf-8")

home = replace_once(
    home,
    r"const borderColor = Color\(0xFF2F65BA\);",
    "const borderColor = Color(0xFFE31E24);",
    "Ana ekran kenarlığı",
)

home = replace_once(
    home,
    r"width:\s*isIncomingOnly\s*\?\s*"
    r"280\.0\s*:\s*200\.0",
    "width: isIncomingOnly ? 300.0 : 240.0",
    "Sol panel genişliği",
)

home = replace_once(
    home,
    r"colors:\s*\[\s*"
    r"Color\.fromARGB\(255,\s*226,\s*66,\s*188\),\s*"
    r"Color\.fromARGB\(255,\s*244,\s*114,\s*124\),\s*"
    r"\]",
    """colors: [
              Color(0xFFE31E24),
              Color(0xFF55565A),
            ]""",
    "Kurulum kartı renkleri",
)

HOME_FILE.write_text(home, encoding="utf-8")

print("DyoDesk kırmızı-gri görsel teması uygulandı.")
