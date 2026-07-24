from pathlib import Path

HOME_FILE = Path("flutter/lib/desktop/pages/desktop_home_page.dart")
CONNECTION_FILE = Path("flutter/lib/desktop/pages/connection_page.dart")
PEER_TAB_FILE = Path("flutter/lib/common/widgets/peer_tab_page.dart")

for file_path in (HOME_FILE, CONNECTION_FILE, PEER_TAB_FILE):
    if not file_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")


def matching_brace(text: str, open_index: int) -> int:
    depth = 0
    i = open_index
    quote = None
    triple = False
    line_comment = False
    block_comment = False

    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        nxt2 = text[i + 2] if i + 2 < len(text) else ""

        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue

        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
                continue
            i += 1
            continue

        if quote is not None:
            if triple:
                if ch == quote and nxt == quote and nxt2 == quote:
                    quote = None
                    triple = False
                    i += 3
                    continue
                i += 1
                continue

            if ch == "\\":
                i += 2
                continue

            if ch == quote:
                quote = None
            i += 1
            continue

        if ch == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue

        if ch == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue

        if ch in ("'", '"'):
            if nxt == ch and nxt2 == ch:
                quote = ch
                triple = True
                i += 3
                continue
            quote = ch
            triple = False
            i += 1
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i

        i += 1

    raise RuntimeError("Kapanış süslü parantezi bulunamadı.")



def matching_parenthesis(text: str, open_index: int) -> int:
    depth = 0
    i = open_index
    quote = None
    triple = False
    line_comment = False
    block_comment = False

    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        nxt2 = text[i + 2] if i + 2 < len(text) else ""

        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue

        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
                continue
            i += 1
            continue

        if quote is not None:
            if triple:
                if ch == quote and nxt == quote and nxt2 == quote:
                    quote = None
                    triple = False
                    i += 3
                    continue
                i += 1
                continue

            if ch == "\\":
                i += 2
                continue

            if ch == quote:
                quote = None
            i += 1
            continue

        if ch == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue

        if ch == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue

        if ch in ("'", '"'):
            if nxt == ch and nxt2 == ch:
                quote = ch
                triple = True
                i += 3
                continue
            quote = ch
            triple = False
            i += 1
            continue

        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i

        i += 1

    raise RuntimeError("Kapanış normal parantezi bulunamadı.")

def replace_method(
    text: str,
    class_marker: str,
    signature_marker: str,
    replacement: str,
    description: str,
) -> str:
    class_start = text.find(class_marker)
    if class_start < 0:
        raise RuntimeError(f"{description}: sınıf bulunamadı.")

    method_start = text.find(signature_marker, class_start)
    if method_start < 0:
        raise RuntimeError(f"{description}: metot bulunamadı.")

    params_open = text.find("(", method_start)
    if params_open < 0:
        raise RuntimeError(f"{description}: parametre başlangıcı bulunamadı.")

    params_close = matching_parenthesis(text, params_open)
    open_brace = text.find("{", params_close)
    if open_brace < 0:
        raise RuntimeError(f"{description}: metot gövdesi bulunamadı.")

    method_end = matching_brace(text, open_brace) + 1
    return text[:method_start] + replacement + text[method_end:]


def insert_before_once(
    text: str,
    marker: str,
    insertion: str,
    description: str,
) -> str:
    index = text.find(marker)
    if index < 0:
        raise RuntimeError(f"{description}: ekleme noktası bulunamadı.")
    return text[:index] + insertion + "\n\n" + text[index:]


home = HOME_FILE.read_text(encoding="utf-8").replace("\r\n", "\n")
connection = CONNECTION_FILE.read_text(encoding="utf-8").replace("\r\n", "\n")
peer_tab = PEER_TAB_FILE.read_text(encoding="utf-8").replace("\r\n", "\n")

if "_buildDyoDeskDashboardHeader" in home:
    print("DyoDesk özgün gösterge paneli zaten uygulanmış.")
    raise SystemExit(0)


