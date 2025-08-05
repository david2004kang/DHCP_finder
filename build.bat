@echo off
echo ========================================
echo DHCP Finder 編譯腳本
echo ========================================

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到Python，請先安裝Python 3.8+
    pause
    exit /b 1
)

echo 檢查並安裝依賴套件...
pip install -r requirements.txt
if errorlevel 1 (
    echo 錯誤: 安裝依賴套件失敗
    pause
    exit /b 1
)

echo.
echo 清理舊的編譯檔案...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"

echo.
echo 開始編譯...
pyinstaller --onefile ^
    --windowed ^
    --name "DHCP_Finder" ^
    --add-data "modules;modules" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "tkinter.scrolledtext" ^
    --hidden-import "psutil" ^
    --hidden-import "scapy.all" ^
    --hidden-import "netifaces" ^
    --hidden-import "speedtest" ^
    --hidden-import "requests" ^
    --collect-all "scapy" ^
    --collect-all "psutil" ^
    --collect-all "netifaces" ^
    --noupx ^
    main.py

if errorlevel 1 (
    echo.
    echo 編譯失敗！
    echo 請檢查錯誤訊息並修正問題後重試。
    pause
    exit /b 1
)

echo.
echo ========================================
echo 編譯完成！
echo ========================================
echo.
echo 執行檔位置: dist\DHCP_Finder.exe
echo.
echo 注意事項:
echo 1. 執行時建議以管理員身份運行以獲得完整功能
echo 2. 防火牆可能會詢問網路存取權限，請允許
echo 3. 某些防毒軟體可能會誤報，請加入白名單
echo.

REM 檢查是否要立即執行
set /p choice="是否要立即執行程式? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo 啟動程式...
    start "" "dist\DHCP_Finder.exe"
)

echo.
echo 按任意鍵結束...
pause >nul
