// ========================================
// CS2 Clip Maker - History Page JavaScript
// ========================================

class HistoryPage {
    constructor() {
        this.apiBase = '';
        this.init();
    }

    init() {
        this.loadClips();
        this.setupEventListeners();
    }

    setupEventListeners() {
        const clearBtn = document.getElementById('clearHistoryBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearHistory());
        }
    }

    async loadClips() {
        try {
            const response = await fetch('/api/clips');
            const data = await response.json();

            if (data.success) {
                this.renderClips(data.clips);
            } else {
                console.error('Failed to load clips:', data.error);
            }
        } catch (error) {
            console.error('Error loading clips:', error);
        }
    }

    renderClips(clips) {
        const container = document.getElementById('clipsList');
        const emptyState = document.getElementById('emptyState');

        if (!clips || clips.length === 0) {
            container.innerHTML = '';
            emptyState.style.display = 'block';
            return;
        }

        emptyState.style.display = 'none';
        container.innerHTML = '';

        clips.forEach((clip, index) => {
            const clipCard = this.createClipCard(clip, index + 1);
            container.appendChild(clipCard);
        });
    }

    createClipCard(clip, index) {
        const card = document.createElement('div');
        card.className = 'clip-card';
        card.style.animationDelay = `${index * 0.1}s`;

        const filename = clip.path ? clip.path.split('/').pop() : `Клип ${index}`;
        const duration = clip.duration || 60;
        const size = clip.size_mb || 0;
        const createdAt = clip.created_at ? new Date(clip.created_at).toLocaleDateString('ru-RU') : '';

        card.innerHTML = `
            <div class="clip-thumbnail">
                <div class="clip-thumbnail-content">
                    <div class="clip-thumbnail-icon">🎬</div>
                    <div class="clip-thumbnail-duration">${this.formatDuration(duration)}</div>
                </div>
            </div>
            <div class="clip-info">
                <h4>${filename}</h4>
                <div class="clip-meta">
                    <span class="clip-meta-item">📐 1080×1920</span>
                    <span class="clip-meta-item">📊 ${size} MB</span>
                    <span class="clip-meta-item">📅 ${createdAt}</span>
                </div>
                <div class="clip-actions">
                    <button class="clip-btn clip-btn-preview" onclick="HistoryPage.playClip('${clip.path}')">
                        <span class="btn-icon">▶</span>
                        Просмотр
                    </button>
                    <button class="clip-btn clip-btn-download" onclick="HistoryPage.downloadClip('${clip.path}')">
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

    async clearHistory() {
        if (!confirm('Вы уверены, что хотите очистить историю клипов?')) {
            return;
        }

        try {
            const response = await fetch('/api/clear-history', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                this.loadClips();
                this.showToast('История очищена', 'success');
            } else {
                this.showToast(data.error || 'Ошибка при очистке', 'error');
            }
        } catch (error) {
            this.showToast('Ошибка при очистке истории', 'error');
        }
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
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.HistoryPage = new HistoryPage();
});