home_build = r'''Widget build(BuildContext context) {
    super.build(context);
    final isIncomingOnly = bind.isIncomingOnly();

    return _buildBlock(
      child: Container(
        color: const Color(0xFFF4F6F8),
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 10),
        child: Column(
          children: [
            _buildDyoDeskDashboardHeader(context),
            const SizedBox(height: 12),
            Expanded(
              child: isIncomingOnly
                  ? buildLeftPane(context)
                  : Row(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        SizedBox(
                          width: 318,
                          child: buildLeftPane(context),
                        ),
                        const SizedBox(width: 14),
                        Expanded(child: buildRightPane(context)),
                      ],
                    ),
            ),
            if (!isIncomingOnly) const SizedBox(height: 10),
            if (!isIncomingOnly) _buildDyoDeskFooter(context),
          ],
        ),
      ),
    );
  }'''

home = replace_method(
    home,
    "class _DesktopHomePageState",
    "Widget build(BuildContext context) {",
    home_build,
    "Ana ekran",
)

home_helpers = r'''  Widget _buildDyoDeskDashboardHeader(BuildContext context) {
    final titleColor =
        Theme.of(context).textTheme.titleLarge?.color ?? Colors.black87;

    return Container(
      height: 64,
      padding: const EdgeInsets.symmetric(horizontal: 18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black.withOpacity(0.06)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.035),
            blurRadius: 14,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              color: MyTheme.accent.withOpacity(0.10),
              borderRadius: BorderRadius.circular(11),
            ),
            child: const Icon(
              Icons.desktop_windows_rounded,
              color: MyTheme.accent,
              size: 24,
            ),
          ),
          const SizedBox(width: 11),
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'DyoDesk',
                style: TextStyle(
                  color: titleColor,
                  fontSize: 19,
                  fontWeight: FontWeight.w700,
                ),
              ),
              Text(
                'Dyo Bilgi Sistemleri',
                style: TextStyle(
                  color: titleColor.withOpacity(0.48),
                  fontSize: 11.5,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const Spacer(),
          Obx(() {
            final color = _dyoStatusColor();
            return Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 7,
              ),
              decoration: BoxDecoration(
                color: color.withOpacity(0.10),
                borderRadius: BorderRadius.circular(22),
                border: Border.all(color: color.withOpacity(0.20)),
              ),
              child: Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: color,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 7),
                  Text(
                    _dyoStatusText(),
                    style: TextStyle(
                      color: color,
                      fontSize: 12.5,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            );
          }),
          const SizedBox(width: 8),
          IconButton(
            tooltip: translate('Settings'),
            onPressed: DesktopTabPage.onAddSetting,
            icon: Icon(
              Icons.settings_outlined,
              color: titleColor.withOpacity(0.68),
              size: 22,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDyoDeskFooter(BuildContext context) {
    final textColor =
        Theme.of(context).textTheme.bodyMedium?.color ?? Colors.black87;

    return Container(
      height: 34,
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Row(
        children: [
          Obx(() {
            final color = _dyoStatusColor();
            return Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  _dyoStatusText(),
                  style: TextStyle(
                    color: textColor.withOpacity(0.70),
                    fontSize: 12.5,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            );
          }),
          const Spacer(),
          InkWell(
            onTap: DesktopTabPage.onAddSetting,
            borderRadius: BorderRadius.circular(8),
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 9,
                vertical: 6,
              ),
              child: Text(
                'Ayarlar',
                style: TextStyle(
                  color: MyTheme.accent,
                  fontSize: 12.5,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _dyoStatusColor() {
    if (svcStopped.value) {
      return const Color(0xFFE0A12B);
    }
    if (stateGlobal.svcStatus.value == SvcStatus.ready) {
      return const Color(0xFF2DB47D);
    }
    if (stateGlobal.svcStatus.value == SvcStatus.connecting) {
      return const Color(0xFFE0A12B);
    }
    return const Color(0xFFD94A55);
  }

  String _dyoStatusText() {
    if (svcStopped.value) {
      return 'Hizmet kapalı';
    }
    if (stateGlobal.svcStatus.value == SvcStatus.ready) {
      return 'Hazır';
    }
    if (stateGlobal.svcStatus.value == SvcStatus.connecting) {
      return 'Bağlanıyor';
    }
    return 'Hazır değil';
  }

  Widget _buildDyoDeskValueCard({
    required BuildContext context,
    required String label,
    required Widget value,
    required List<Widget> actions,
  }) {
    final textColor =
        Theme.of(context).textTheme.titleLarge?.color ?? Colors.black87;

    return Container(
      padding: const EdgeInsets.fromLTRB(14, 11, 8, 11),
      decoration: BoxDecoration(
        color: const Color(0xFFFAFBFC),
        borderRadius: BorderRadius.circular(13),
        border: Border.all(color: Colors.black.withOpacity(0.07)),
      ),
      child: Row(
        children: [
          Container(
            width: 3,
            height: 51,
            decoration: BoxDecoration(
              color: MyTheme.accent,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(width: 11),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    color: textColor.withOpacity(0.50),
                    fontSize: 12.5,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 3),
                value,
              ],
            ),
          ),
          ...actions,
        ],
      ),
    );
  }'''

