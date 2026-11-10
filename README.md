# 🎬 CS2 Clip Maker

Полноценный проект для создания клипов из CS2 видео с использованием ИИ-анализа, Whisper распознавания речи и FFmpeg обработки.

## 🚀 Возможности

- **Веб-приложение** с премиум тёмным интерфейсом
- **Telegram-бот** для приветствия и уведомлений
- **AI анализ** видео для поиска интересных моментов
- **Вырезание клипов** длительностью 60-120 секунд
- **TikTok формат** 9:16, 1080×1920
- **Размытый фон** с увеличенным центром
- **Whisper субтитры** - белые жирные субтитры с чёрной обводкой
- **Просмотр и скачивание** готовых MP4
- **История клипов** и настройки

## 📋 Технологии

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Video Processing:** FFmpeg, yt-dlp
- **AI:** OpenAI Whisper
- **Telegram:** python-telegram-bot

## 📦 Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/ilanazarov163-spec/Bot-marker.git
cd Bot-marker
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Установка FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Скачайте с https://ffmpeg.org/download.html и добавьте в PATH

### 4. Настройка Telegram бота

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Получите токен бота
3. Создайте `.env` файл:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
TELEGRAM_CHAT_ID=ваш_chat_id
SECRET_KEY=произвольный_ключ
```

### 5. Запуск

```bash
python app.py
```

Веб-приложение будет доступно по адресу: `http://localhost:5000`

## 🎯 Использование

1. Откройте веб-приложение
2. Вставьте YouTube-ссылку на CS2 видео
3. Нажмите "Обработать"
4. Дождитесь завершения обработки
5. Скачайте готовые клипы

## 📁 Структура проекта

```
Bot-marker/
├── app.py              # Flask веб-приложение
├── bot.py              # Telegram бот
├── config.py           # Конфигурация
├── requirements.txt    # Зависимости
├── .gitignore          # Игнорируемые файлы
├── .env                # Переменные окружения (не коммитится)
├── templates/
│   ├── index.html      # Главная страница
│   ├── history.html    # История клипов
│   └── settings.html   # Настройки
├── static/
│   ├── css/
│   │   └── style.css   # Стили
│   └── js/
│       ├── main.js     # Основной JS
│       ├── history.js  # JS для истории
│       └── settings.js # JS для настроек
├── utils/
│   └── video_processor.py  # Обработка видео
├── downloads/          # Временные загрузки
├── clips/              # Готовые клипы
└── temp/               # Временные файлы
```

## 🔧 Настройки

В настройках можно изменить:
- Минимальную и максимальную длительность клипов
- Размер выходного видео
- Модель Whisper
- Язык субтитров

## 🤖 Telegram бот

Бот отправляет:
- Приветствие при запуске: "Здравствуй, @ник! Я бот для монтажа"
- Уведомления о готовых клипах

## 📝 Лицензия

Проект распространяется под лицензией MIT.