#!/bin/bash

# AniStream - GitHub Push Setup Script
# Bu script loyihani GitHub'ga push qilish uchun tayyorlaydi

echo "======================================"
echo "AniStream - GitHub Setup"
echo "======================================"

# 1. Git repository tayyorlash
echo "[1/5] Git repository tayyorlash..."

# .git papkasi mavjud bo'lsa uni o'chirish
if [ -d ".git" ]; then
    echo "⚠ .git papkasi allaqachon mavjud, o'tib chiqildi"
else
    # Git initialize qilish
    git init
    echo "✓ Git repository initialized"
fi

# 2. Remote URL qo'shish
echo "[2/5] GitHub remote URL qo'shish..."

# Mavjud remote bo'lsa o'chirib yuborish
git remote remove origin 2>/dev/null

# Yangi remote qo'shish
read -p "GitHub repository URL'ni kiriting (https://github.com/username/anistream.git): " GITHUB_URL

if [ -z "$GITHUB_URL" ]; then
    echo "❌ URL kiritilmadi"
    exit 1
fi

git remote add origin "$GITHUB_URL"
echo "✓ Remote URL qo'shildi: $GITHUB_URL"

# 3. Barcha fayllarni stage qilish
echo "[3/5] Fayllarni staging area'ga qo'shish..."
git add .
echo "✓ Fayllar added"

# 4. Initial commit
echo "[4/5] Initial commit yaratish..."
git commit -m "Initial commit: AniStream Django project ready for production"
echo "✓ Commit yaratildi"

# 5. Branch aylantirilish va push
echo "[5/5] GitHub'ga push qilish..."

# Main branch'ga o'tish
git branch -M main
echo "✓ Main branch'ga o'tildi"

# Push qilish
git push -u origin main
if [ $? -eq 0 ]; then
    echo "✓ GitHub'ga muvaffaqiyatli push qilindi!"
else
    echo "❌ Push qilishda xato. SSH key yoki credentials tekshiring."
    exit 1
fi

echo ""
echo "======================================"
echo "Railway Deployment"
echo "======================================"
echo ""
echo "Keyin nima qilish kerak:"
echo "1. Railway.app'ga kiring: https://railway.app"
echo "2. New Project → Deploy from GitHub"
echo "3. Bu repository'ni tanlang"
echo "4. Environment Variables qo'shish:"
echo "   - SECRET_KEY (yangi key generate qiling)"
echo "   - ENVIRONMENT=production"
echo "   - DEBUG=False"
echo "   - ALLOWED_HOSTS=your-app.railway.app"
echo ""
echo "Yangi SECRET_KEY generate qilish uchun:"
echo "python manage.py shell -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
echo ""
echo "======================================"