home = insert_before_once(
    home,
    "  Widget _buildBlock({required Widget child}) {",
    home_helpers,
    "Ana ekran yardımcıları",
)

left_pane = r'''Widget buildLeftPane(BuildContext context) {
    final isOutgoingOnly = bind.isOutgoingOnly();

    return ChangeNotifierProvider.value(
      value: gFFI.serverModel,
      child: Consumer<ServerModel>(
        builder: (context, model, child) {
          final textColor =
              Theme.of(context).textTheme.titleLarge?.color ??
                  Colors.black87;
          final showOneTime = model.approveMode != 'click' &&
              model.verificationMethod != kUsePermanentPassword;

          return Container(
            clipBehavior: Clip.antiAlias,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.black.withOpacity(0.06)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.04),
                  blurRadius: 16,
                  offset: const Offset(0, 5),
                ),
              ],
            ),
            child: Column(
              children: [
                Expanded(
                  child: SingleChildScrollView(
                    controller: _leftPaneScrollController,
                    padding: const EdgeInsets.fromLTRB(18, 18, 18, 16),
                    child: Column(
                      key: _childKey,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              width: 35,
                              height: 35,
                              decoration: BoxDecoration(
                                color: MyTheme.accent.withOpacity(0.09),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Icon(
                                Icons.monitor_rounded,
                                color: MyTheme.accent,
                                size: 21,
                              ),
                            ),
                            const SizedBox(width: 10),
                            Text(
                              'Bu Bilgisayar',
                              style: TextStyle(
                                color: textColor,
                                fontSize: 18,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Bu bilgisayara DyoDesk kimliği ve parola ile '
                          'güvenli şekilde erişebilirsiniz.',
                          style: TextStyle(
                            color: textColor.withOpacity(0.60),
                            height: 1.35,
                            fontSize: 12.5,
                          ),
                        ),
                        const SizedBox(height: 16),
                        if (!isOutgoingOnly)
                          _buildDyoDeskValueCard(
                            context: context,
                            label: 'Kimlik',
                            value: TextField(
                              controller: model.serverId,
                              readOnly: true,
                              decoration: const InputDecoration(
                                border: InputBorder.none,
                                isDense: true,
                                contentPadding: EdgeInsets.zero,
                              ),
                              style: const TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.8,
                              ),
                            ).workaroundFreezeLinuxMint(),
                            actions: [
                              IconButton(
                                tooltip: 'Kimliği kopyala',
                                onPressed: () {
                                  Clipboard.setData(
                                    ClipboardData(
                                      text: model.serverId.text,
                                    ),
                                  );
                                  showToast(translate('Copied'));
                                },
                                icon: Icon(
                                  Icons.copy_rounded,
                                  color: textColor.withOpacity(0.56),
                                  size: 19,
                                ),
                              ),
                            ],
                          ),
                        if (!isOutgoingOnly) const SizedBox(height: 12),
                        if (!isOutgoingOnly)
                          _buildDyoDeskValueCard(
                            context: context,
                            label: 'Tek Kullanımlık Parola',
                            value: TextField(
                              controller: model.serverPasswd,
                              readOnly: true,
                              decoration: const InputDecoration(
                                border: InputBorder.none,
                                isDense: true,
                                contentPadding: EdgeInsets.zero,
                              ),
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.4,
                              ),
                            ).workaroundFreezeLinuxMint(),
                            actions: [
                              if (showOneTime)
                                IconButton(
                                  tooltip: 'Parolayı yenile',
                                  onPressed: () =>
                                      bind.mainUpdateTemporaryPassword(),
                                  icon: Icon(
                                    Icons.refresh_rounded,
                                    color: textColor.withOpacity(0.56),
                                    size: 20,
                                  ),
                                ),
                              if (showOneTime)
                                IconButton(
                                  tooltip: 'Parolayı kopyala',
                                  onPressed: () {
                                    Clipboard.setData(
                                      ClipboardData(
                                        text: model.serverPasswd.text,
                                      ),
                                    );
                                    showToast(translate('Copied'));
                                  },
                                  icon: Icon(
                                    Icons.copy_rounded,
                                    color: textColor.withOpacity(0.56),
                                    size: 19,
                                  ),
                                ),
                            ],
                          ),
                        if (!isOutgoingOnly) const SizedBox(height: 12),
                        if (!isOutgoingOnly)
                          Row(
                            children: [
                              Expanded(
                                child: OutlinedButton.icon(
                                  onPressed: showOneTime
                                      ? () => bind
                                          .mainUpdateTemporaryPassword()
                                      : null,
                                  icon: const Icon(
                                    Icons.refresh_rounded,
                                    size: 17,
                                  ),
                                  label: const Text('Parolayı Yenile'),
                                  style: OutlinedButton.styleFrom(
                                    minimumSize: const Size(0, 40),
                                    foregroundColor: MyTheme.accent,
                                    side: BorderSide(
                                      color:
                                          MyTheme.accent.withOpacity(0.32),
                                    ),
                                    shape: RoundedRectangleBorder(
                                      borderRadius:
                                          BorderRadius.circular(10),
                                    ),
                                    textStyle: const TextStyle(
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: OutlinedButton.icon(
                                  onPressed: showOneTime
                                      ? () {
                                          Clipboard.setData(
                                            ClipboardData(
                                              text: model
                                                  .serverPasswd.text,
                                            ),
                                          );
                                          showToast(
                                            translate('Copied'),
                                          );
                                        }
                                      : null,
                                  icon: const Icon(
                                    Icons.copy_rounded,
                                    size: 16,
                                  ),
                                  label: const Text('Kopyala'),
                                  style: OutlinedButton.styleFrom(
                                    minimumSize: const Size(0, 40),
                                    foregroundColor:
                                        textColor.withOpacity(0.68),
                                    side: BorderSide(
                                      color:
                                          Colors.black.withOpacity(0.10),
                                    ),
                                    shape: RoundedRectangleBorder(
                                      borderRadius:
                                          BorderRadius.circular(10),
                                    ),
                                    textStyle: const TextStyle(
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        if (!isOutgoingOnly)
                          Obx(
                            () => buildHelpCards(
                              stateGlobal.updateUrl.value,
                            ),
                          ),
                        buildPluginEntry(),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }'''

