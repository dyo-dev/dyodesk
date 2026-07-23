Unicode true
RequestExecutionLevel user
SetCompressor /SOLID lzma

!include "MUI2.nsh"
!include "nsDialogs.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
!include "FileFunc.nsh"

!ifndef PROJECT_ROOT
  !error "PROJECT_ROOT tanımlanmadı."
!endif

Name "DyoDesk"
Caption "DyoDesk"
BrandingText "Powered by Dyo Bilgi Sistemleri"

OutFile "${PROJECT_ROOT}\packaging\output\DyoDesk.exe"
Icon "${PROJECT_ROOT}\res\dyodesk_icon.ico"
UninstallIcon "${PROJECT_ROOT}\res\dyodesk_icon.ico"

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "DyoDesk"
VIAddVersionKey "CompanyName" "Dyo Bilgi Sistemleri"
VIAddVersionKey "FileDescription" "DyoDesk Uzak Masaüstü"
VIAddVersionKey "FileVersion" "1.0.0"
VIAddVersionKey "ProductVersion" "1.0.0"
VIAddVersionKey "LegalCopyright" "Dyo Bilgi Sistemleri"

InstallDir "$PROGRAMFILES64\DyoDesk"
InstallDirRegKey HKLM "Software\Dyo Bilgi Sistemleri\DyoDesk" "InstallPath"

ShowInstDetails show
ShowUninstDetails show
AutoCloseWindow false
WindowIcon on

!define MUI_ICON "${PROJECT_ROOT}\res\dyodesk_icon.ico"
!define MUI_UNICON "${PROJECT_ROOT}\res\dyodesk_icon.ico"
!define MUI_ABORTWARNING

Var ModePage
Var PortableRadio
Var InstallRadio
Var Mode
Var ResultCode

Page custom ModePageCreate ModePageLeave
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Turkish"


Function IsElevated
  System::Call 'shell32::IsUserAnAdmin() i .r0'
  Push $0
FunctionEnd


Function RelaunchElevatedForInstall
  Call IsElevated
  Pop $0

  ${If} $0 == 0
    ExecShell "runas" "$EXEPATH" "/MODE=install"
    Quit
  ${EndIf}
FunctionEnd


Function .onInit
  ${GetParameters} $0
  ${GetOptions} $0 "/MODE=" $Mode

  ${If} $Mode == "install"
    Call RelaunchElevatedForInstall
  ${EndIf}
FunctionEnd


Function ModePageCreate
  ${If} $Mode != ""
    Abort
  ${EndIf}

  nsDialogs::Create 1018
  Pop $ModePage

  ${If} $ModePage == error
    Abort
  ${EndIf}

  ${NSD_CreateLabel} 0 0 100% 26u "DyoDesk nasıl çalıştırılsın?"
  Pop $0
  CreateFont $1 "Segoe UI" 14 700
  SendMessage $0 ${WM_SETFONT} $1 1

  ${NSD_CreateLabel} 0 32u 100% 24u \
    "Geçici kullanım için kurulumsuz çalıştırabilir veya sürekli erişim için bilgisayara kurabilirsiniz."
  Pop $0

  ${NSD_CreateRadioButton} 0 72u 100% 18u "Kurulumsuz Çalıştır"
  Pop $PortableRadio
  ${NSD_Check} $PortableRadio

  ${NSD_CreateLabel} 20u 92u 95% 28u \
    "Teknisyen kullanımı içindir. Hizmet, kısayol ve kaldırma kaydı oluşturmaz."
  Pop $0

  ${NSD_CreateRadioButton} 0 132u 100% 18u "Bu Bilgisayara Kur"
  Pop $InstallRadio

  ${NSD_CreateLabel} 20u 152u 95% 38u \
    "Sürekli erişim, Windows hizmeti, açılışta çalışma ve UAC ekranlarında tam kontrol sağlar."
  Pop $0

  nsDialogs::Show
FunctionEnd


Function ModePageLeave
  ${NSD_GetState} $InstallRadio $0

  ${If} $0 == ${BST_CHECKED}
    StrCpy $Mode "install"
    Call RelaunchElevatedForInstall
  ${Else}
    StrCpy $Mode "portable"
  ${EndIf}
FunctionEnd


Function ExtractX64Payload
  InitPluginsDir
  SetOutPath "$PLUGINSDIR\DyoDesk"
  File /r "${PROJECT_ROOT}\packaging\payload\x64\*.*"
FunctionEnd


Function RunPortable
  ${IfNot} ${RunningX64}
    MessageBox MB_ICONSTOP|MB_OK \
      "Bu test paketinde henüz Windows 32-bit istemcisi bulunmuyor.$\r$\n$\r$\n32-bit Legacy sürüm sonraki aşamada aynı DyoDesk.exe dosyasına eklenecek."
    Quit
  ${EndIf}

  DetailPrint "DyoDesk kurulumsuz hazırlanıyor..."
  Call ExtractX64Payload

  IfFileExists "$PLUGINSDIR\DyoDesk\DyoDesk.exe" +3 0
    MessageBox MB_ICONSTOP|MB_OK "DyoDesk.exe paket içinde bulunamadı."
    Quit

  HideWindow
  ExecWait '"$PLUGINSDIR\DyoDesk\DyoDesk.exe"' $ResultCode
  SetErrorLevel $ResultCode
  Quit
