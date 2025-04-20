# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Data files from your actual project structure
added_files = [
    ('resources/*', 'resources'),
    ('translations/*', 'translations'),
]

# Your application's Python modules/packages
app_imports = [
    'database',
    'database.car_parts_db',
    'database.users_db',
    'database.settings_db',
    'gui',
    'logger',
    'themes',
    'translations',
    'utils',
    'widgets',
    'widgets.login',
    'widgets.login.login_widget',
    'widgets.login.password_change_dialog',
    'widgets.header',
    'widgets.products',
    'widgets.register_widget',
    'widgets.settings',
    'widgets.smart_search_widget',
    'widgets.splash',
]

# PyQt5 specific imports for proper functionality
pyqt_imports = [
    'PyQt5.QtWidgets',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.sip',
    'PyQt5.QtPrintSupport',
    'PyQt5.uic'
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=app_imports + pyqt_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add PyQt5 plugins (needed for proper functionality)
# This ensures that all Qt plugins are included
from PyInstaller.utils.hooks import collect_data_files
for pkg in ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets']:
    a.datas.extend(collect_data_files(pkg))

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Abu Mukh Car Parts',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window in final version
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/car-icon.jpg',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AbuMukhCarParts',
)