home = replace_method(
    home,
    "class _DesktopHomePageState",
    "Widget buildLeftPane(BuildContext context) {",
    left_pane,
    "Sol DyoDesk kartı",
)

right_pane = r'''buildRightPane(BuildContext context) {
    return ConnectionPage();
  }'''

home = replace_method(
    home,
    "class _DesktopHomePageState",
    "buildRightPane(BuildContext context) {",
    right_pane,
    "Sağ DyoDesk alanı",
)

install_card = r'''Widget buildInstallCard(
    String title,
    String content,
    String btnText,
    GestureTapCallback onPressed, {
    double marginTop = 12.0,
    String? help,
    String? link,
    bool? closeButton,
    String? closeOption,
  }) {
    if (bind.mainGetBuildinOption(key: kOptionHideHelpCards) == 'Y' &&
        content != 'install_daemon_tip') {
      return const SizedBox();
    }

    void closeCard() async {
      if (closeOption != null) {
        await bind.mainSetLocalOption(
          key: closeOption,
          value: 'N',
        );
        if (bind.mainGetLocalOption(key: closeOption) == 'N') {
          setState(() => isCardClosed = true);
        }
      } else {
        setState(() => isCardClosed = true);
      }
    }

    return Container(
      margin: EdgeInsets.only(top: marginTop),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF8E8),
        borderRadius: BorderRadius.circular(13),
        border: Border.all(
          color: const Color(0xFFE9B44C).withOpacity(0.58),
        ),
      ),
      child: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(13, 12, 13, 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Padding(
                  padding: EdgeInsets.only(top: 2),
                  child: Icon(
                    Icons.warning_amber_rounded,
                    color: Color(0xFFE09A24),
                    size: 24,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (title.isNotEmpty)
                        Text(
                          translate(title),
                          style: const TextStyle(
                            fontSize: 12.5,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      if (title.isNotEmpty && content.isNotEmpty)
                        const SizedBox(height: 4),
                      if (content.isNotEmpty)
                        Text(
                          translate(content),
                          style: TextStyle(
                            color: Colors.black.withOpacity(0.68),
                            height: 1.35,
                            fontSize: 11.5,
                          ),
                        ),
                      if (btnText.isNotEmpty) const SizedBox(height: 10),
                      if (btnText.isNotEmpty)
                        SizedBox(
                          width: double.infinity,
                          height: 38,
                          child: ElevatedButton(
                            onPressed: onPressed,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: MyTheme.accent,
                              foregroundColor: Colors.white,
                              elevation: 0,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(9),
                              ),
                            ),
                            child: Text(
                              translate(btnText),
                              style: const TextStyle(
                                fontSize: 12.5,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ),
                      if (help != null) const SizedBox(height: 7),
                      if (help != null)
                        InkWell(
                          onTap: () async =>
                              await launchUrl(Uri.parse(link!)),
                          child: Text(
                            translate(help),
                            style: const TextStyle(
                              color: MyTheme.accent,
                              decoration: TextDecoration.underline,
                              fontSize: 11,
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          if (closeButton == true)
            Positioned(
              top: 1,
              right: 1,
              child: IconButton(
                onPressed: closeCard,
                icon: Icon(
                  Icons.close_rounded,
                  color: Colors.black.withOpacity(0.45),
                  size: 17,
                ),
              ),
            ),
        ],
      ),
    );
  }'''

