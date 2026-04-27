#!/bin/bash

echo "🐅 Тигр пушит Tiger Market на GitHub..."

# Если Git не инициализирован — инициализируем
if [ ! -d ".git" ]; then
    git init
    git branch -M main
fi

# Если remote origin не настроен — настраиваем
if ! git remote get-url origin &> /dev/null; then
    echo "Вставь ссылку на репозиторий:"
    read repo_url
    git remote add origin "$repo_url"
fi

# Создаём .gitignore, если его нет
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.db
.env
build/
*.o
*.out
EOF
fi

git add .
echo "Сообщение коммита:"
read msg
git commit -m "${msg:-обнова}"
git push 
echo "✅ Готово!"