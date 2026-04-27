#!/bin/bash

echo "⚡ Устанавливаю зависимости для C++ микросервиса..."

# Проверяем, есть ли g++
if ! command -v g++ &> /dev/null; then
    echo "❌ g++ не найден. Установи его: sudo apt install g++"
    exit 1
fi

# Проверяем, есть ли crow_all.h
if [ ! -f "crow_all.h" ]; then
    echo "📥 Скачиваю crow_all.h (header-only библиотека)..."
    wget https://raw.githubusercontent.com/CrowCpp/crow/master/single_include/crow_all.h
fi

# Создаём папку для скомпилированного файла
mkdir -p build

echo "🔧 Компилирую C++ сервер..."
g++ main.cpp -o build/wheel -lpthread

if [ $? -eq 0 ]; then
    echo "✅ C++ сервер готов!"
    echo "🚀 Запусти: ./build/wheel"
else
    echo "❌ Ошибка компиляции!"
fi