import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
from config import Config
from utils.video_processor import VideoProcessor

# Инициализация Flask
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
CORS(app)

# Инициализация процессора видео
video_processor = VideoProcessor()

# История клипов
CLIPS_HISTORY_FILE = os.path.join(Config.BASE_DIR, 'clips_history.json')


def load_clips_history():
    """Загрузка истории клипов"""
    if os.path.exists(CLIPS_HISTORY_FILE):
        try:
            with open(CLIPS_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка при загрузке истории: {e}")
    return []


def save_clips_history(history):
    """Сохранение истории клипов"""
    try:
        with open(CLIPS_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка при сохранении истории: {e}")


# ==================== HTML Templates ====================

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/settings')
def settings():
    """Страница настроек"""
    return render_template('settings.html')


@app.route('/history')
def history():
    """Страница истории клипов"""
    return render_template('history.html')


# ==================== API Endpoints ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка здоровья API"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'ffmpeg': 'installed',
            'whisper': 'available'
        }
    })


@app.route('/api/process', methods=['POST'])
def process_video():
    """Обработка видео"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'Не указана ссылка'}), 400
        
        # Генерируем ID задачи
        task_id = str(uuid.uuid4())
        
        # Запускаем обработку в фоновом потоке
        import threading
        thread = threading.Thread(
            target=_process_video_async,
            args=(task_id, url)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Обработка началась'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _process_video_async(task_id: str, url: str):
    """Асинхронная обработка видео"""
    try:
        # Сохраняем прогресс
        session[f'{task_id}_progress'] = 0
        session[f'{task_id}_status'] = 'processing'
        
        # Обработка видео
        result = video_processor.process_video(url)
        
        # Сохраняем результат
        session[f'{task_id}_result'] = result
        session[f'{task_id}_status'] = 'completed'
        session[f'{task_id}_progress'] = 100
        
        # Добавляем в историю
        history = load_clips_history()
        for clip in result['clips']:
            clip_info = video_processor.get_clip_info(clip)
            clip_info['url'] = clip
            clip_info['youtube_url'] = url
            clip_info['created_at'] = datetime.now().isoformat()
            history.append(clip_info)
        
        save_clips_history(history)
        
    except Exception as e:
        print(f"Ошибка при обработке: {e}")
        session[f'{task_id}_status'] = 'error'
        session[f'{task_id}_error'] = str(e)


@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id: str):
    """Получение статуса задачи"""
    try:
        status = session.get(f'{task_id}_status', 'pending')
        progress = session.get(f'{task_id}_progress', 0)
        error = session.get(f'{task_id}_error')
        
        if status == 'completed':
            result = session.get(f'{task_id}_result')
            return jsonify({
                'success': True,
                'status': status,
                'progress': progress,
                'result': result
            })
        else:
            return jsonify({
                'success': True,
                'status': status,
                'progress': progress,
                'error': error
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clips', methods=['GET'])
def get_clips():
    """Получение списка клипов"""
    try:
        history = load_clips_history()
        return jsonify({
            'success': True,
            'clips': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clip/<path:clip_path>', methods=['GET'])
def download_clip(clip_path: str):
    """Скачивание клипа"""
    try:
        full_path = os.path.join(Config.CLIPS_DIR, clip_path)
        
        if not os.path.exists(full_path):
            return jsonify({'success': False, 'error': 'Клип не найден'}), 404
        
        # Получаем имя файла
        filename = os.path.basename(full_path)
        
        return send_file(
            full_path,
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/settings', methods=['GET', 'POST'])
def settings_api():
    """Настройки API"""
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'settings': {
                'clip_min_duration': Config.CLIP_MIN_DURATION,
                'clip_max_duration': Config.CLIP_MAX_DURATION,
                'output_width': Config.OUTPUT_WIDTH,
                'output_height': Config.OUTPUT_HEIGHT,
                'whisper_model': Config.WHISPER_MODEL,
                'whisper_language': Config.WHISPER_LANGUAGE
            }
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Обновляем настройки
            if 'clip_min_duration' in data:
                Config.CLIP_MIN_DURATION = int(data['clip_min_duration'])
            if 'clip_max_duration' in data:
                Config.CLIP_MAX_DURATION = int(data['clip_max_duration'])
            if 'whisper_model' in data:
                Config.WHISPER_MODEL = data['whisper_model']
            if 'whisper_language' in data:
                Config.WHISPER_LANGUAGE = data['whisper_language']
            
            return jsonify({
                'success': True,
                'message': 'Настройки обновлены'
            })
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Очистка истории"""
    try:
        # Удаляем файл истории
        if os.path.exists(CLIPS_HISTORY_FILE):
            os.remove(CLIPS_HISTORY_FILE)
        
        return jsonify({
            'success': True,
            'message': 'История очищена'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Страница не найдена'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Внутренняя ошибка сервера'}), 500


# ==================== Main ====================

if __name__ == '__main__':
    print("=" * 60)
    print("🎬 CS2 Clip Maker")
    print("=" * 60)
    print(f"✅ Flask приложение запущено на http://{Config.HOST}:{Config.PORT}")
    print(f"📁 Рабочая директория: {Config.BASE_DIR}")
    print(f"📥 Директория загрузок: {Config.DOWNLOADS_DIR}")
    print(f"🎬 Директория клипов: {Config.CLIPS_DIR}")
    print("=" * 60)
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )