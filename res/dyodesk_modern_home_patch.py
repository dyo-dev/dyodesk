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
            f"{description} değiştirilemedi. "
            f"Eşleşme sayısı: {count}"
        )

    content = updated


replace_once(
    r'''@override\s+
Widget build\(BuildContext context\)\s*\{\s*
super\.build\(context\);\s*
final isIncomingOnly = bind\.isIncomingOnly\(\);\s*
return _buildBlock\(\s*
child: Row\(\s*
crossAxisAlignment: CrossAxisAlignment\.start,\s*
children: \[\s*
buildLeftPane\(context\),\s*
if \(!isIncomingOnly\) const VerticalDivider\(width: 1\),\s*
if \(!isIncomingOnly\)\s*
Expanded\(child: buildRightPane\(context\)\),\s*
\],\s*
\),\s*
\);\s*
\}''',
    '''@override
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
  }''',
    "Modern ana pencere düzeni",
)


replace_once(
    r'''return ChangeNotifierProvider\.value\(\s*
value: gFFI\.serverModel,\s*
child: Container\(\s*
width: isIncomingOnly \? 280\.0 : [0-9.]+,\s*
color: Theme\.of\(context\)\.colorScheme\.background,\s*
child: Stack\(''',
    '''return ChangeNotifierProvider.value(
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
        child: Stack(''',
    "Sol bilgi kartı",
)


replace_once(
    r'''buildRightPane\(BuildContext context\)\s*\{\s*
return Container\(\s*
color: Theme\.of\(context\)\.scaffoldBackgroundColor,\s*
child: ConnectionPage\(\),\s*
\);\s*
\}''',
    '''buildRightPane(BuildContext context) {
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


content = content.replace(
    "Align(\n        alignment: Alignment.center,\n        child: loadLogo(),\n      ),",
    '''Container(
        padding: const EdgeInsets.fromLTRB(18, 18, 18, 4),
        alignment: Alignment.centerLeft,
        child: loadLogo(),
      ),''',
)

HOME_FILE.write_text(content, encoding="utf-8")

print("DyoDesk modern ana ekran düzeni başarıyla uygulandı.")