home = replace_method(
    home,
    "class _DesktopHomePageState",
    "Widget buildInstallCard(",
    install_card,
    "Kurulum uyarı kartı",
)

connection_build = r'''Widget build(BuildContext context) {
    final isOutgoingOnly = bind.isOutgoingOnly();

    return Container(
      color: const Color(0xFFF4F6F8),
      child: Column(
        children: [
          Expanded(
            child: Column(
              children: [
                _buildRemoteIDTextField(context),
                const SizedBox(height: 12),
                Expanded(
                  child: Container(
                    clipBehavior: Clip.antiAlias,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: Colors.black.withOpacity(0.06),
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.04),
                          blurRadius: 16,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Padding(
                      padding: const EdgeInsets.fromLTRB(14, 10, 14, 8),
                      child: PeerTabPage(),
                    ),
                  ),
                ),
              ],
            ),
          ),
          if (!isOutgoingOnly)
            const Offstage(
              offstage: true,
              child: OnlineStatusWidget(),
            ),
        ],
      ),
    );
  }'''

connection = replace_method(
    connection,
    "class _ConnectionPageState",
    "Widget build(BuildContext context) {",
    connection_build,
    "Bağlantı sayfası",
)

remote_field = r'''Widget _buildRemoteIDTextField(BuildContext context) {
    updateTextAndPreserveSelection(
      _idEditingController,
      _idController.text,
    );

    final textColor =
        Theme.of(context).textTheme.titleLarge?.color ?? Colors.black87;
    final quickPeers = _allPeersLoader.peers.take(3).toList();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(22, 20, 22, 18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black.withOpacity(0.06)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 16,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 35,
                height: 35,
                decoration: BoxDecoration(
                  color: MyTheme.accent.withOpacity(0.09),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(
                  Icons.desktop_windows_rounded,
                  color: MyTheme.accent,
                  size: 21,
                ),
              ),
              const SizedBox(width: 10),
              Text(
                'Uzak Bilgisayara Bağlan',
                style: TextStyle(
                  color: textColor,
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Obx(
                  () => TextField(
                    autocorrect: false,
                    enableSuggestions: false,
                    keyboardType: TextInputType.visiblePassword,
                    focusNode: _idFocusNode,
                    controller: _idEditingController,
                    inputFormatters: [IDTextInputFormatter()],
                    style: const TextStyle(
                      fontFamily: 'WorkSans',
                      fontSize: 19,
                      height: 1.3,
                    ),
                    decoration: InputDecoration(
                      filled: true,
                      fillColor: const Color(0xFFFAFBFC),
                      hintText: _idInputFocused.value
                          ? null
                          : 'Bilgisayar kimliğini girin',
                      hintStyle: TextStyle(
                        color: textColor.withOpacity(0.34),
                        fontSize: 16,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 15,
                        vertical: 14,
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(11),
                        borderSide: BorderSide(
                          color: Colors.black.withOpacity(0.11),
                        ),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(11),
                        borderSide: const BorderSide(
                          color: MyTheme.accent,
                          width: 1.4,
                        ),
                      ),
                    ),
                    onChanged: (value) {
                      _idController.id = value;
                    },
                    onSubmitted: (_) => onConnect(),
                  ).workaroundFreezeLinuxMint(),
                ),
              ),
              const SizedBox(width: 10),
              SizedBox(
                width: 106,
                height: 50,
                child: ElevatedButton(
                  onPressed: onConnect,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: MyTheme.accent,
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(11),
                    ),
                  ),
                  child: const Text(
                    'BAĞLAN',
                    style: TextStyle(
                      fontSize: 13.5,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 7),
              SizedBox(
                width: 45,
                height: 50,
                child: PopupMenuButton<String>(
                  tooltip: 'Bağlantı türü',
                  onOpened: () => _menuOpen.value = true,
                  onCanceled: () => _menuOpen.value = false,
                  onSelected: (value) {
                    _menuOpen.value = false;
                    if (value == 'file') {
                      onConnect(isFileTransfer: true);
                    } else if (value == 'camera') {
                      onConnect(isViewCamera: true);
                    } else if (value == 'terminal') {
                      onConnect(isTerminal: true);
                    }
                  },
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  itemBuilder: (context) => const [
                    PopupMenuItem(
                      value: 'file',
                      child: Text('Dosya Aktarımı'),
                    ),
                    PopupMenuItem(
                      value: 'camera',
                      child: Text('Kamerayı Görüntüle'),
                    ),
                    PopupMenuItem(
                      value: 'terminal',
                      child: Text('Terminal'),
                    ),
                  ],
                  child: Container(
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: Colors.black.withOpacity(0.11),
                      ),
                      borderRadius: BorderRadius.circular(11),
                    ),
                    child: Center(
                      child: Obx(
                        () => Icon(
                          _menuOpen.value
                              ? Icons.keyboard_arrow_up_rounded
                              : Icons.keyboard_arrow_down_rounded,
                          color: textColor.withOpacity(0.66),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
          if (quickPeers.isNotEmpty) const SizedBox(height: 14),
          if (quickPeers.isNotEmpty)
            Text(
              'Son kullanılanlar',
              style: TextStyle(
                color: textColor.withOpacity(0.52),
                fontSize: 11.5,
                fontWeight: FontWeight.w600,
              ),
            ),
          if (quickPeers.isNotEmpty) const SizedBox(height: 8),
          if (quickPeers.isNotEmpty)
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: quickPeers.map((peer) {
                final label = peer.alias.isNotEmpty
                    ? peer.alias
                    : peer.hostname.isNotEmpty
                        ? peer.hostname
                        : peer.id;
                return InkWell(
                  onTap: () {
                    setState(() {
                      _idController.id = peer.id;
                      updateTextAndPreserveSelection(
                        _idEditingController,
                        peer.id,
                      );
                    });
                  },
                  borderRadius: BorderRadius.circular(9),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 7,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFAFBFC),
                      borderRadius: BorderRadius.circular(9),
                      border: Border.all(
                        color: Colors.black.withOpacity(0.08),
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.monitor_rounded,
                          color: MyTheme.accent,
                          size: 16,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          label,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            color: textColor.withOpacity(0.74),
                            fontSize: 11.5,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
        ],
      ),
    );
  }'''

