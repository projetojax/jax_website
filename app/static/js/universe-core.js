class UniverseGame {
    constructor(config) {
        this.config = config;
        this.init();
    }

    init() {
        this.setupElements();
        this.setupControls();
        this.setupModal();
        this.gameLoop();
    }

    setupElements() {
        this.viewport = document.getElementById('viewport');
        this.mapLayer = document.getElementById('mapLayer');
        this.player = document.getElementById('player');
        this.zones = document.querySelectorAll('.zone');
        this.modal = document.getElementById('welcomeModal');
        
        // Configurações do mapa
        this.mapSize = this.config.mapSize;
        this.viewSize = { width: 1000, height: 600 };
        this.speed = this.config.speed || 4;
        
        // Estado do jogo
        this.pos = { ...this.config.initialPos };
        this.keys = {};
        this.muted = false;
        this.activeZone = null;
        this.confirming = false;

        console.log('Game initialized:', this.config.areaName);
    }

    setupControls() {
        // Teclado - CORREÇÃO AQUI
        const handleKeyDown = (e) => {
            const key = e.key.toLowerCase();
            console.log('Key down:', key);
            
            // Mapear teclas
            if (key === 'a' || key === 'arrowleft') this.keys.left = true;
            if (key === 'd' || key === 'arrowright') this.keys.right = true;
            if (key === 'w' || key === 'arrowup') this.keys.up = true;
            if (key === 's' || key === 'arrowdown') this.keys.down = true;
            
            // Prevenir comportamento padrão apenas para as teclas de movimento
            if (['a', 'd', 'w', 's', 'arrowleft', 'arrowright', 'arrowup', 'arrowdown'].includes(key)) {
                e.preventDefault();
            }
        };

        const handleKeyUp = (e) => {
            const key = e.key.toLowerCase();
            console.log('Key up:', key);
            
            if (key === 'a' || key === 'arrowleft') this.keys.left = false;
            if (key === 'd' || key === 'arrowright') this.keys.right = false;
            if (key === 'w' || key === 'arrowup') this.keys.up = false;
            if (key === 's' || key === 'arrowdown') this.keys.down = false;
        };

        window.addEventListener('keydown', handleKeyDown.bind(this));
        window.addEventListener('keyup', handleKeyUp.bind(this));

        // Tela cheia
        const btnFull = document.getElementById('btnFull');
        if (btnFull) {
            btnFull.addEventListener('click', () => {
                if (document.fullscreenElement) {
                    document.exitFullscreen();
                } else {
                    document.documentElement.requestFullscreen();
                }
            });
        }

        // Som
        const btnMute = document.getElementById('btnMute');
        if (btnMute) {
            btnMute.addEventListener('click', () => {
                this.muted = !this.muted;
                btnMute.textContent = this.muted ? '🔇 Som' : '🔊 Som';
            });
        }

        // Fechar modal
        if (this.modal) {
            const closeModal = document.getElementById('closeModal');
            if (closeModal) {
                closeModal.addEventListener('click', () => {
                    this.modal.classList.add('hidden');
                    sessionStorage.setItem(`${this.config.areaName}_modal_shown`, 'true');
                });
            }
        }

        console.log('Controls setup complete');
    }

    setupModal() {
        if (this.modal) {
            const hasSeenModal = sessionStorage.getItem(`${this.config.areaName}_modal_shown`);
            if (!hasSeenModal) {
                this.modal.classList.remove('hidden');
            }
        }
    }

    clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    movePlayer() {
        let moved = false;

        // CORREÇÃO: Usar as chaves corretas
        if (this.keys.left) {
            this.pos.x -= this.speed;
            moved = true;
        }
        if (this.keys.right) {
            this.pos.x += this.speed;
            moved = true;
        }
        if (this.keys.up) {
            this.pos.y -= this.speed;
            moved = true;
        }
        if (this.keys.down) {
            this.pos.y += this.speed;
            moved = true;
        }

        // Limitar movimento aos limites do mapa
        this.pos.x = this.clamp(this.pos.x, 0, this.mapSize.width - 64);
        this.pos.y = this.clamp(this.pos.y, 0, this.mapSize.height - 80);

        if (moved) {
            console.log('Player moved to:', this.pos.x, this.pos.y);
        }
    }

    updateCamera() {
        // Atualizar posição do player
        this.player.style.left = `${this.pos.x}px`;
        this.player.style.top = `${this.pos.y}px`;

        // Calcular offset da câmera (centralizar no player)
        const offsetX = this.clamp(
            -(this.pos.x - this.viewSize.width / 2), 
            -(this.mapSize.width - this.viewSize.width), 
            0
        );
        const offsetY = this.clamp(
            -(this.pos.y - this.viewSize.height / 2), 
            -(this.mapSize.height - this.viewSize.height), 
            0
        );
        
        // Aplicar transformação ao mapa
        this.mapLayer.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
    }

    checkZoneCollision() {
        const playerRect = this.player.getBoundingClientRect();
        let currentZone = null;

        this.zones.forEach(zone => {
            const zoneRect = zone.getBoundingClientRect();
            
            const overlap = !(
                zoneRect.right < playerRect.left ||
                zoneRect.left > playerRect.right ||
                zoneRect.bottom < playerRect.top ||
                zoneRect.top > playerRect.bottom
            );

            if (overlap) {
                currentZone = zone;
            }
        });

        return currentZone;
    }

    handleZoneInteraction(zone) {
        if (!zone) {
            this.activeZone = null;
            this.confirming = false;
            return;
        }

        if (zone !== this.activeZone && !this.confirming && zone.dataset.link) {
            this.activeZone = zone;
            this.confirming = true;

            const areaName = zone.dataset.name || 'esta área';
            const confirmed = confirm(`Você está entrando em ${areaName}. Deseja continuar?`);

            if (confirmed) {
                window.location.href = zone.dataset.link;
            } else {
                // Move o player para fora da zona
                this.pos.y += 50;
                setTimeout(() => {
                    this.confirming = false;
                }, 600);
            }
        }
    }

    gameLoop() {
        this.movePlayer();
        this.updateCamera();
        
        const currentZone = this.checkZoneCollision();
        this.handleZoneInteraction(currentZone);

        requestAnimationFrame(() => this.gameLoop());
    }
}

