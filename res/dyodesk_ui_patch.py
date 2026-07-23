from pathlib import Path
import re


LANG_FILES = [
    Path("src/lang/en.rs"),
    Path("src/lang/tr.rs"),
]

PAIR_PATTERN = re.compile(
    r'(\(\s*"(?P<key>(?:\\.|[^"\\])*)"\s*,\s*")'
    r'(?P<value>(?:\\.|[^"\\])*)'
    r'("\s*\))'
)


def escape_rust_string(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def replace_brand_in_values(content: str) -> str:
    def replacement(match: re.Match) -> str:
        value = match.group("value")

        if "RustDesk" not in value:
            return match.group(0)

        value = value.replace("RustDesk", "DyoDesk")
        return f'{match.group(1)}{value}{match.group(4)}'

    return PAIR_PATTERN.sub(replacement, content)


def set_translation(content: str, key: str, value: str) -> str:
    escaped_key = re.escape(key)
    escaped_value = escape_rust_string(value)

    pattern = re.compile(
        rf'(\(\s*"{escaped_key}"\s*,\s*")'
        rf'((?:\\.|[^"\\])*)'
        rf'("\s*\))'
    )

    updated, count = pattern.subn(
        rf'\g<1>{escaped_value}\g<3>',
        content,
        count=1,
    )

    if count == 0:
        print(f"Uyarı: Çeviri anahtarı bulunamadı: {key}")

    return updated


for language_file in LANG_FILES:
    if not language_file.exists():
        raise FileNotFoundError(
            f"Dil dosyası bulunamadı: {language_file}"
        )

    text = language_file.read_text(encoding="utf-8")
    text = replace_brand_in_values(text)
    text = set_translation(
        text,
        "powered_by_me",
        "Powered by Dyo Bilgi Sistemleri",
    )
    language_file.write_text(text, encoding="utf-8")


turkish_file = Path("src/lang/tr.rs")
turkish_text = turkish_file.read_text(encoding="utf-8")

translations = {
    "Your Desktop": "Bu Bilgisayar",
    "Your Device": "Bu Bilgisayar",
    "desk_tip": (
        "Bu bilgisayara DyoDesk kimliği ve parola ile "
        "güvenli şekilde erişebilirsiniz."
    ),
    "Control Remote Desktop": "Uzak Bilgisayara Bağlan",
    "One-time Password": "Tek Kullanımlık Parola",
    "Connect": "Bağlan",
    "Install": "DyoDesk'i Kur",
    "Service is not running": "DyoDesk hizmeti çalışmıyor",
    "Start service": "Hizmeti Başlat",
    "New Connection": "Yeni Bağlantı",
    "Recent sessions": "Son Bağlantılar",
    "Favorites": "Favoriler",
    "Settings": "Ayarlar",
    "Network": "Ağ",
    "General": "Genel",
    "Security": "Güvenlik",
    "Display": "Görüntü",
    "About": "Hakkında",
    "ID/Relay server": "ID/Relay Sunucusu",
    "ID server": "ID Sunucusu",
    "Relay server": "Relay Sunucusu",
    "Key": "Anahtar",
    "empty_recent_tip": (
        "Henüz bağlantı geçmişi yok.\\n"
        "Yeni bir bağlantı başlatın."
    ),
}

for translation_key, translation_value in translations.items():
    turkish_text = set_translation(
        turkish_text,
        translation_key,
        translation_value,
    )

turkish_file.write_text(turkish_text, encoding="utf-8")

print("DyoDesk arayüz marka ve Türkçe metin yaması uygulandı.")
