@echo off
echo ========================================
echo DHCP Finder 執行腳本
echo ========================================

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到Python，請先安裝Python 3.8+
    echo 或者執行編譯好的exe檔案
    pause
    exit /b 1
)

REM 檢查是否已安裝依賴套件
python -c "import tkinter, psutil, scapy, netifaces, speedtest, requests" >nul 2>&1
if errorlevel 1 (
    echo 正在安裝依賴套件...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 錯誤: 安裝依賴套件失敗
        echo 請手動執行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo 啟動DHCP Finder...
python main.py

if errorlevel 1 (
    echo.
    echo 程式執行時發生錯誤
    pause
)

echo.
echo 程式已結束
pause
