@echo off
echo ========================================
echo DHCP Finder 除錯版本編譯腳本
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
echo 開始編譯除錯版本（保留控制台視窗）...
pyinstaller --onefile ^
    --console ^
    --name "DHCP_Finder_Debug" ^
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
    --debug "all" ^
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
echo 除錯版本編譯完成！
echo ========================================
echo.
echo 執行檔位置: dist\DHCP_Finder_Debug.exe
echo.
echo 此版本會顯示控制台視窗，方便查看除錯訊息
echo.

echo 按任意鍵結束...
pause >nul
