@echo off
echo ========================================
echo DHCP Finder 虛擬環境設置腳本
echo ========================================

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到Python，請先安裝Python 3.8+
    pause
    exit /b 1
)

echo Python版本:
python --version

REM 檢查虛擬環境是否已存在
if exist "venv" (
    echo.
    set /p choice="虛擬環境已存在，是否重新創建? (y/n): "
    if /i not "%choice%"=="y" (
        echo 跳過虛擬環境創建
        goto install_deps
    )
    echo 刪除現有虛擬環境...
    rmdir /s /q venv
)

echo.
echo 創建虛擬環境...
python -m venv venv
if errorlevel 1 (
    echo 錯誤: 創建虛擬環境失敗
    pause
    exit /b 1
)

echo 虛擬環境創建成功！

:install_deps
echo.
echo 升級pip...
venv\Scripts\python.exe -m pip install --upgrade pip

echo.
echo 安裝依賴套件...
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo 錯誤: 安裝依賴套件失敗
    pause
    exit /b 1
)

echo.
echo 測試虛擬環境...
venv\Scripts\python.exe -c "import main; print('虛擬環境測試成功！')"
if errorlevel 1 (
    echo 錯誤: 虛擬環境測試失敗
    pause
    exit /b 1
)

echo.
echo ========================================
echo 虛擬環境設置完成！
echo ========================================
echo.
echo 使用方法:
echo 1. 啟動虛擬環境: activate_venv.bat
echo 2. 在VSCode中: 選擇 ./venv/Scripts/python.exe 作為解釋器
echo 3. 執行程式: venv\Scripts\python.exe main.py
echo.

set /p choice="是否要立即啟動虛擬環境? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo 啟動虛擬環境...
    call activate_venv.bat
) else (
    echo.
    echo 按任意鍵結束...
    pause >nul
)
