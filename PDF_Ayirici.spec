# -*- mode: python ; coding: utf-8 -*-

# tkinterdnd2 (surukle-birak) dosyalarini exe'ye gom
try:
    from PyInstaller.utils.hooks import collect_all
    _tkdnd_datas, _tkdnd_binaries, _tkdnd_hidden = collect_all('tkinterdnd2')
except Exception:
    _tkdnd_datas, _tkdnd_binaries, _tkdnd_hidden = [], [], []


a = Analysis(
    ['pdf_ayirici.py'],
    pathex=[],
    binaries=_tkdnd_binaries,
    datas=_tkdnd_datas,
    hiddenimports=_tkdnd_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PDF_Ayirici',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