FunctionEnd


Function InstallDyoDesk
  ${IfNot} ${RunningX64}
    MessageBox MB_ICONSTOP|MB_OK \
      "Bu test paketinde henüz Windows 32-bit istemcisi bulunmuyor.$\r$\n$\r$\n32-bit Legacy sürüm hazırlandığında otomatik olarak eklenecek."
    Quit
  ${EndIf}

  SetRegView 64
  StrCpy $INSTDIR "$PROGRAMFILES64\DyoDesk"

  DetailPrint "Eski DyoDesk hizmeti durduruluyor..."
  nsExec::ExecToLog '"$SYSDIR\sc.exe" stop DyoDesk'
  nsExec::ExecToLog '"$SYSDIR\taskkill.exe" /F /IM DyoDesk.exe'
  Sleep 1000

  DetailPrint "DyoDesk dosyaları hazırlanıyor..."
  Call ExtractX64Payload

  CreateDirectory "$INSTDIR"

  nsExec::ExecToLog \
    '"$COMSPEC" /C xcopy "$PLUGINSDIR\DyoDesk\*" "$INSTDIR\" /E /I /H /R /Y'
  Pop $ResultCode

  ${If} $ResultCode != 0
  ${AndIf} $ResultCode != 1
    MessageBox MB_ICONSTOP|MB_OK \
      "DyoDesk dosyaları kopyalanamadı. Hata kodu: $ResultCode"
    Quit
  ${EndIf}

  IfFileExists "$INSTDIR\DyoDesk.exe" +3 0
    MessageBox MB_ICONSTOP|MB_OK "Kurulum klasöründe DyoDesk.exe bulunamadı."
    Quit

  WriteUninstaller "$INSTDIR\DyoDeskKaldir.exe"

  CreateDirectory "$SMPROGRAMS\DyoDesk"
  CreateShortcut "$SMPROGRAMS\DyoDesk\DyoDesk.lnk" \
    "$INSTDIR\DyoDesk.exe" "" "$INSTDIR\DyoDesk.exe"
  CreateShortcut "$DESKTOP\DyoDesk.lnk" \
    "$INSTDIR\DyoDesk.exe" "" "$INSTDIR\DyoDesk.exe"

  WriteRegStr HKLM "Software\Dyo Bilgi Sistemleri\DyoDesk" \
    "InstallPath" "$INSTDIR"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "DisplayName" "DyoDesk"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "DisplayIcon" "$INSTDIR\DyoDesk.exe"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "UninstallString" '"$INSTDIR\DyoDeskKaldir.exe"'

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "Publisher" "Dyo Bilgi Sistemleri"

  WriteRegStr HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "DisplayVersion" "1.0.0"

  WriteRegDWORD HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "NoModify" 1

  WriteRegDWORD HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk" \
    "NoRepair" 1

  DetailPrint "DyoDesk Windows hizmeti kuruluyor..."
  nsExec::ExecToLog '"$INSTDIR\DyoDesk.exe" --install-service'
  Pop $ResultCode

  nsExec::ExecToLog '"$SYSDIR\sc.exe" config DyoDesk start= auto'
  nsExec::ExecToLog '"$SYSDIR\sc.exe" start DyoDesk'

  MessageBox MB_ICONINFORMATION|MB_OK \
    "DyoDesk kurulumu tamamlandı.$\r$\n$\r$\nWindows hizmeti kuruldu ve sürekli erişim hazırlandı."
FunctionEnd


Section "DyoDesk"
  ${If} $Mode == "portable"
    Call RunPortable
  ${ElseIf} $Mode == "install"
    Call InstallDyoDesk
  ${Else}
    MessageBox MB_ICONSTOP|MB_OK "Çalışma biçimi seçilemedi."
    Quit
  ${EndIf}
SectionEnd


Function un.onInit
  System::Call 'shell32::IsUserAnAdmin() i .r0'

  ${If} $0 == 0
    ExecShell "runas" "$EXEPATH" "/S _?=$INSTDIR"
    Quit
  ${EndIf}
FunctionEnd


Section "Uninstall"
  SetRegView 64

  nsExec::ExecToLog '"$SYSDIR\sc.exe" stop DyoDesk'
  nsExec::ExecToLog '"$SYSDIR\sc.exe" delete DyoDesk'
  nsExec::ExecToLog '"$SYSDIR\taskkill.exe" /F /IM DyoDesk.exe'

  Delete "$DESKTOP\DyoDesk.lnk"
  RMDir /r "$SMPROGRAMS\DyoDesk"

  DeleteRegKey HKLM \
    "Software\Microsoft\Windows\CurrentVersion\Uninstall\DyoDesk"
  DeleteRegKey HKLM "Software\Dyo Bilgi Sistemleri\DyoDesk"

  RMDir /r "$INSTDIR"
SectionEnd
