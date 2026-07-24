from pathlib import Path
import re

HOME_FILE = Path(
    "flutter/lib/desktop/pages/desktop_home_page.dart"
)

if not HOME_FILE.exists():
    raise FileNotFoundError(
        f"Ana ekran dosyası bulunamadı: {HOME_FILE}"
    )

content = HOME_FILE.read_text(encoding="utf-8")
content = content.replace("\r\n", "\n")


def replace_section(
    start_marker: str,
    end_marker: str,
    replacement: str,
    description: str,
) -> None:
    global content

    start = content.find(start_marker)
    if start < 0:
        raise RuntimeError(
            f"{description} başlangıcı bulunamadı."
        )

    end = content.find(end_marker, start)
    if end < 0:
        raise RuntimeError(
            f"{description} bitişi bulunamadı."
        )

    content = (
        content[:start]
        + replacement
        + "\n\n"
        + content[end:]
    )


if "_buildDyoDeskTopBar" in content:
    print("DyoDesk modern ana ekranı zaten uygulanmış.")
    raise SystemExit(0)


build_start = content.find(
    "  @override\n  Widget build(BuildContext context) {"
)
if build_start < 0:
    build_start = content.find(
        "@override\n  Widget build(BuildContext context) {"
    )

if build_start < 0:
    raise RuntimeError(
        "Modern ana pencere düzeninin başlangıcı bulunamadı."
    )

build_end_marker = (
    "  Widget _buildBlock({required Widget child}) {"
)
build_end = content.find(build_end_marker, build_start)

if build_end < 0:
    raise RuntimeError(
        "Modern ana pencere düzeninin bitişi bulunamadı."
    )

modern_build = '''  @override
  Widget build(BuildContext context) {
    super.build(context);
    final isIncomingOnly = bind.isIncomingOnly();

    return _buildBlock(
      child: Container(
        color: const Color(0xFFF4F5F7),
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            _buildDyoDeskTopBar(context),
            const SizedBox(height: 10),
            Expanded(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  buildLeftPane(context),
                  if (!isIncomingOnly) const SizedBox(width: 10),
                  if (!isIncomingOnly)
                    Expanded(child: buildRightPane(context)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDyoDeskTopBar(BuildContext context) {
    final textColor =
        Theme.of(context).textTheme.titleLarge?.color ?? Colors.black87;

    return Container(
      height: 48,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.background,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.black.withOpacity(0.06),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.035),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(
            Icons.desktop_windows_rounded,
            color: MyTheme.accent,
            size: 22,
          ),
          const SizedBox(width: 9),
          Text(
            'DyoDesk',
            style: TextStyle(
              color: textColor,
              fontSize: 18,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.2,
            ),
          ),
          const Spacer(),
          IconButton(
            tooltip: translate('Settings'),
            onPressed: DesktopTabPage.onAddSetting,
            icon: Icon(
              Icons.settings_outlined,
              color: textColor.withOpacity(0.66),
              size: 21,
            ),
          ),
        ],
      ),
    );
  }'''

content = (
    content[:build_start]
    + modern_build
    + "\n\n"
    + content[build_end:]
)


left_method = content.find(
    "  Widget buildLeftPane(BuildContext context) {"
)
if left_method < 0:
    raise RuntimeError("Sol bilgi kartı metodu bulunamadı.")

provider_start = content.find(
    "    return ChangeNotifierProvider.value(",
    left_method,
)
stack_marker = "        child: Stack("
stack_start = content.find(stack_marker, provider_start)

if provider_start < 0 or stack_start < 0:
    raise RuntimeError("Sol bilgi kartı bölümü bulunamadı.")

stack_end = stack_start + len(stack_marker)

left_replacement = '''    return ChangeNotifierProvider.value(
      value: gFFI.serverModel,
      child: Container(
        width: isIncomingOnly ? 310.0 : 300.0,
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.background,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: Colors.black.withOpacity(0.06),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 16,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        child: Stack('''

