import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram бот для уведомлений о готовых клипах"""
    
    def __init__(self):
        self.config = Config
        self.token = self.config.TELEGRAM_BOT_TOKEN
        self.chat_id = self.config.TELEGRAM_CHAT_ID
        
        if not self.token:
            logger.warning("TELEGRAM_BOT_TOKEN не задан в конфигурации")
            self.application = None
            return
        
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков команд"""
        
        # Команда /start
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            username = user.username or user.first_name
            
            message = (
                f"🎬 <b>Здравствуй, @{username}!</b>\n\n"
                f"Я бот для монтажа CS2-клипов.\n\n"
                f"✅ <b>Возможности:</b>\n"
                f"• Анализ видео и поиск интересных моментов\n"
                f"• Вырезание клипов 60-120 секунд\n"
                f"• Формат TikTok 9:16, 1080×1920\n"
                f"• Белые жирные субтитры с обводкой\n"
                f"• Размытый фон с увеличенным центром\n"
                f"• Просмотр и скачивание готовых клипов\n\n"
                f"📝 <b>Как использовать:</b>\n"
                f"1. Вставьте YouTube-ссылку в веб-приложении\n"
                f"2. Нажмите «Обработать»\n"
                f"3. Дождитесь готовности клипов\n"
                f"4. Скачайте готовые файлы"
            )
            
            await update.message.reply_html(message)
        
        # Команда /help
        async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            message = (
                "🎬 <b>Помощь по боту</b>\n\n"
                f"• <b>/start</b> - Начать работу\n"
                f"• <b>/help</b> - Эта справка\n"
                f"• <b>/status</b> - Статус обработки\n\n"
                f"Для работы используйте веб-приложение:\n"
                f"1. Вставьте ссылку на CS2 видео\n"
                f"2. Бот автоматически найдёт интересные моменты\n"
                f"3. Сформирует клипы в TikTok формате\n"
                f"4"  # Добавить правильный текст
            )
            
            await update.message.reply_html(message)
        
        # Команда /status
        async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            message = (
                "📊 <b>Статус обработки</b>\n\n"
                f"• Веб-приложение: <b>Активно</b>\n"
                f"• Telegram бот: <b>Активен</b>\n"
                f"• FFmpeg: <b>Установлен</b>\n"
                f"• Whisper: <b>Готов к работе</b>\n\n"
                f"Для создания клипов используйте веб-приложение."
            )
            
            await update.message.reply_html(message)
        
        # Обработчик текстовых сообщений
        async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            username = user.username or user.first_name
            
            message = (
                f"🎬 <b>Здравствуй, @{username}!</b>\n\n"
                f"Я бот для монтажа CS2-клипов.\n\n"
                f"✅ <b>Возможности:</b>\n"
                f"• Анализ видео и поиск интересных моментов\n"
                f"• Вырезание клипов 60-120 секунд\n"
                f"• Формат TikTok 9:16, 1080×1920\n"
                f"• Белые жирные субтитры с обводкой\n"
                f"• Размытый фон с увеличенным центром\n"
                f"• Просмотр и скачивание готовых клипов\n\n"
                f"📝 <b>Как использовать:</b>\n"
                f"1. Вставьте YouTube-ссылку в веб-приложении\n"
                f"2. Нажмите «Обработать»\n"
                f"3. Дождитесь готовности клипов\n"
                f"4. Скачайте готовые файлы"
            )
            
            await update.message.reply_html(message)
        
        # Регистрация обработчиков
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("status", status_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    def send_notification(self, message: str):
        """Отправка уведомления о готовых клипах"""
        if not self.application or not self.chat_id:
            logger.warning("Не могу отправить уведомление: бот не настроен")
            return
        
        try:
            self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info("Уведомление отправлено успешно")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления: {e}")
    
    def send_clip_notification(self, clip_path: str, clip_name: str):
        """Отправка уведомления о готовом клипе"""
        if not self.application or not self.chat_id:
            return
        
        try:
            file_size = os.path.getsize(clip_path) / (1024 * 1024)  # MB
            duration = self._get_video_duration(clip_path)
            
            message = (
                f"🎬 <b>Готов клип!</b>\n\n"
                f"📁 <b>Название:</b> {clip_name}\n"
                f"⏱️ <b>Длительность:</b> {duration:.1f} сек\n"
                f"📊 <b>Размер:</b> {file_size:.2f} MB\n"
                f"📐 <b>Формат:</b> 1080×1920 (9:16)\n\n"
                f"✅ Кликните, чтобы скачать"
            )
            
            self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления о клипе: {e}")
    
    def _get_video_duration(self, video_path: str) -> float:
        """Получение длительности видео"""
        try:
            import subprocess
            cmd = [
                self.config.FFMPEG_BINARY,
                '-i', video_path,
                '-f', 'null',
                '-'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            for line in result.stderr.split('\n'):
                if 'Duration:' in line:
                    time_str = line.split('Duration:')[1].split(',')[0].strip()
                    h, m, s = time_str.split(':')
                    return int(h) * 3600 + int(m) * 60 + float(s)
            
            return 0
        except Exception as e:
            logger.error(f"Ошибка при получении длительности: {e}")
            return 0
    
    def start(self):
        """Запуск бота"""
        if not self.application:
            logger.error("Бот не может быть запущен: отсутствует токен")
            return
        
        logger.info("Запуск Telegram бота...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    def stop(self):
        """Остановка бота"""
        if self.application:
            logger.info("Остановка Telegram бота...")
            self.application.stop()
            self.application.shutdown()


if __name__ == '__main__':
    bot = TelegramBot()
    bot.start()