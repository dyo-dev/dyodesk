from pathlib import Path
import re
import shutil


MANIFEST = Path("flutter/android/app/src/main/AndroidManifest.xml")
BUILD_GRADLE = Path("flutter/android/app/build.gradle")
STRINGS = Path("flutter/android/app/src/main/res/values/strings.xml")
PUBSPEC = Path("flutter/pubspec.yaml")
SERVER_PAGE = Path("flutter/lib/mobile/pages/server_page.dart")
CONFIG_RS = Path("libs/hbb_common/src/config.rs")

ICON_SOURCE = Path("res/dyodesk_icon.png")
RES_ICON = Path("res/icon.png")
FLUTTER_ICON = Path("flutter/assets/icon.png")


for required in (
    MANIFEST,
    BUILD_GRADLE,
    STRINGS,
    PUBSPEC,
    SERVER_PAGE,
    CONFIG_RS,
    ICON_SOURCE,
):
    if not required.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {required}")


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
    if count != 1:
        raise RuntimeError(
            f"{description} değiştirilemedi. Eşleşme sayısı: {count}"
        )

    print(f"{description} uygulandı.")
    return content.replace(old, new, 1)


manifest = MANIFEST.read_text(encoding="utf-8")
manifest = replace_once_or_keep(
    manifest,
    'android:label="RustDesk"',
    'android:label="DyoDesk"',
    "Android uygulama adı",
)
manifest = replace_once_or_keep(
    manifest,
    'android:label="RustDesk Input"',
    'android:label="DyoDesk Giriş Hizmeti"',
    "Android erişilebilirlik hizmeti adı",
)
manifest = replace_once_or_keep(
    manifest,
    'android:scheme="rustdesk"',
    'android:scheme="dyodesk"',
    "DyoDesk bağlantı şeması",
)
MANIFEST.write_text(manifest, encoding="utf-8")


build_gradle = BUILD_GRADLE.read_text(encoding="utf-8")
build_gradle = replace_once_or_keep(
    build_gradle,
    'applicationId "com.carriez.flutter_hbb"',
    'applicationId "com.dyo.dyodesk"',
    "Android applicationId",
)
BUILD_GRADLE.write_text(build_gradle, encoding="utf-8")


strings = STRINGS.read_text(encoding="utf-8")
strings = replace_once_or_keep(
    strings,
    '<string name="app_name">RustDesk</string>',
    '<string name="app_name">DyoDesk</string>',
    "Android app_name",
)
strings = strings.replace(
    "when RustDesk screen sharing is established",
    "DyoDesk ekran paylaşımı kurulduğunda",
)
STRINGS.write_text(strings, encoding="utf-8")


shutil.copy2(ICON_SOURCE, RES_ICON)
FLUTTER_ICON.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(ICON_SOURCE, FLUTTER_ICON)

pubspec = PUBSPEC.read_text(encoding="utf-8")
if "adaptive_icon_foreground:" not in pubspec:
    android_line_pattern = re.compile(
        r'(^flutter_icons:\s*\n'
        r'(?:^[ \t].*\n)*?'
        r'^[ \t]+android:\s*true\s*$)',
        re.MULTILINE,
    )
    pubspec, adaptive_count = android_line_pattern.subn(
        lambda match: (
            f'{match.group(1)}\n'
            '  adaptive_icon_background: "#FFFFFF"\n'
            '  adaptive_icon_foreground: "../res/dyodesk_icon.png"'
        ),
        pubspec,
        count=1,
    )
    if adaptive_count != 1:
        raise RuntimeError(
            "flutter_icons adaptive ikon ayarları eklenemedi. "
            f"Eşleşme sayısı: {adaptive_count}"
        )
    print("Android adaptive launcher ikon ayarları eklendi.")
else:
    print("Android adaptive launcher ikon ayarları zaten var.")
PUBSPEC.write_text(pubspec, encoding="utf-8")


config_rs = CONFIG_RS.read_text(encoding="utf-8")

floating_option_code = '''        config.options.insert(
            "disable-floating-window".to_owned(),
            "Y".to_owned(),
        );
'''

