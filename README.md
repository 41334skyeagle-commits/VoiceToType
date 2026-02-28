# VoiceToType（Windows 桌面語音轉文字工具）

VoiceToType 是一個使用 **Python + Tkinter** 開發的輕量 Windows 桌面工具。  
透過全域快捷鍵即可開始/停止錄音，並自動完成：

1. 錄音（WAV / 16kHz / Mono）
2. Whisper API 語音轉文字（`whisper-1`）
3. GPT 文本優化（`gpt-4o-mini`）
4. 自動複製到剪貼簿
5. 顯示在視窗並儲存歷史

---

## 功能特色

- 標準桌面視窗（可最小化到工作列）
- 不使用 System Tray
- 預設全域快捷鍵：`Right Alt`
- 快捷鍵可在 UI 中修改
- 狀態顯示：待機 / 錄音中 / 處理中 / 完成 / 錯誤
- 支援常見錯誤提示（API 失敗、麥克風問題、設定問題）

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
│  └─ openai_service.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ LICENSE
└─ README.md
```

---

## 安裝步驟

> 以下步驟以 Windows PowerShell 為例。

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

3. 安裝依賴
   ```powershell
   pip install -r requirements.txt
   ```

---

## 環境變數設定

1. 複製範例檔
   ```powershell
   copy .env.example .env
   ```

2. 編輯 `.env`，填入你的 OpenAI API Key
   ```env
   OPENAI_API_KEY=你的金鑰
   ```

> 程式啟動時會自動讀取 `.env`。

---

## 執行方式

```powershell
python main.py
```

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

> 若需要一起帶入 `.env`，請將 `.env` 放在與 `.exe` 同層目錄，或改為系統環境變數。

---

## 常見問題排除

### 1) 啟動後顯示 API Key 錯誤

- 確認 `.env` 存在且有 `OPENAI_API_KEY`
- 確認金鑰可用且未過期

### 2) 無法開始錄音 / 找不到麥克風

- 檢查 Windows 麥克風權限（設定 → 隱私權）
- 確認有可用的錄音裝置
- 重新插拔麥克風或改預設裝置

### 3) 處理中失敗（網路/API）

- 檢查網路連線
- 稍後重試
- 檢查 OpenAI API 配額與服務狀態

### 4) 全域快捷鍵沒有反應

- 嘗試改用 `f8` 或 `f9`
- 避免與其他軟體快捷鍵衝突
- 以一般使用者權限重新啟動程式

### 5) 複製到剪貼簿失敗

- 關閉可能佔用剪貼簿的軟體後重試
- 更新 `pyperclip`

---

## 授權

本專案採用 MIT License，詳見 `LICENSE`。
