#!/bin/bash

# AniStream - Ubuntu Setup Script
# Bu script loyihani Ubuntu-da ishga tushirish uchun zarur bo'lgan barcha narsani tayyorlaydi

echo "======================================"
echo "AniStream Ubuntu Setup Script"
echo "======================================"

# 1. Python va Virtual Environment
echo "[1/7] Virtual Environment tayyorlash..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual Environment yaratildi"
else
    echo "✓ Virtual Environment allaqachon mavjud"
fi

# Activate virtual environment
source venv/bin/activate

# 2. Zavisimliklarni o'rnatish
echo "[2/7] Zavisimliklarni o'rnatish..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Zavisimliklarni o'rnatildi"

# 3. .env faylini tayyorlash
echo "[3/7] .env fayli tayyorlash..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env fayli yaratildi (.env.example dan)"
    echo "⚠ .env faylini o'z sozlamalaringiz bilan tahrirlang!"
else
    echo "✓ .env fayli allaqachon mavjud"
fi

# 4. Migratsiyalar
echo "[4/7] Database migratsiyalarini qo'llash..."
python manage.py migrate
echo "✓ Migratsiyalar qo'llandi"

# 5. Static fayllarni to'plash
echo "[5/7] Static fayllarni to'plash..."
python manage.py collectstatic --noinput
echo "✓ Static fayllar to'plandi"

# 6. Superuser tayyorlash (optional)
echo "[6/7] Superuser tayyorlash (optional)..."
echo "Superuser yaratishni xohlaysizmi? (y/n): "
read -r response
if [ "$response" = "y" ]; then
    python manage.py createsuperuser
    echo "✓ Superuser yaratildi"
else
    echo "⊘ Superuser yaratilmadi"
fi

# 7. Yakuniy qadamlar
echo "[7/7] Yakuniy sozlamalar..."
echo "✓ Setup to'liq bo'ldi!"

echo ""
echo "======================================"
echo "Keyin nima qilish kerak:"
echo "======================================"
echo "1. Mahalliy server ishga tushirish uchun:"
echo "   python manage.py runserver"
echo ""
echo "2. Production uchun Gunicorn bilan:"
echo "   gunicorn src.wsgi:application --bind 0.0.0.0:8000"
echo ""
echo "3. Admin panelga kirish:"
echo "   http://127.0.0.1:8000/admin"
echo ""
echo "======================================"

