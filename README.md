# VoiceToType（Windows 本機語音轉文字工具）

VoiceToType 是使用 **Python + Tkinter** 開發的 Windows 桌面工具。  
透過全域快捷鍵即可開始/停止錄音，並在本機完成 Whisper 轉寫與文本清理。

---

## 新功能（本次更新）

- **歷史紀錄管理**
  - 每筆歷史旁都有「刪除」按鈕
  - 支援「清空歷史」按鈕
  - 清空前會跳出確認對話框
  - 刪除完成後會顯示提示訊息
- **快速開啟工具**
  - 新增全域熱鍵：`Ctrl + Alt + W`
  - 可喚醒已在背景/最小化的視窗
- **單一執行實例**
  - 程式啟動時會檢查是否已在執行
  - 若已執行，新的啟動會改為喚醒既有視窗
- **啟動後預設最小化**
  - 開啟程式後會最小化到工作列（非 System Tray）

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

## 依賴安裝指令

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

> `requirements.txt` 內已包含 `pynput`，用於錄音熱鍵與視窗喚醒熱鍵。

---

## Windows 安裝與執行（PowerShell）

### 0️⃣ 前置條件

- Windows 10 或更新版本
- 網路正常
- 已安裝 Git
- 已安裝 Python 3.10+（安裝時勾選 **Add Python to PATH**）

### 1️⃣ 下載專案

```powershell
cd C:\Users\<你的使用者名稱>
git clone https://github.com/41334skyeagle-commits/VoiceToType.git
cd VoiceToType
```

### 2️⃣ 建立並啟動虛擬環境

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

若遇到權限問題：

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
```

### 3️⃣ 安裝 Python 套件

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ 安裝 FFmpeg（Whisper 需要）

先安裝 Chocolatey（管理員 PowerShell）：

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = `
    [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

再安裝 FFmpeg：

```powershell
choco install ffmpeg -y
ffmpeg -version
```

### 5️⃣ 啟動程式

```powershell
python main.py
```

> 首次執行 Whisper 會下載 `base` 模型，請稍候。

---

## 熱鍵說明

- **錄音熱鍵（可自訂）**：預設 `Right Alt`
  - 第一次按下：開始錄音
  - 第二次按下：停止錄音並開始處理
- **喚醒視窗熱鍵（固定）**：`Ctrl + Alt + W`
  - 用途：快速把程式視窗帶到前景

---

## 歷史管理操作方式

1. 在「歷史紀錄」區塊中，每筆文字右側有「刪除」按鈕。  
2. 點擊「刪除」後，該筆紀錄會被移除，並顯示提示。  
3. 點擊「清空歷史」可刪除全部紀錄。  
4. 清空前會出現確認對話框，避免誤刪。  

---

## 打包為 EXE（PyInstaller）

```powershell
pip install pyinstaller
pyinstaller --noconfirm --windowed --name VoiceToType main.py
```

執行檔位置：`dist/VoiceToType/VoiceToType.exe`

---

## 授權

本專案採用 MIT License，詳見 `LICENSE`。
