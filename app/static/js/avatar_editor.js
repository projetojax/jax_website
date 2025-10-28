class AvatarEditor {
    constructor(currentAvatar, availableItems) {
        this.currentAvatar = { ...currentAvatar };
        this.availableItems = availableItems;
        this.currentCategory = 'hair';
        
        this.init();
    }
    
    init() {
        this.setupElements();
        this.setupEventListeners();
        this.renderAvatar();
        this.loadCategoryItems('hair');
    }
    
    setupElements() {
        this.avatarPreview = document.getElementById('avatarPreview');
        this.itemsGrid = document.getElementById('itemsGrid');
        this.tabButtons = document.querySelectorAll('.tab-btn');
        this.saveModal = document.getElementById('saveModal');
        
        // Elementos de ação
        document.getElementById('btnRandom').addEventListener('click', () => this.randomizeAvatar());
        document.getElementById('btnReset').addEventListener('click', () => this.resetAvatar());
        document.getElementById('btnSave').addEventListener('click', () => this.saveAvatar());
        document.getElementById('closeSaveModal').addEventListener('click', () => this.hideSaveModal());
    }
    
    setupEventListeners() {
        // Tabs de categoria
        this.tabButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const category = e.target.dataset.category;
                this.switchCategory(category);
            });
        });
    }
    
    switchCategory(category) {
        // Atualizar tabs ativas
        this.tabButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.category === category);
        });
        
        this.currentCategory = category;
        this.loadCategoryItems(category);
    }
    
    loadCategoryItems(category) {
        const items = this.availableItems[category] || [];
        
        this.itemsGrid.innerHTML = items.map(item => `
            <div class="item-card ${this.isItemEquipped(item) ? 'equipped' : ''} ${!item.owned ? 'locked' : ''}" 
                 data-item-id="${item.id}" data-item-type="${item.type}">
                <div class="item-preview" style="background-image: url('${item.path}')"></div>
                <div class="item-name">${item.name}</div>
                <div class="item-rarity rarity-${item.rarity}">${item.rarity}</div>
                ${!item.owned ? '<div class="item-locked">🔒</div>' : ''}
            </div>
        `).join('');
        
        // Adicionar event listeners aos itens
        this.itemsGrid.querySelectorAll('.item-card:not(.locked)').forEach(card => {
            card.addEventListener('click', (e) => {
                const itemId = e.currentTarget.dataset.itemId;
                const itemType = e.currentTarget.dataset.itemType;
                this.equipItem(itemType, parseInt(itemId));
            });
        });
    }
    
    isItemEquipped(item) {
        const currentItemPath = this.currentAvatar[item.type];
        return currentItemPath === item.path;
    }
    
    equipItem(itemType, itemId) {
        // Encontrar o item nos availableItems
        const item = this.availableItems[itemType].find(i => i.id === itemId);
        
        if (item && item.owned) {
            this.currentAvatar[itemType] = item.path;
            this.renderAvatar();
            this.loadCategoryItems(this.currentCategory); // Recarregar para atualizar estado
            
            // Salvar no servidor
            this.saveToServer(itemType, itemId);
        }
    }
    
    renderAvatar() {
        this.avatarPreview.innerHTML = '';
        
        // Ordem de renderização: corpo → calças → camiseta → cabelo → acessório
        const renderOrder = ['pants', 'shirt', 'hair', 'accessory'];
        
        renderOrder.forEach(type => {
            if (this.currentAvatar[type]) {
                const layer = document.createElement('div');
                layer.className = 'avatar-layer';
                layer.style.backgroundImage = `url('${this.currentAvatar[type]}')`;
                this.avatarPreview.appendChild(layer);
            }
        });
    }
    
    randomizeAvatar() {
        Object.keys(this.currentAvatar).forEach(type => {
            const available = this.availableItems[type].filter(item => item.owned);
            if (available.length > 0) {
                const randomItem = available[Math.floor(Math.random() * available.length)];
                this.currentAvatar[type] = randomItem.path;
            }
        });
        
        this.renderAvatar();
        this.loadCategoryItems(this.currentCategory);
    }
    
    resetAvatar() {
        this.currentAvatar = {
            'hair': 'img/avatar/items/hair/default.png',
            'shirt': 'img/avatar/items/shirt/default.png',
            'pants': 'img/avatar/items/pants/default.png', 
            'shoes': 'img/avatar/items/shoes/default.png',
            'accessory': null
        };
        
        this.renderAvatar();
        this.loadCategoryItems(this.currentCategory);
    }
    
    async saveToServer(itemType, itemId) {
        try {
            const response = await fetch('/api/avatar/equip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    item_type: itemType,
                    item_id: itemId
                })
            });
            
            const result = await response.json();
            
            if (!result.success) {
                console.error('Erro ao equipar item:', result.message);
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
        }
    }
    
    async saveAvatar() {
        // Aqui você pode adicionar lógica para salvar toda a configuração
        // Por enquanto, apenas mostra o modal de confirmação
        this.showSaveModal();
    }
    
    showSaveModal() {
        this.saveModal.classList.remove('hidden');
    }
    
    hideSaveModal() {
        this.saveModal.classList.add('hidden');
    }
}