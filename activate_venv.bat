@echo off
echo ========================================
echo DHCP Finder 虛擬環境啟動腳本
echo ========================================

REM 檢查虛擬環境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo 錯誤: 虛擬環境不存在
    echo 請先執行 setup_venv.bat 創建虛擬環境
    pause
    exit /b 1
)

echo 啟動虛擬環境...
call venv\Scripts\activate.bat

echo.
echo ========================================
echo 虛擬環境已啟動！
echo ========================================
echo.
echo 可用命令:
echo   python main.py          - 執行主程式
echo   python test_modules.py  - 執行測試
echo   deactivate              - 退出虛擬環境
echo.
echo Python路徑: %VIRTUAL_ENV%\Scripts\python.exe
echo.

REM 保持命令提示字元開啟
cmd /k
