# DHCP Finder - Git版本控制說明

## Git倉庫狀態

✅ **Git倉庫已初始化完成**

- **初始提交**: `1c0c1e4` - DHCP Finder v1.0
- **分支**: master
- **檔案數**: 19個檔案，2858行程式碼
- **狀態**: 工作目錄乾淨，無未提交變更

## 已提交的檔案

### 核心程式檔案
- `main.py` - 主程式
- `modules/` - 功能模組目錄
  - `__init__.py`
  - `dhcp_scanner.py` - DHCP掃描模組
  - `network_info.py` - 網路資訊模組
  - `internet_test.py` - 外網測試模組

### 配置檔案
- `requirements.txt` - Python依賴套件
- `.gitignore` - Git忽略檔案配置
- `.vscode/` - VSCode開發環境配置
  - `launch.json` - 除錯配置
  - `settings.json` - 編輯器設定
  - `tasks.json` - 任務配置

### 腳本檔案
- `run.bat` - 執行腳本
- `build.bat` - 編譯腳本
- `build_debug.bat` - 除錯編譯腳本
- `setup.py` - 安裝腳本
- `setup_venv.bat` - 虛擬環境設置腳本
- `activate_venv.bat` - 虛擬環境啟動腳本

### 文檔檔案
- `README.md` - 專案說明
- `使用說明.md` - 詳細使用說明
- `test_modules.py` - 測試腳本

## Git忽略檔案 (.gitignore)

已配置忽略以下檔案類型：
- Python編譯檔案 (`__pycache__/`, `*.pyc`)
- 虛擬環境 (`venv/`, `.venv/`)
- 編譯產物 (`build/`, `dist/`, `*.spec`)
- IDE檔案 (`.idea/`)
- 系統檔案 (`Thumbs.db`, `.DS_Store`)
- 日誌檔案 (`*.log`)
- 備份檔案 (`*.bak`, `*.backup`)

**注意**: VSCode配置檔案已保留在版本控制中，以便團隊開發使用。

## 常用Git命令

### 查看狀態
```bash
git status          # 查看工作目錄狀態
git log --oneline   # 查看提交歷史
git diff            # 查看未暫存的變更
git diff --cached   # 查看已暫存的變更
```

### 添加和提交
```bash
git add .                    # 添加所有變更
git add <file>              # 添加特定檔案
git commit -m "提交訊息"     # 提交變更
git commit -am "提交訊息"    # 添加並提交已追蹤檔案的變更
```

### 分支操作
```bash
git branch                  # 查看分支
git branch <branch-name>    # 創建分支
git checkout <branch-name>  # 切換分支
git checkout -b <branch-name> # 創建並切換分支
git merge <branch-name>     # 合併分支
```

### 遠端倉庫
```bash
git remote add origin <url>  # 添加遠端倉庫
git push -u origin master    # 首次推送到遠端
git push                     # 推送變更
git pull                     # 拉取遠端變更
git clone <url>              # 複製遠端倉庫
```

## 建議的工作流程

### 1. 功能開發
```bash
git checkout -b feature/new-feature  # 創建功能分支
# 進行開發...
git add .
git commit -m "Add new feature"
git checkout master
git merge feature/new-feature        # 合併功能分支
git branch -d feature/new-feature    # 刪除功能分支
```

### 2. 錯誤修復
```bash
git checkout -b bugfix/fix-issue     # 創建修復分支
# 修復錯誤...
git add .
git commit -m "Fix issue description"
git checkout master
git merge bugfix/fix-issue           # 合併修復分支
git branch -d bugfix/fix-issue       # 刪除修復分支
```

### 3. 版本發布
```bash
git tag v1.0.0                      # 創建版本標籤
git push origin v1.0.0               # 推送標籤到遠端
```

## 提交訊息規範

建議使用以下格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type類型
- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文檔變更
- `style`: 程式碼格式變更
- `refactor`: 程式碼重構
- `test`: 測試相關
- `chore`: 建置或輔助工具變更

### 範例
```
feat(dhcp): add MAC address vendor identification

- Add OUI database lookup for MAC address vendors
- Improve DHCP server information display
- Update test cases for vendor identification

Closes #123
```

## 版本控制最佳實踐

1. **頻繁提交**: 小而頻繁的提交比大而稀少的提交更好
2. **清晰的提交訊息**: 描述變更的內容和原因
3. **使用分支**: 為每個功能或修復創建獨立分支
4. **定期同步**: 經常從主分支拉取最新變更
5. **測試後提交**: 確保程式碼通過測試後再提交
6. **保持歷史整潔**: 使用rebase整理提交歷史（謹慎使用）

## 緊急情況處理

### 撤銷最後一次提交
```bash
git reset --soft HEAD~1    # 保留變更，撤銷提交
git reset --hard HEAD~1    # 完全撤銷提交和變更（危險）
```

### 恢復刪除的檔案
```bash
git checkout HEAD -- <file>  # 恢復特定檔案
git checkout .               # 恢復所有變更
```

### 查看檔案歷史
```bash
git log --follow <file>      # 查看檔案的提交歷史
git blame <file>             # 查看檔案每行的最後修改者
```

## 團隊協作

如果要與團隊協作，建議：

1. 設置遠端倉庫（GitHub, GitLab等）
2. 使用Pull Request/Merge Request進行程式碼審查
3. 設置CI/CD自動化測試和部署
4. 建立分支保護規則
5. 定期進行程式碼審查

## 備份建議

- 定期推送到遠端倉庫
- 考慮使用多個遠端倉庫作為備份
- 重要版本創建標籤
- 定期匯出專案備份