// Inicialização para mapa inicial (com redirecionamento)
class InitialMapGame extends UniverseGame {
    constructor(config) {
        super(config);
    }
}

// Inicialização para mapas campus (com zonas interativas)
class CampusMapGame extends UniverseGame {
    constructor(config) {
        super(config);
        this.locationBox = document.getElementById('location');
        this.statusBox = document.getElementById('statusMsg');
        this.teleportButtons = document.querySelectorAll('.tele');
        this.setupTeleport();
    }

    setupTeleport() {
        this.teleportButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.target.dataset.target;
                const allowed = e.target.dataset.allowed === 'true';
                
                if (allowed && this.config.zonePositions && this.config.zonePositions[target]) {
                    this.teleportToZone(target);
                }
            });
        });
    }

    teleportToZone(zoneName) {
        const position = this.config.zonePositions[zoneName];
        if (position) {
            this.pos.x = position.x;
            this.pos.y = position.y;
            this.updateCamera();
            
            if (this.statusBox) {
                this.statusBox.textContent = `Teleportado para ${zoneName}.`;
            }
        }
    }

    handleZoneInteraction(zone) {
        if (!zone) {
            if (this.locationBox) this.locationBox.textContent = this.config.defaultLocation;
            this.activeZone = null;
            return;
        }

        const zoneName = zone.dataset.zone;
        const allowed = this.config.permissions && 
                       (this.config.permissions[zoneName] === true || this.config.permissions[zoneName] === 'true');

        if (this.locationBox) {
            this.locationBox.textContent = zone.dataset.name || zoneName;
        }

        if (this.statusBox) {
            if (allowed) {
                this.statusBox.textContent = `Acesso permitido à ${zoneName}.`;
                
                // Trigger modal para zona específica
                if (zoneName === this.config.triggerModalZone && this.modal) {
                    const hasSeenModal = sessionStorage.getItem(`${this.config.areaName}_modal_shown`);
                    if (!hasSeenModal) {
                        this.modal.classList.remove('hidden');
                    }
                }
            } else {
                this.statusBox.textContent = `Acesso negado à ${zoneName}.`;
            }
        }
    }
}