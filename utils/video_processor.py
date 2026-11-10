import os
import subprocess
import json
import whisper
from typing import List, Dict, Tuple
from config import Config


class VideoProcessor:
    """Класс для обработки видео"""
    
    def __init__(self):
        self.config = Config
        self.config.init_dirs()
        self.model = None
    
    def load_whisper_model(self):
        """Загрузка модели Whisper"""
        if self.model is None:
            print(f"Загрузка модели Whisper: {self.config.WHISPER_MODEL}")
            self.model = whisper.load_model(self.config.WHISPER_MODEL)
        return self.model
    
    def download_video(self, url: str) -> str:
        """Скачивание видео с YouTube"""
        import yt_dlp
        
        output_template = os.path.join(self.config.DOWNLOADS_DIR, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Заменяем расширение на mp4 если нужно
            if not filename.endswith('.mp4'):
                filename = filename.rsplit('.', 1)[0] + '.mp4'
            
        return filename
    
    def get_video_duration(self, video_path: str) -> float:
        """Получение длительности видео"""
        cmd = [
            self.config.FFMPEG_BINARY,
            '-i', video_path,
            '-f', 'null',
            '-'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Извлекаем длительность из вывода FFmpeg
        for line in result.stderr.split('\n'):
            if 'Duration:' in line:
                time_str = line.split('Duration:')[1].split(',')[0].strip()
                h, m, s = time_str.split(':')
                return int(h) * 3600 + int(m) * 60 + float(s)
        
        return 0
    
    def extract_clips(self, video_path: str, clips: List[Dict]) -> List[str]:
        """Вырезание клипов из видео"""
        clips_paths = []
        total_duration = self.get_video_duration(video_path)
        
        for i, clip in enumerate(clips):
            start_time = clip['start']
            duration = clip['duration']
            
            output_path = os.path.join(
                self.config.CLIPS_DIR,
                f'clip_{i+1}_{int(start_time)}s.mp4'
            )
            
            # Формат TikTok 9:16, 1080×1920
            cmd = [
                self.config.FFMPEG_BINARY,
                '-i', video_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-vf', f'scale={self.config.OUTPUT_WIDTH}:{self.config.OUTPUT_HEIGHT}:force_original_aspect_ratio=decrease,pad={self.config.OUTPUT_WIDTH}:{self.config.OUTPUT_HEIGHT}:(ow-iw)/2:(oh-ih)/2',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '192k',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True)
            clips_paths.append(output_path)
        
        return clips_paths
    
    def add_blurred_background(self, clip_path: str) -> str:
        """Добавление размытого фона"""
        output_path = clip_path.replace('.mp4', '_blurred.mp4')
        
        # Создаём размытое фоновое изображение
        bg_path = os.path.join(self.config.TEMP_DIR, 'background.png')
        
        cmd = [
            self.config.FFMPEG_BINARY,
            '-i', clip_path,
            '-vf', f'crop={self.config.OUTPUT_WIDTH}:{self.config.OUTPUT_HEIGHT}:0:0,scale=512:512',
            '-frames:v', '1',
            bg_path
        ]
        subprocess.run(cmd, capture_output=True)
        
        # Добавляем размытый фон к видео
        cmd = [
            self.config.FFMPEG_BINARY,
            '-i', bg_path,
            '-i', clip_path,
            '-filter_complex',
            f'[1:v]scale={self.config.OUTPUT_WIDTH}:{self.config.OUTPUT_HEIGHT}:force_original_aspect_ratio=decrease,pad={self.config.OUTPUT_WIDTH}:{self.config.OUTPUT_WIDTH}:(ow-iw)/2:(oh-ih)/2[fg];'
            f'[0:v]boxblur=20[bg];'
            f'[bg][fg]overlay=(W-w)/2:(H-h)/2',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        # Удаляем временный фон
        if os.path.exists(bg_path):
            os.remove(bg_path)
        
        return output_path
    
    def add_subtitles(self, video_path: str, subtitles: List[Dict]) -> str:
        """Добавление субтитров к видео"""
        output_path = video_path.replace('.mp4', '_subtitled.mp4')
        
        # Создаём временный файл субтитров
        srt_path = os.path.join(self.config.TEMP_DIR, 'subtitles.srt')
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(subtitles):
                start = self._format_timestamp(sub['start'])
                end = self._format_timestamp(sub['end'])
                text = sub['text']
                
                f.write(f"{i+1}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")
        
        # Добавляем субтитры
        cmd = [
            self.config.FFMPEG_BINARY,
            '-i', video_path,
            '-vf', f"subtitles={srt_path}:force_style='Fontname=Arial,FontSize=48,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=3,Alignment=10'",
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        # Удаляем временный файл субтитров
        if os.path.exists(srt_path):
            os.remove(srt_path)
        
        return output_path
    
    def _format_timestamp(self, seconds: float) -> str:
        """Форматирование времени в формат SRT"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    def process_video(self, url: str) -> Dict:
        """Полная обработка видео"""
        print(f"Начинаем обработку видео: {url}")
        
        # Шаг 1: Скачивание
        print("Шаг 1: Скачивание видео...")
        video_path = self.download_video(url)
        print(f"Видео скачано: {video_path}")
        
        # Шаг 2: Распознавание речи
        print("Шаг 2: Распознавание речи с помощью Whisper...")
        self.load_whisper_model()
        result = self.model.transcribe(video_path, language=self.config.WHISPER_LANGUAGE)
        
        # Шаг 3: Анализ и выбор клипов
        print("Шаг 3: Анализ и выбор клипов...")
        clips = self._analyze_clips(result, video_path)
        
        # Шаг 4: Вырезание клипов
        print("Шаг 4: Вырезание клипов...")
        clips_paths = self.extract_clips(video_path, clips)
        
        # Шаг 5: Добавление размытого фона
        print("Шаг 5: Добавление размытого фона...")
        final_clips = []
        for clip_path in clips_paths:
            print(f"Обработка клипа: {clip_path}")
            final_clip = self.add_blurred_background(clip_path)
            final_clips.append(final_clip)
        
        # Шаг 6: Добавление субтитров
        print("Шаг 6: Добавление субтитров...")
        final_clips_with_subs = []
        for clip_path in final_clips:
            print(f"Добавление субтитров к: {clip_path}")
            final_clip = self.add_subtitles(clip_path, result['segments'])
            final_clips_with_subs.append(final_clip)
        
        # Очистка временных файлов
        if os.path.exists(video_path):
            os.remove(video_path)
        
        return {
            'success': True,
            'clips': final_clips_with_subs,
            'total_clips': len(final_clips_with_subs),
            'video_duration': self.get_video_duration(video_path) if os.path.exists(video_path) else 0
        }
    
    def _analyze_clips(self, transcript: Dict, video_path: str) -> List[Dict]:
        """Анализ транскрипции и выбор клипов"""
        segments = transcript['segments']
        clips = []
        
        # Группируем сегменты по смыслу
        current_clip = None
        current_duration = 0
        
        for segment in segments:
            start = segment['start']
            end = segment['end']
            duration = end - start
            text = segment['text'].strip()
            
            if current_clip is None:
                current_clip = {
                    'start': start,
                    'end': end,
                    'text': text,
                    'duration': duration
                }
                current_duration = duration
            else:
                # Добавляем сегмент к текущему клипу
                current_clip['end'] = end
                current_clip['text'] += ' ' + text
                current_clip['duration'] += duration
                
                # Если клип достиг максимальной длительности, сохраняем его
                if current_clip['duration'] >= Config.CLIP_MIN_DURATION:
                    clips.append(current_clip.copy())
                    current_clip = None
                    current_duration = 0
        
        # Добавляем последний клип если он достаточно длинный
        if current_clip and current_clip['duration'] >= Config.CLIP_MIN_DURATION:
            clips.append(current_clip)
        
        # Ограничиваем количество клипов
        clips = clips[:Config.MAX_CLIPS_PER_VIDEO]
        
        # Если нет подходящих клипов, создаем один из середины видео
        if not clips:
            total_duration = self.get_video_duration(video_path)
            if total_duration >= Config.CLIP_MIN_DURATION:
                clips.append({
                    'start': (total_duration - Config.CLIP_MAX_DURATION) / 2,
                    'end': (total_duration + Config.CLIP_MAX_DURATION) / 2,
                    'text': 'CS2 Clip',
                    'duration': Config.CLIP_MAX_DURATION
                })
        
        return clips
    
    def get_clip_info(self, clip_path: str) -> Dict:
        """Получение информации о клипе"""
        duration = self.get_video_duration(clip_path)
        file_size = os.path.getsize(clip_path) / (1024 * 1024)  # MB
        
        return {
            'path': clip_path,
            'duration': duration,
            'size_mb': round(file_size, 2),
            'created_at': os.path.getctime(clip_path)
        }