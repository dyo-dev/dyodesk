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


def escape_rust_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def host_without_port(value: str) -> str:
    if value.count(":") == 1:
        host, possible_port = value.rsplit(":", 1)
        if possible_port.isdigit():
            return host
    return value


host = host_without_port(server)
id_server = server if server != host else f"{host}:21116"
relay_server = f"{host}:21117"

safe_host = escape_rust_string(host)
safe_id_server = escape_rust_string(id_server)
safe_relay_server = escape_rust_string(relay_server)
safe_key = escape_rust_string(public_key)

content = CONFIG_FILE.read_text(encoding="utf-8")


def replace_once(
    pattern: str,
    replacement: str,
    description: str,
    flags: int = re.MULTILINE | re.DOTALL,
) -> None:
    global content

    updated, count = re.subn(
        pattern,
        replacement,
        content,
        count=1,
        flags=flags,
    )

    if count != 1:
        raise RuntimeError(
            f"{description} değiştirilemedi. Eşleşme sayısı: {count}"
        )

    content = updated


replace_once(
    r'pub static ref APP_NAME:\s*RwLock<String>\s*=\s*'
    r'RwLock::new\("RustDesk"\.to_owned\(\)\);',
    'pub static ref APP_NAME: RwLock<String> = '
    'RwLock::new("DyoDesk".to_owned());',
    "Uygulama adı",
)

replace_once(
    r'pub const RENDEZVOUS_SERVERS:\s*&\[&str\]\s*=\s*&\[[^\]]*\];',
    f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{safe_host}"];',
    "Yerleşik ID sunucusu",
)

replace_once(
    r'pub const RS_PUB_KEY:\s*&str\s*=\s*"[^"]*";',
    f'pub const RS_PUB_KEY: &str = "{safe_key}";',
    "Yerleşik public key",
)

config2_pattern = (
    r'(impl\s+Config2\s*\{\s*'
    r'fn\s+load\(\)\s*->\s*Config2\s*\{\s*'
    r'let\s+mut\s+config\s*=\s*'
    r'Config::load_::\s*<\s*Config2\s*>\s*'
    r'\(\s*"2"\s*\)\s*;\s*'
    r'let\s+mut\s+store\s*=\s*false\s*;)'
)

config2_injection = (
    r"\1" + f"""
        config.options.insert(
            "custom-rendezvous-server".to_owned(),
            "{safe_id_server}".to_owned(),
        );

        config.options.insert(
            "relay-server".to_owned(),
            "{safe_relay_server}".to_owned(),
        );

        config.options.insert(
            "key".to_owned(),
            "{safe_key}".to_owned(),
        );

        config.rendezvous_server = "{safe_id_server}".to_owned();
        store = true;
"""
)

replace_once(
    config2_pattern,
    config2_injection,
    "DyoDesk ağ varsayılanları",
)

local_pattern = (
    r'impl\s+LocalConfig\s*\{\s*'
    r'fn\s+load\(\)\s*->\s*LocalConfig\s*\{\s*'
    r'Config::load_::\s*<\s*LocalConfig\s*>\s*'
    r'\(\s*"_local"\s*\)\s*'
    r'\}'
)

local_replacement = """impl LocalConfig {
    fn load() -> LocalConfig {
        let mut config = Config::load_::<LocalConfig>("_local");
        config
            .options
            .insert("lang".to_owned(), "tr".to_owned());
        config
    }"""

replace_once(
    local_pattern,
    local_replacement,
    "Varsayılan Türkçe dili",
)

CONFIG_FILE.write_text(content, encoding="utf-8")

print("DyoDesk çekirdek ayarları başarıyla uygulandı.")
print(f"ID sunucusu: {id_server}")
print(f"Relay sunucusu: {relay_server}")
print("Public key uygulandı.")
print("Varsayılan dil: Türkçe")
