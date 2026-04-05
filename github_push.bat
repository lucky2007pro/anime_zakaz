@echo off
REM AniStream - GitHub Push Setup Script (Windows)
REM Bu script loyihani GitHub'ga push qilish uchun tayyorlaydi

echo ======================================
echo AniStream - GitHub Setup (Windows)
echo ======================================
echo.

REM 1. Git repository tayyorlash
echo [1/5] Git repository tayyorlash...

if exist .git (
    echo.
    echo Warning: .git papkasi allaqachon mavjud
) else (
    git init
    echo √ Git repository initialized
)

REM 2. Remote URL qo'shish
echo [2/5] GitHub remote URL qo'shish...

set /p GITHUB_URL="GitHub repository URL'ni kiriting (https://github.com/username/anistream.git): "

if "%GITHUB_URL%"=="" (
    echo Error: URL kiritilmadi
    exit /b 1
)

git remote remove origin >nul 2>&1
git remote add origin %GITHUB_URL%
echo √ Remote URL qo'shildi: %GITHUB_URL%

REM 3. Barcha fayllarni stage qilish
echo [3/5] Fayllarni staging area'ga qo'shish...
git add .
echo √ Fayllar added

REM 4. Initial commit
echo [4/5] Initial commit yaratish...
git commit -m "Initial commit: AniStream Django project ready for production"
echo √ Commit yaratildi

REM 5. Branch aylantirilish va push
echo [5/5] GitHub'ga push qilish...

git branch -M main
echo √ Main branch'ga o'tildi

git push -u origin main
if %ERRORLEVEL% EQU 0 (
    echo √ GitHub'ga muvaffaqiyatli push qilindi!
) else (
    echo Error: Push qilishda xato. SSH key yoki credentials tekshiring.
    exit /b 1
)

echo.
echo ======================================
echo Railway Deployment
echo ======================================
echo.
echo Keyin nima qilish kerak:
echo 1. Railway.app'ga kiring: https://railway.app
echo 2. New Project → Deploy from GitHub
echo 3. Bu repository'ni tanlang
echo 4. Environment Variables qo'shish:
echo    - SECRET_KEY (yangi key generate qiling)
echo    - ENVIRONMENT=production
echo    - DEBUG=False
echo    - ALLOWED_HOSTS=your-app.railway.app
echo.
echo Yangi SECRET_KEY generate qilish uchun:
echo python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
echo.
echo ======================================
pause

