from pathlib import Path

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
        padding: const EdgeInsets.all(14),
        child: Column(
          children: [
            _buildDyoDeskTopBar(context),
            const SizedBox(height: 12),
            Expanded(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  buildLeftPane(context),
                  if (!isIncomingOnly) const SizedBox(width: 12),
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
      height: 54,
      padding: const EdgeInsets.symmetric(horizontal: 18),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.background,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: Colors.black.withOpacity(0.06),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(
            Icons.desktop_windows_rounded,
            color: MyTheme.accent,
            size: 24,
          ),
          const SizedBox(width: 10),
          Text(
            'DyoDesk',
            style: TextStyle(
              color: textColor,
              fontSize: 19,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.2,
            ),
          ),
          const SizedBox(width: 10),
          Container(
            width: 1,
            height: 22,
            color: Colors.black.withOpacity(0.10),
          ),
          const SizedBox(width: 10),
          Text(
            'Dyo Bilgi Sistemleri',
            style: TextStyle(
              color: textColor.withOpacity(0.52),
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 10,
              vertical: 6,
            ),
            decoration: BoxDecoration(
              color: MyTheme.accent.withOpacity(0.08),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                Container(
                  width: 7,
                  height: 7,
                  decoration: const BoxDecoration(
                    color: Color(0xFF22B987),
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 7),
                Text(
                  translate('Ready'),
                  style: TextStyle(
                    color: textColor.withOpacity(0.72),
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
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
          borderRadius: BorderRadius.circular(16),
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
        borderRadius: BorderRadius.circular(16),
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

if old_logo not in content:
    raise RuntimeError("Logo yerleşimi bulunamadı.")

content = content.replace(old_logo, new_logo, 1)

HOME_FILE.write_text(content, encoding="utf-8")

print("DyoDesk modern ana ekran düzeni başarıyla uygulandı.")
