@echo off
echo DPR Analysis Platform - Git Push Helper
echo ========================================

REM Add all changes
echo Adding all changes to git...
git add .

REM Check git status
echo Current git status:
git status --short

REM Commit changes
echo.
set /p commit_message="Enter commit message: "
if "%commit_message%"=="" set commit_message=Updated DPR Analysis Platform with modern UI and fixed CI/CD pipeline

echo Committing changes...
git commit -m "%commit_message%"

REM Push to repository
echo Pushing to repository...
git push origin main

echo.
echo Successfully pushed to repository!
echo Check your GitHub repository for CI/CD pipeline status
echo Pipeline will run automatically and test all components

pause