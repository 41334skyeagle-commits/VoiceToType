# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for VoiceToType with bundled Whisper model and FFmpeg."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all

block_cipher = None
project_dir = Path.cwd()
whisper_model_dir = project_dir / "whisper_model"

# Collect package binaries/data/hiddenimports for runtime stability in EXE.
datas = []
binaries = []
hiddenimports = []

for package_name in ["whisper", "torch", "numpy", "imageio_ffmpeg", "tiktoken"]:
    pkg_datas, pkg_bins, pkg_hidden = collect_all(package_name)
    datas += pkg_datas
    binaries += pkg_bins
    hiddenimports += pkg_hidden

# Bundle local Whisper model directory into exe resources.
datas.append((str(whisper_model_dir), "whisper_model"))


a = Analysis(
    ["main.py"],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="VoiceToType",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
