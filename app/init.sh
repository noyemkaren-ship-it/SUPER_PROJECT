#!/bin/bash

echo "🐹 Устанавливаю зависимости для Go-микросервиса..."

# Инициализируем модуль, если его нет
if [ ! -f "go.mod" ]; then
    go mod init go-server
fi

# Gin — веб-фреймворк
go get github.com/gin-gonic/gin

# GORM — ORM для базы данных
go get gorm.io/gorm
go get gorm.io/driver/sqlite

# Чистим зависимости
go mod tidy

echo "✅ Все зависимости установлены!"
echo "🚀 Запусти сервер: go run micro.go"