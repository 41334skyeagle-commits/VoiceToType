# VoiceToType（Windows 本機語音轉文字工具）

VoiceToType 是使用 **Python + Tkinter** 開發的 Windows 桌面工具。  
透過全域快捷鍵即可開始/停止錄音，並在本機完成 Whisper 轉寫與文本清理。

---

## 新功能（本次更新）

- **EXE 穩定運行補強（Whisper + FFmpeg）**
  - 新增 `runtime_patch.py`，啟動時自動處理 `_MEIPASS` / 一般執行路徑
  - 啟動時自動把 `imageio_ffmpeg` 的 ffmpeg binary 目錄加入 `PATH`
  - 支援從專案內 `whisper_model/` 載入 `base` 模型
  - 提供 `VoiceToType.spec`，打包時一併收集 whisper/torch/numpy/imageio_ffmpeg 資源
- **歷史紀錄管理**
  - 每筆歷史旁都有「刪除」按鈕
  - 支援「清空歷史」按鈕（含確認對話框）
- **快速開啟工具**
  - 全域喚醒熱鍵：`Ctrl + Alt + W`
  - 單一執行實例：重複啟動時喚醒既有視窗

---

## 核心功能

1. 錄音（WAV / 16kHz / Mono）
2. 本機 Whisper（`base`）語音轉文字
3. 本機規則式文本清理
4. 自動複製到剪貼簿
5. 顯示在視窗並儲存歷史

---

## 專案結構

```text
VoiceToType/
├─ main.py
├─ runtime_patch.py
├─ VoiceToType.spec
├─ whisper_model/
│  └─ .gitkeep
├─ audio/
│  ├─ __init__.py
│  └─ recorder.py
├─ ui/
│  ├─ __init__.py
│  └─ main_window.py
├─ services/
│  ├─ __init__.py
│  ├─ clipboard_service.py
│  ├─ history_manager.py
│  ├─ hotkey_manager.py
│  ├─ local_transcriber.py
│  ├─ single_instance.py
│  └─ text_cleaner.py
├─ requirements.txt
├─ .gitignore
├─ LICENSE
└─ README.md
```

---

## 安裝依賴

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 準備本機 Whisper 模型（重要）

### 模型放置位置

- 請將模型放在專案根目錄：`whisper_model/`
- `base` 模型檔案應為：`whisper_model/base.pt`

### 下載 `base` 模型到專案資料夾

```powershell
python -c "import whisper; whisper.load_model('base', download_root='whisper_model')"
```

> 建議在打包前先執行一次，確認模型已就位，讓 EXE 可離線使用。

---

## Windows 本機執行

```powershell
python main.py
```

- 程式啟動時會先套用 runtime patch（PATH / `_MEIPASS` / whisper_model）
- 如果模型不在 `whisper_model/`，Whisper 可能嘗試下載（需網路）

---

## 重新打包成 EXE（完整步驟）

### 1) 安裝 PyInstaller

```powershell
pip install pyinstaller
```

### 2) 確認模型已在 whisper_model/

```powershell
dir .\whisper_model
```

需看到 `base.pt`。

### 3) 使用自訂 spec 打包

```powershell
pyinstaller --noconfirm VoiceToType.spec
```

### 4) 產物位置

- `dist/VoiceToType/VoiceToType.exe`

### 5) 執行 EXE

```powershell
.\dist\VoiceToType\VoiceToType.exe
```

---

## 為什麼這版 EXE 比較穩定

1. `runtime_patch.py` 會在啟動時處理 EXE 臨時目錄 `_MEIPASS`。  
2. 啟動時自動把 `imageio_ffmpeg` 提供的 ffmpeg 路徑加進 `PATH`。  
3. 模型目錄固定在 `whisper_model/`，打包時透過 `.spec` 一起帶入。  
4. `VoiceToType.spec` 透過 `collect_all` 打包 `whisper` / `torch` / `numpy` / `imageio_ffmpeg` 必要資源。  

---

## 熱鍵說明

- **錄音熱鍵（可自訂）**：預設 `Right Alt`
  - 第一次按下：開始錄音
  - 第二次按下：停止錄音並開始處理
- **喚醒視窗熱鍵（固定）**：`Ctrl + Alt + W`

---

## 測試流程（建議）

1. 啟動 `python main.py`。  
2. 按 `Right Alt` 開始錄音，再按一次停止。  
3. 確認可得到文字、複製到剪貼簿、歷史可新增。  
4. 打包後執行 `dist/VoiceToType/VoiceToType.exe`。  
5. 重複第 2~3 步，確認 EXE 仍可正常轉寫（不依賴外部 ffmpeg 路徑）。  
6. 關閉視窗後重新啟動 EXE，測試 `Ctrl + Alt + W` 喚醒。  

---

## 授權

本專案採用 MIT License，詳見 `LICENSE`。
