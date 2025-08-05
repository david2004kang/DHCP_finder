# DHCP Finder - 網路工具

一個功能完整的網路診斷工具，提供以下功能：

## 功能特色

1. **DHCP伺服器掃描**
   - 掃描網路中的DHCP伺服器
   - 顯示DHCP伺服器的IP地址和MAC地址
   - 支援多網段掃描

2. **網路介面卡資訊**
   - 列出本機所有網路介面卡
   - 顯示詳細的網路配置資訊
   - 包含IP地址、子網路遮罩、閘道等資訊

3. **外網連線測試**
   - 檢測外網連線狀態
   - 網路速度測試（上傳/下載）
   - 延遲測試

## 系統需求

- Windows 10/11
- Python 3.8+ (如果從源碼執行)
- 管理員權限 (部分網路掃描功能需要)

## 安裝與使用

### 方法1：使用編譯好的exe檔案
1. 下載 `DHCP_Finder.exe`
2. 以管理員身份執行

### 方法2：使用虛擬環境（推薦）
1. 設置虛擬環境：
   ```bash
   setup_venv.bat
   ```
2. 啟動虛擬環境：
   ```bash
   activate_venv.bat
   ```
3. 執行主程式：
   ```bash
   python main.py
   ```

### 方法3：直接從源碼執行
1. 安裝Python依賴：
   ```bash
   pip install -r requirements.txt
   ```
2. 執行主程式：
   ```bash
   python main.py
   ```

### 方法4：使用VSCode開發
1. 在VSCode中開啟專案資料夾
2. 選擇Python解釋器：`./venv/Scripts/python.exe`
3. 使用F5開始除錯，或Ctrl+F5執行

## 編譯成exe

### 使用批次檔編譯
執行 `build.bat` 即可自動編譯成exe檔案：
```bash
build.bat
```

### 使用VSCode編譯
1. 按 `Ctrl+Shift+P` 開啟命令面板
2. 選擇 `Tasks: Run Task`
3. 選擇 `編譯成exe` 或 `編譯除錯版exe`

## VSCode開發環境

本專案已配置完整的VSCode開發環境：

### 除錯配置
- **DHCP Finder - 主程式**: 除錯主程式
- **DHCP Finder - 測試模組**: 除錯測試腳本
- **各模組單獨測試**: 單獨測試各功能模組
- **DHCP Finder - 除錯模式**: 詳細除錯模式

### 可用任務
- **執行主程式**: 直接執行程式
- **執行測試**: 執行模組測試
- **安裝依賴套件**: 安裝requirements.txt中的套件
- **編譯成exe**: 編譯正式版exe
- **編譯除錯版exe**: 編譯除錯版exe
- **Pylint檢查**: 程式碼品質檢查
- **清理編譯檔案**: 清理build和dist目錄

## 注意事項

- 某些功能需要管理員權限才能正常運作
- 防火牆可能會阻擋網路掃描功能
- 建議在受信任的網路環境中使用

## 授權

MIT License