if '"disable-floating-window".to_owned()' not in config_rs:
    mutable_local_pattern = re.compile(
        r'(impl\s+LocalConfig\s*\{\s*'
        r'fn\s+load\(\)\s*->\s*LocalConfig\s*\{\s*'
        r'let\s+mut\s+config\s*=\s*'
        r'Config::load_::\s*<\s*LocalConfig\s*>\s*'
        r'\(\s*"_local"\s*\)\s*;\s*)',
        re.MULTILINE | re.DOTALL,
    )
    config_rs, mutable_count = mutable_local_pattern.subn(
        lambda match: (
            f"{match.group(1)}\n"
            f"{floating_option_code}\n"
        ),
        config_rs,
        count=1,
    )

    if mutable_count == 0:
        direct_local_pattern = re.compile(
            r'impl\s+LocalConfig\s*\{\s*'
            r'fn\s+load\(\)\s*->\s*LocalConfig\s*\{\s*'
            r'Config::load_::\s*<\s*LocalConfig\s*>\s*'
            r'\(\s*"_local"\s*\)\s*'
            r'\}\s*\}',
            re.MULTILINE | re.DOTALL,
        )
        direct_local_replacement = '''impl LocalConfig {
    fn load() -> LocalConfig {
        let mut config =
            Config::load_::<LocalConfig>("_local");

        config.options.insert(
            "disable-floating-window".to_owned(),
            "Y".to_owned(),
        );

        config
    }
}'''
        config_rs, direct_count = direct_local_pattern.subn(
            direct_local_replacement,
            config_rs,
            count=1,
        )
        if direct_count != 1:
            raise RuntimeError(
                "Yüzen pencere varsayılanı LocalConfig içine eklenemedi."
            )

    print("Yüzen DyoDesk servis balonu varsayılan kapatıldı.")
else:
    print("Yüzen servis balonu ayarı zaten uygulanmış.")

CONFIG_RS.write_text(config_rs, encoding="utf-8")


server_page = SERVER_PAGE.read_text(encoding="utf-8")
if "class DyoDeskAndroidSetupCard" not in server_page:
    children_old = '''                        buildPresetPasswordWarningMobile(),
                        gFFI.serverModel.isStart
'''
    children_new = '''                        buildPresetPasswordWarningMobile(),
                        const DyoDeskAndroidSetupCard(),
                        gFFI.serverModel.isStart
'''
    server_page = replace_once_or_keep(
        server_page,
        children_old,
        children_new,
        "DyoDesk Android ilk kurulum kartı konumu",
    )

    class_marker = "class ServiceNotRunningNotification extends StatelessWidget"

    setup_class = '''class DyoDeskAndroidSetupCard extends StatelessWidget {
  const DyoDeskAndroidSetupCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final serverModel = Provider.of<ServerModel>(context);

    if (serverModel.mediaOk && serverModel.inputOk) {
      return const SizedBox.shrink();
    }

    void startScreenCapture() {
      if (gFFI.userModel.userName.value.isEmpty &&
          bind.mainGetLocalOption(key: "show-scam-warning") != "N") {
        showScamWarning(context, serverModel);
      } else {
        serverModel.toggleService();
      }
    }

    return PaddingCard(
      title: "DyoDesk İlk Kurulum",
      titleIcon: const Icon(
        Icons.admin_panel_settings_outlined,
        color: Colors.redAccent,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "Bu telefona veya tablete uzaktan bağlanmak için "
            "aşağıdaki iki izni etkinleştirin.",
          ),
          const SizedBox(height: 10),
          if (!serverModel.mediaOk)
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.mobile_screen_share),
                label: const Text("1. Ekran Yakalamayı Başlat"),
                onPressed: startScreenCapture,
              ),
            ),
          if (!serverModel.inputOk)
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                icon: const Icon(Icons.touch_app_outlined),
                label: const Text("2. Giriş Kontrolünü Aç"),
                onPressed: serverModel.toggleInput,
              ),
            ),
          const SizedBox(height: 4),
          const Text(
            "Android güvenliği nedeniyle sistem izinlerinin "
            "kullanıcı tarafından onaylanması gerekir.",
            style: TextStyle(
              fontSize: 12,
              color: MyTheme.darkGray,
            ),
          ),
        ],
      ),
    );
  }
}

'''
    if class_marker not in server_page:
        raise RuntimeError(
            "server_page.dart içinde kurulum kartı ekleme noktası bulunamadı."
        )
    server_page = server_page.replace(
        class_marker,
        setup_class + class_marker,
        1,
    )
    print("DyoDesk Android izin kurulum kartı eklendi.")
else:
    print("DyoDesk Android izin kurulum kartı zaten var.")

SERVER_PAGE.write_text(server_page, encoding="utf-8")

print()
print("DyoDesk Android marka ve kullanım yaması tamamlandı.")
print("Launcher ve adaptive ikonlar: DyoDesk")
print("Yüzen servis balonu: Varsayılan kapalı")
print("İzin kurulum yönlendirmesi: Eklendi")
