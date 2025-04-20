@echo off
echo Initializing Git repository and uploading to GitHub...

REM 初始化Git仓库
git init
git add .
git commit -m "Initial commit: DeepSeq-Report project structure and error handling tests"

REM 添加远程仓库
git remote add origin https://github.com/algorithm07-ai/-Deep-seq-Report.git

REM 推送到远程仓库
git push -u origin master

echo Upload completed! 