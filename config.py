import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Основная конфигурация приложения"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'cs2-clip-maker-secret-key-2024')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DOWNLOADS_DIR = os.path.join(BASE_DIR, 'downloads')
    CLIPS_DIR = os.path.join(BASE_DIR, 'clips')
    TEMP_DIR = os.path.join(BASE_DIR, 'temp')
    
    # Video settings
    CLIP_MIN_DURATION = 60  # секунд
    CLIP_MAX_DURATION = 120  # секунд
    OUTPUT_WIDTH = 1080
    OUTPUT_HEIGHT = 1920
    OUTPUT_FPS = 30
    
    # FFmpeg settings
    FFMPEG_BINARY = os.getenv('FFMPEG_BINARY', 'ffmpeg')
    
    # Whisper settings
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
    WHISPER_LANGUAGE = os.getenv('WHISPER_LANGUAGE', 'ru')
    
    # Processing limits
    MAX_VIDEO_SIZE_MB = 500
    MAX_CLIPS_PER_VIDEO = 10
    
    # Ensure directories exist
    @classmethod
    def init_dirs(cls):
        for directory in [cls.DOWNLOADS_DIR, cls.CLIPS_DIR, cls.TEMP_DIR]:
            os.makedirs(directory, exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': Config
}