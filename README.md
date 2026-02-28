# VoiceToType（Windows 本機語音轉文字工具）

VoiceToType 是使用 **Python + Tkinter** 開發的輕量 Windows 桌面工具。  
透過全域快捷鍵即可開始/停止錄音，並在本機完成：

1. 錄音（WAV / 16kHz / Mono）
2. 本機 Whisper（`base`）語音轉文字
3. 本機規則式文本清理
4. 自動複製到剪貼簿
5. 顯示在視窗並儲存歷史

> 本版本不使用 OpenAI 雲端 API，也不需要 API Key。

---

## 功能特色

- 標準桌面視窗（可最小化到工作列）
- 不使用 System Tray
- 預設全域快捷鍵：`Right Alt`
- 快捷鍵可在 UI 中修改
- 狀態顯示：待機 / 錄音中 / 處理中 / 完成 / 錯誤
- 適合一般筆電 CPU（Whisper `base` + `fp16=False`）

---

## 專案結構

```text
VoiceToType/
├─ main.py
├─ audio/
│  ├─ __init__.py
│  └─ recorder.py
├─ ui/
│  ├─ __init__.py
│  └─ main_window.py
├─ services/
│  ├─ __init__.py
│  ├─ clipboard_service.py
│  ├─ history_service.py
│  ├─ hotkey_manager.py
│  ├─ local_transcriber.py
│  └─ text_cleaner.py
├─ requirements.txt
├─ .gitignore
├─ LICENSE
└─ README.md
```

---

## Windows 安裝步驟

> 以下以 Windows PowerShell 為例。

1. 下載專案
   ```powershell
   git clone <your-repo-url>
   cd VoiceToType
   ```

2. 建立虛擬環境
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. 安裝 Python 套件
   ```powershell
   pip install -r requirements.txt
   ```

4. 安裝 FFmpeg（Whisper 需要）
   - 建議使用 Chocolatey：
   ```powershell
   choco install ffmpeg -y
   ```
   - 安裝後確認：
   ```powershell
   ffmpeg -version
   ```

---

## 執行方式

```powershell
python main.py
```

第一次執行 Whisper 時會下載 `base` 模型，需稍候片刻。

---

## 快捷鍵使用方式

- 預設快捷鍵：`Right Alt`
- 第一次按下：開始錄音
- 第二次按下：停止錄音並開始處理
- 可在 UI 的「全域快捷鍵」欄位修改，例如：
  - `right alt`
  - `f8` ~ `f12`
  - 單一字元（例如 `r`）

---

## 打包為 EXE（PyInstaller）

1. 安裝 PyInstaller
   ```powershell
   pip install pyinstaller
   ```

2. 進行打包
   ```powershell
   pyinstaller --noconfirm --windowed --name VoiceToType main.py
   ```

3. 執行檔位置
   - `dist/VoiceToType/VoiceToType.exe`

> 請確保執行環境仍可找到 `ffmpeg`。

---

## 常見問題排除

### 1) 無法開始錄音 / 找不到麥克風

- 檢查 Windows 麥克風權限（設定 → 隱私權）
- 確認有可用的錄音裝置
- 重新插拔麥克風或改預設裝置

### 2) 轉寫失敗（Whisper 錯誤）

- 確認 `ffmpeg -version` 可正常輸出
- 確認 `pip show openai-whisper torch` 可查到套件
- 網路不穩時，首次模型下載可能失敗，重新執行一次

### 3) 全域快捷鍵沒有反應

- 嘗試改用 `f8` 或 `f9`
- 避免與其他軟體快捷鍵衝突
- 以一般使用者權限重新啟動程式

### 4) 複製到剪貼簿失敗

- 關閉可能佔用剪貼簿的軟體後重試
- 更新 `pyperclip`

---

## 授權

本專案採用 MIT License，詳見 `LICENSE`。
