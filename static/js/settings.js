// ========================================
// CS2 Clip Maker - Settings Page JavaScript
// ========================================

class SettingsPage {
    constructor() {
        this.apiBase = '';
        this.init();
    }

    init() {
        this.loadSettings();
        this.setupEventListeners();
    }

    setupEventListeners() {
        const saveBtn = document.getElementById('saveSettingsBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveSettings());
        }

        const resetBtn = document.getElementById('resetSettingsBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetSettings());
        }
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            const data = await response.json();

            if (data.success) {
                const settings = data.settings;
                
                document.getElementById('clipMinDuration').value = settings.clip_min_duration || 60;
                document.getElementById('clipMaxDuration').value = settings.clip_max_duration || 120;
                document.getElementById('outputWidth').value = settings.output_width || 1080;
                document.getElementById('outputHeight').value = settings.output_height || 1920;
                document.getElementById('whisperModel').value = settings.whisper_model || 'base';
                document.getElementById('whisperLanguage').value = settings.whisper_language || 'ru';
            } else {
                console.error('Failed to load settings:', data.error);
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    async saveSettings() {
        const settings = {
            clip_min_duration: parseInt(document.getElementById('clipMinDuration').value),
            clip_max_duration: parseInt(document.getElementById('clipMaxDuration').value),
            output_width: parseInt(document.getElementById('outputWidth').value),
            output_height: parseInt(document.getElementById('outputHeight').value),
            whisper_model: document.getElementById('whisperModel').value,
            whisper_language: document.getElementById('whisperLanguage').value
        };

        // Validation
        if (settings.clip_min_duration >= settings.clip_max_duration) {
            this.showToast('Минимальная длительность должна быть меньше максимальной', 'error');
            return;
        }

        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Настройки сохранены успешно', 'success');
            } else {
                this.showToast(data.error || 'Ошибка при сохранении', 'error');
            }
        } catch (error) {
            this.showToast('Ошибка при сохранении настроек', 'error');
        }
    }

    async resetSettings() {
        if (!confirm('Вы уверены, что хотите сбросить настройки к значениям по умолчанию?')) {
            return;
        }

        document.getElementById('clipMinDuration').value = 60;
        document.getElementById('clipMaxDuration').value = 120;
        document.getElementById('outputWidth').value = 1080;
        document.getElementById('outputHeight').value = 1920;
        document.getElementById('whisperModel').value = 'base';
        document.getElementById('whisperLanguage').value = 'ru';

        await this.saveSettings();
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
    window.SettingsPage = new SettingsPage();
});