content = (
    content[:provider_start]
    + left_replacement
    + content[stack_end:]
)


replace_section(
    "  buildRightPane(BuildContext context) {",
    "  buildIDBoard(BuildContext context) {",
    '''  buildRightPane(BuildContext context) {
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: Colors.black.withOpacity(0.06),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 16,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: ConnectionPage(),
    );
  }''',
    "Sağ bağlantı kartı",
)


old_logo = '''    Align(
      alignment: Alignment.center,
      child: loadLogo(),
    ),'''

new_logo = '''    Container(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 4),
      alignment: Alignment.centerLeft,
      child: loadLogo(),
    ),'''

if old_logo in content:
    content = content.replace(old_logo, new_logo, 1)
    print("Logo yerleşimi güncellendi.")
else:
    print("Logo yerleşimi mevcut tema tarafından değiştirilmiş; bu adım atlandı.")


# Küçük "Powered by Dyo Bilgi Sistemleri" satırını kaldır.
powered_pattern = re.compile(
    r"""if\s*\(bind\.isCustomClient\(\)\)\s*
        Align\(\s*
          alignment:\s*Alignment\.center,\s*
          child:\s*loadPowered\(context\),\s*
        \),""",
    re.MULTILINE,
)
content, powered_count = powered_pattern.subn("", content, count=1)
print(
    "Powered by satırı kaldırıldı."
    if powered_count == 1
    else "Powered by satırı bulunamadı veya önceden kaldırılmış."
)

# Sol panel içeriğini gerçek kaydırılabilir alana dönüştür.
scroll_pattern = re.compile(
    r"""Column\(\s*
      children:\s*\[\s*
        SingleChildScrollView\(\s*
          controller:\s*_leftPaneScrollController,\s*
          child:\s*Column\(\s*
            key:\s*_childKey,\s*
            children:\s*children,\s*
          \),\s*
        \),\s*
        Expanded\(child:\s*Container\(\)\)\s*
      \],\s*
    \),""",
    re.MULTILINE,
)

scroll_replacement = """Column(
      children: [
        Expanded(
          child: SingleChildScrollView(
            controller: _leftPaneScrollController,
            child: Column(
              key: _childKey,
              children: children,
            ),
          ),
        ),
      ],
    ),"""

content, scroll_count = scroll_pattern.subn(
    scroll_replacement,
    content,
    count=1,
)
print(
    "Sol panel kaydırma düzeni iyileştirildi."
    if scroll_count == 1
    else "Sol panel kaydırma düzeni bulunamadı; mevcut yapı korundu."
)

# Kurulum/UAC bilgi kartını kompakt hâle getir.
card_start = content.find("  Widget buildInstallCard(")
card_end = content.find("  @override\n  void initState()", card_start)

if card_start >= 0 and card_end > card_start:
    card = content[card_start:card_end]
    card = card.replace(
        "double marginTop = 20.0,",
        "double marginTop = 10.0,",
        1,
    )
    card = card.replace(
        "padding: EdgeInsets.all(20),",
        "padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),",
        1,
    )
    card = card.replace("fontSize: 15)", "fontSize: 14)", 1)
    card = card.replace("height: 1.5,", "height: 1.35,", 1)
    card = card.replace("fontSize: 13)", "fontSize: 12)", 1)
    card = card.replace(
        ").marginOnly(bottom: 20)",
        ").marginOnly(bottom: 10)",
        1,
    )
    card = card.replace("width: 150,", "width: 140,", 1)
    card = card.replace("textSize: 20,", "textSize: 14,", 1)
    card = card.replace("radius: 10,", "radius: 8,", 1)
    content = content[:card_start] + card + content[card_end:]
    print("Kurulum ve UAC bilgi kartı küçültüldü.")
else:
    print("Kurulum/UAC kartı bulunamadı; mevcut yapı korundu.")


HOME_FILE.write_text(content, encoding="utf-8")

print("DyoDesk modern ana ekran düzeni başarıyla uygulandı.")
