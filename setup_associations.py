#!/usr/bin/env python3
"""
SPL File Association Setup
"""
import os
import sys
import platform
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
DOCS_DIR = BASE_DIR / "docs"
ICON_SOURCE = DOCS_DIR / "logo.png"  # Primary source

def get_icon_path(target_os: str) -> Path:
    """Get platform-specific icon path"""
    return {
        "Windows": DOCS_DIR / "logo.ico",
        "Darwin": DOCS_DIR / "logo.icns",
        "Linux": DOCS_DIR / "logo.png"
    }[target_os]

def linux_setup():
    """Linux file association setup"""
    try:
        # Create MIME type
        mime_file = "/usr/share/mime/packages/application-x-spl.xml"
        Path(mime_file).write_text(f"""<?xml version="1.0"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-spl">
    <comment>Swahili Programming Language</comment>
    <glob pattern="*.spl"/>
    <icon name="spl-logo"/>
  </mime-type>
</mime-info>""")

        # Install icon
        icon_dir = Path("/usr/share/icons/hicolor/256x256/apps/")
        icon_dir.mkdir(parents=True, exist_ok=True)
        os.symlink(ICON_SOURCE, icon_dir / "spl-logo.png")
        
        # Update databases
        os.system("sudo update-mime-database /usr/share/mime")
        os.system("sudo gtk-update-icon-cache /usr/share/icons/hicolor/")
        
    except PermissionError:
        print("Run with sudo for system-wide setup")
        sys.exit(1)

def windows_setup():
    """Windows registry setup"""
    try:
        import winreg
        icon_path = get_icon_path("Windows")
        
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.spl")
        winreg.SetValue(key, "", winreg.REG_SZ, "SPLFile")
        
        icon_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Classes\SPLFile\DefaultIcon")
        winreg.SetValue(icon_key, "", winreg.REG_SZ, str(icon_path))
        
    except ImportError:
        print("Install pywin32 for Windows support: pip install pywin32")

def macos_setup():
    """macOS file association setup"""
    plist_path = Path.home()/"Library/Preferences/com.spl.associations.plist"
    plist_content = f"""<?xml version="1.0"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDocumentTypes</key>
  <array>
    <dict>
      <key>CFBundleTypeExtensions</key>
      <array><string>spl</string></array>
      <key>CFBundleTypeIconFile</key>
      <string>{get_icon_path("Darwin")}</string>
    </dict>
  </array>
</dict>
</plist>"""
    plist_path.write_text(plist_content)
    os.system("killall Finder")  # Refresh Finder

if __name__ == "__main__":
    current_os = platform.system()
    
    if not ICON_SOURCE.exists():
        print(f"Error: Missing icon file at {ICON_SOURCE}")
        sys.exit(1)
        
    if current_os == "Linux":
        linux_setup()
    elif current_os == "Windows":
        windows_setup()
    elif current_os == "Darwin":
        macos_setup()
    else:
        print(f"Unsupported OS: {current_os}")
        sys.exit(1)
        
    print("File associations configured successfully!")