connection = replace_method(
    connection,
    "class _ConnectionPageState",
    "Widget _buildRemoteIDTextField(BuildContext context) {",
    remote_field,
    "Bağlantı kartı",
)

peer_build = r'''Widget build(BuildContext context) {
    final model = Provider.of<PeerTabModel>(context);

    Widget selectionWrap(Widget widget) {
      return model.multiSelectionMode
          ? createMultiSelectionBar(model)
          : widget;
    }

    return Column(
      textBaseline: TextBaseline.ideographic,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          height: 52,
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: selectionWrap(
            Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Expanded(child: _createSwitchBar(context)),
                if (stateGlobal.isPortrait.isTrue)
                  ..._portraitRightActions(context)
                else
                  ..._landscapeRightActions(context),
              ],
            ),
          ),
        ),
        Divider(
          height: 1,
          color: Colors.black.withOpacity(0.07),
        ),
        _createPeersView(),
      ],
    );
  }'''

peer_tab = replace_method(
    peer_tab,
    "class _PeerTabPageState",
    "Widget build(BuildContext context) {",
    peer_build,
    "Bilgisayar sekmeleri",
)

tab_helper = r'''  String _dyoTabTitle(int index) {
    switch (index) {
      case 0:
        return 'Son Bağlantılar';
      case 1:
        return 'Favoriler';
      case 2:
        return 'Yakındaki Cihazlar';
      case 3:
        return 'Adres Defteri';
      case 4:
        return 'Gruplar';
      default:
        return 'Bilgisayarlar';
    }
  }'''

