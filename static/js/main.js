// ========================================
// CS2 Clip Maker - Main JavaScript
// ========================================

class ClipMaker {
    constructor() {
        this.apiBase = '';
        this.currentTaskId = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkUrlParam();
    }

    setupEventListeners() {
        // Process button
        const processBtn = document.getElementById('processBtn');
        if (processBtn) {
            processBtn.addEventListener('click', () => this.processVideo());
        }

        // Enter key in input
        const urlInput = document.getElementById('youtubeUrl');
        if (urlInput) {
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.processVideo();
                }
            });
        }

        // New clip button
        const newClipBtn = document.getElementById('newClipBtn');
        if (newClipBtn) {
            newClipBtn.addEventListener('click', () => this.resetForm());
        }
    }

    checkUrlParam() {
        const urlParams = new URLSearchParams(window.location.search);
        const url = urlParams.get('url');
        if (url) {
            document.getElementById('youtubeUrl').value = url;
        }
    }

    async processVideo() {
        const url = document.getElementById('youtubeUrl').value.trim();
        
        if (!url) {
            this.showToast('Введите ссылку на YouTube видео', 'error');
            return;
        }

        // Validate URL
        if (!this.isValidYouTubeUrl(url)) {
            this.showToast('Неверный формат ссылки YouTube', 'error');
            return;
        }

        // Show progress section
        document.getElementById('progressSection').classList.remove('hidden');
        document.getElementById('resultSection').classList.add('hidden');
        
        // Reset progress
        this.resetProgress();
        
        // Disable button
        const processBtn = document.getElementById('processBtn');
        processBtn.disabled = true;
        processBtn.innerHTML = '<span class="btn-icon">⏳</span> Обработка...';

        try {
            // Start processing
            const response = await fetch('/api/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Ошибка при запуске обработки');
            }

            this.currentTaskId = data.task_id;
            
            // Poll for status
            this.pollTaskStatus(this.currentTaskId);

        } catch (error) {
            this.showToast(error.message, 'error');
            this.resetForm();
        }
    }

    async pollTaskStatus(taskId) {
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/task/${taskId}`);
                const data = await response.json();

                if (!data.success) {
                    throw new Error(data.error);
                }

                // Update progress
                this.updateProgress(data.progress, data.status);

                if (data.status === 'completed') {
                    clearInterval(pollInterval);
                    this.showResults(data.result);
                } else if (data.status === 'error') {
                    clearInterval(pollInterval);
                    this.showToast(data.error || 'Ошибка при обработке', 'error');
                    this.resetForm();
                }

            } catch (error) {
                clearInterval(pollInterval);
                this.showToast('Ошибка при получении статуса', 'error');
                this.resetForm();
            }
        }, 2000); // Poll every 2 seconds
    }

    resetProgress() {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        progressBar.style.width = '0%';
        progressText.textContent = '0%';

        // Reset steps
        const steps = document.querySelectorAll('.step');
        steps.forEach((step, index) => {
            step.classList.remove('active');
            if (index === 0) {
                step.classList.add('active');
            }
        });
    }

    updateProgress(progress, status) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${progress}%`;

        // Update steps
        const steps = document.querySelectorAll('.step');
        const activeStepIndex = Math.min(
            Math.floor((progress / 100) * steps.length),
            steps.length - 1
        );

        steps.forEach((step, index) => {
            step.classList.remove('active');
            if (index <= activeStepIndex) {
                step.classList.add('active');
            }
        });
    }

    showResults(result) {
        // Hide progress, show results
        document.getElementById('progressSection').classList.add('hidden');
        document.getElementById('resultSection').classList.remove('hidden');

        // Enable button
        const processBtn = document.getElementById('processBtn');
        processBtn.disabled = false;
        processBtn.innerHTML = '<span class="btn-icon">▶</span> Обработать';

        // Render clips
        const clipsContainer = document.getElementById('resultClips');
        clipsContainer.innerHTML = '';

        if (result.clips && result.clips.length > 0) {
            result.clips.forEach((clipPath, index) => {
                const clipCard = this.createClipCard(clipPath, index + 1, result.total_clips);
                clipsContainer.appendChild(clipCard);
            });
        } else {
            clipsContainer.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">😔</span>
                    <h3>Не удалось создать клипы</h3>
                    <p>Попробуйте другое видео</p>
                </div>
            `;
        }

        // Scroll to results
        document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
    }

    createClipCard(clipPath, index, total) {
        const card = document.createElement('div');
        card.className = 'clip-card';
        card.style.animationDelay = `${index * 0.1}s`;

        const filename = clipPath.split('/').pop();
        const duration = this.formatDuration(this.getDurationFromFilename(filename));

        card.innerHTML = `
            <div class="clip-thumbnail">
                <div class="clip-thumbnail-content">
                    <div class="clip-thumbnail-icon">🎬</div>
                    <div class="clip-thumbnail-duration">${duration}</div>
                </div>
            </div>
            <div class="clip-info">
                <h4>Клип #${index} из ${total}</h4>
                <div class="clip-meta">
                    <span class="clip-meta-item">📐 1080×1920</span>
                    <span class="clip-meta-item">📝 Субтитры</span>
                </div>
                <div class="clip-actions">
                    <button class="clip-btn clip-btn-preview" onclick="ClipMaker.playClip('${clipPath}')">
                        <span class="btn-icon">▶</span>
                        Просмотр
                    </button>
                    <button class="clip-btn clip-btn-download" onclick="ClipMaker.downloadClip('${clipPath}')">
                        <span class="btn-icon">⬇️</span>
                        Скачать
                    </button>
                </div>
            </div>
        `;

        return card;
    }

    formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    getDurationFromFilename(filename) {
        // Extract duration from filename like "clip_1_120s.mp4"
        const match = filename.match(/(\d+)s/);
        return match ? parseInt(match[1]) : 60;
    }

    resetForm() {
        document.getElementById('youtubeUrl').value = '';
        document.getElementById('progressSection').classList.add('hidden');
        document.getElementById('resultSection').classList.add('hidden');
        this.resetProgress();
        this.currentTaskId = null;
    }

    isValidYouTubeUrl(url) {
        const patterns = [
            /^https?:\/\/(www\.)?youtube\.com\/watch\?v=.+/,
            /^https?:\/\/(www\.)?youtube\.com\/embed\/.+/,
            /^https?:\/\/(www\.)?youtube\.com\/v\/.+/,
            /^https?:\/\/(www\.)?youtu\.be\/.+/,
            /^https?:\/\/(www\.)?youtube\.com\/shorts\/.+/
        ];
        
        return patterns.some(pattern => pattern.test(url));
    }

    showToast(message, type = 'success') {
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = type === 'success' ? '✅' : '❌';
        
        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-message">${message}</span>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    playClip(clipPath) {
        const videoUrl = `/api/clip/${clipPath}`;
        const player = document.createElement('video');
        player.src = videoUrl;
        player.controls = true;
        player.style.width = '100%';
        player.style.maxWidth = '600px';
        player.style.borderRadius = '8px';
        player.style.background = '#000';
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 20px;
        `;
        
        modal.innerHTML = `
            <div style="background: #1a1a24; border-radius: 12px; padding: 20px; max-width: 700px; width: 100%;">
                <button onclick="this.closest('div').parentElement.remove()" 
                        style="position: absolute; top: 10px; right: 10px; background: none; border: none; color: white; font-size: 24px; cursor: pointer;">
                    ✕
                </button>
                ${player.outerHTML}
            </div>
        `;
        
        document.body.appendChild(modal);
        player.play();
    }

    downloadClip(clipPath) {
        window.open(`/api/clip/${clipPath}`);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.ClipMaker = new ClipMaker();
});