from pathlib import Path
import os
import re


CONFIG_FILE = Path("libs/hbb_common/src/config.rs")

server = os.environ.get("DYODESK_SERVER", "").strip()
public_key = os.environ.get("DYODESK_KEY", "").strip()

if not server:
    raise RuntimeError("DYODESK_SERVER ortam değişkeni bulunamadı.")

if not public_key:
    raise RuntimeError("DYODESK_KEY ortam değişkeni bulunamadı.")

if not CONFIG_FILE.exists():
    raise FileNotFoundError(f"Dosya bulunamadı: {CONFIG_FILE}")

content = CONFIG_FILE.read_text(encoding="utf-8")


def replace_once(pattern: str, replacement: str, description: str) -> None:
    global content

    updated, count = re.subn(
        pattern,
        replacement,
        content,
        count=1,
        flags=re.MULTILINE,
    )

    if count != 1:
        raise RuntimeError(
            f"{description} değiştirilemedi. Eşleşme sayısı: {count}"
        )

    content = updated


safe_server = server.replace("\\", "\\\\").replace('"', '\\"')
safe_key = public_key.replace("\\", "\\\\").replace('"', '\\"')

replace_once(
    r'pub static ref APP_NAME:\s*RwLock<String>\s*=\s*'
    r'RwLock::new\("RustDesk"\.to_owned\(\)\);',
    'pub static ref APP_NAME: RwLock<String> = '
    'RwLock::new("DyoDesk".to_owned());',
    "Uygulama adı",
)

replace_once(
    r'pub const RENDEZVOUS_SERVERS:\s*&\[&str\]\s*=\s*&\[[^\]]*\];',
    f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{safe_server}"];',
    "DyoDesk ID sunucusu",
)

replace_once(
    r'pub const RS_PUB_KEY:\s*&str\s*=\s*"[^"]*";',
    f'pub const RS_PUB_KEY: &str = "{safe_key}";',
    "DyoDesk public key",
)

CONFIG_FILE.write_text(content, encoding="utf-8")

print("DyoDesk çekirdek ayarları başarıyla uygulandı.")
print(f"ID sunucusu: {server}")
print("Public key GitHub Secret üzerinden uygulandı.")