peer_tab = insert_before_once(
    peer_tab,
    "  Widget _createSwitchBar(BuildContext context) {",
    tab_helper,
    "Sekme başlıkları",
)

switch_bar = r'''Widget _createSwitchBar(BuildContext context) {
    final model = Provider.of<PeerTabModel>(context);

    return Obx(
      () => SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        child: Row(
          children: model.visibleEnabledOrderedIndexs.map((tabIndex) {
            final selected = model.currentTab == tabIndex;
            final selectedColor = MyTheme.accent;
            final normalColor =
                Theme.of(context).textTheme.bodyMedium?.color ??
                    Colors.black87;

            return Padding(
              padding: const EdgeInsets.only(right: 7),
              child: InkWell(
                onTap: isOptionFixed(kOptionPeerTabIndex)
                    ? null
                    : () async {
                        await handleTabSelection(tabIndex);
                        await bind.setLocalFlutterOption(
                          k: kOptionPeerTabIndex,
                          v: tabIndex.toString(),
                        );
                      },
                borderRadius: BorderRadius.circular(10),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 160),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 11,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: selected
                        ? selectedColor.withOpacity(0.08)
                        : const Color(0xFFFAFBFC),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: selected
                          ? selectedColor.withOpacity(0.34)
                          : Colors.black.withOpacity(0.07),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        model.tabIcon(tabIndex),
                        size: 16,
                        color: selected
                            ? selectedColor
                            : normalColor.withOpacity(0.62),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        _dyoTabTitle(tabIndex),
                        style: TextStyle(
                          color: selected
                              ? selectedColor
                              : normalColor.withOpacity(0.68),
                          fontSize: 11.5,
                          fontWeight: selected
                              ? FontWeight.w700
                              : FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }'''

peer_tab = replace_method(
    peer_tab,
    "class _PeerTabPageState",
    "Widget _createSwitchBar(BuildContext context) {",
    switch_bar,
    "Metinli sekme çubuğu",
)

HOME_FILE.write_text(home, encoding="utf-8")
CONNECTION_FILE.write_text(connection, encoding="utf-8")
PEER_TAB_FILE.write_text(peer_tab, encoding="utf-8")

print("DyoDesk özgün gösterge paneli başarıyla uygulandı.")
