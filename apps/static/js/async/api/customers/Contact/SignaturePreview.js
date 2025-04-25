class SignaturePreview {
    constructor() {
        this.previewContainer = document.getElementById('signature-preview');
        if (!this.previewContainer) return;

        this.formInputs = document.querySelectorAll('#signature-form input[type="text"]');
        this.badgeInput = document.querySelector('#badge-upload');
        
        const badgesDataElement = document.getElementById('badges-data');
        try {
            this.existingBadges = badgesDataElement && badgesDataElement.dataset.badges 
                ? JSON.parse(badgesDataElement.dataset.badges) 
                : [];
        } catch (e) {
            console.error('Error parsing badges data:', e);
            this.existingBadges = [];
        }
        
        this.initEventListeners();
        this.updatePreview();
    }
    
    initEventListeners() {
        this.formInputs.forEach(input => {
            input.addEventListener('input', () => this.updatePreview());
        });
        
        if (this.badgeInput) {
            this.badgeInput.addEventListener('change', (e) => this.handleBadgeUpload(e));
        }
    }
    
    updatePreview() {
        const formData = {
            word: document.querySelector('input[name="word"]')?.value || 'Cordialement,',
            name: document.querySelector('input[name="name"]')?.value || 'Nom Complet',
            title: document.querySelector('input[name="title"]')?.value || 'Poste/Title',
            phone: document.querySelector('input[name="phone"]')?.value || '+XXX XX XX XX XX'
        };
        
        this.previewContainer.innerHTML = `
            <div class="signature-preview-container">
                <div class="signature-row signature-word">${formData.word}</div>
                <div class="signature-row signature-name">${formData.name}</div>
                <div class="signature-row signature-details">
                    <span class="signature-title">${formData.title}</span> | 
                    <span class="signature-phone">${formData.phone}</span>
                </div>
                <div class="signature-row signature-footer">
                    <div class="badges-container" id="preview-badges">
                        ${this.renderBadges()}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderBadges() {
        if (!this.existingBadges || !Array.isArray(this.existingBadges)) return '';
        
        return this.existingBadges
            .filter(badge => badge)
            .map(badge => `
                <img src="${badge}" class="signature-badge" data-url="${badge}">
            `).join('');
    }
    
    handleBadgeUpload(event) {
        const files = event.target.files;
        if (!files || files.length === 0) return;
        
        Array.from(files).forEach(file => {
            if (!file.type.startsWith('image/')) return;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                const badgeImg = document.createElement('img');
                badgeImg.src = e.target.result;
                badgeImg.className = 'signature-badge';
                badgeImg.dataset.temp = 'true';
                
                const previewBadges = document.getElementById('preview-badges');
                if (previewBadges) {
                    previewBadges.appendChild(badgeImg);
                }
                
                if (!this.existingBadges) {
                    this.existingBadges = [];
                }
                this.existingBadges.push(e.target.result);
            };
            reader.readAsDataURL(file);
        });
    }
    
    updateBadgeUrls(savedBadges) {
        if (Array.isArray(savedBadges)) {
            this.existingBadges = savedBadges;
            this.updatePreview();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('signature-preview')) {
        window.signaturePreview = new SignaturePreview();
    }
});