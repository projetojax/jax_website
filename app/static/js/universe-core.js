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
        
        // Estado do jogo - CORREÇÃO: Inicializar posição corretamente
        this.pos = { 
            x: this.config.initialPos.x || 400, 
            y: this.config.initialPos.y || 550 
        };
        
        this.keys = {
            left: false,
            right: false, 
            up: false,
            down: false
        };
        
        this.muted = false;
        this.activeZone = null;
        this.confirming = false;

        console.log('Game initialized:', this.config.areaName, 'Pos:', this.pos);
        
        // Posicionar personagem inicialmente
        this.updateCamera();
    }

    setupControls() {
        // Teclado - CORREÇÃO COMPLETA
        const handleKeyDown = (e) => {
            const key = e.key.toLowerCase();
            
            switch(key) {
                case 'a':
                case 'arrowleft':
                    this.keys.left = true;
                    e.preventDefault();
                    break;
                case 'd':
                case 'arrowright':
                    this.keys.right = true;
                    e.preventDefault();
                    break;
                case 'w':
                case 'arrowup':
                    this.keys.up = true;
                    e.preventDefault();
                    break;
                case 's':
                case 'arrowdown':
                    this.keys.down = true;
                    e.preventDefault();
                    break;
            }
        };

        const handleKeyUp = (e) => {
            const key = e.key.toLowerCase();
            
            switch(key) {
                case 'a':
                case 'arrowleft':
                    this.keys.left = false;
                    break;
                case 'd':
                case 'arrowright':
                    this.keys.right = false;
                    break;
                case 'w':
                case 'arrowup':
                    this.keys.up = false;
                    break;
                case 's':
                case 'arrowdown':
                    this.keys.down = false;
                    break;
            }
        };

        document.addEventListener('keydown', handleKeyDown.bind(this));
        document.addEventListener('keyup', handleKeyUp.bind(this));

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
                setTimeout(() => {
                    this.modal.classList.remove('hidden');
                }, 500);
            }
        }
    }

    clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    movePlayer() {
        let moved = false;

        // Movimento com colisão prevenida durante confirmação
        if (!this.confirming) {
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
        }

        // Limitar movimento aos limites do mapa
        this.pos.x = this.clamp(this.pos.x, 0, this.mapSize.width - 64);
        this.pos.y = this.clamp(this.pos.y, 0, this.mapSize.height - 80);

        return moved;
    }

    updateCamera() {
        // Atualizar posição do player IMEDIATAMENTE
        if (this.player) {
            this.player.style.left = `${this.pos.x}px`;
            this.player.style.top = `${this.pos.y}px`;
        }

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
        if (this.mapLayer) {
            this.mapLayer.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
        }
    }

    checkZoneCollision() {
        if (!this.player) return null;

        const playerRect = this.player.getBoundingClientRect();
        let currentZone = null;

        this.zones.forEach(zone => {
            const zoneRect = zone.getBoundingClientRect();
            
            // Verificar colisão mais precisa
            const collision = !(
                playerRect.right < zoneRect.left + 20 ||
                playerRect.left > zoneRect.right - 20 ||
                playerRect.bottom < zoneRect.top + 20 ||
                playerRect.top > zoneRect.bottom - 20
            );

            if (collision) {
                currentZone = zone;
            }
        });

        return currentZone;
    }

    handleZoneInteraction(zone) {
        // Se não há zona, resetar estado
        if (!zone) {
            if (this.activeZone) {
                this.activeZone = null;
                this.confirming = false;
            }
            return;
        }

        // Se já está confirmando, não fazer nada
        if (this.confirming) {
            return;
        }

        // Se é uma nova zona com link
        if (zone !== this.activeZone && zone.dataset.link) {
            this.activeZone = zone;
            this.confirming = true;

            const areaName = zone.dataset.name || 'esta área';
            const isExit = zone.dataset.link === '/home' || zone.classList.contains('zone-exit');
            
            const message = isExit 
                ? `Deseja voltar ao mapa inicial?` 
                : `Você está entrando em ${areaName}. Deseja continuar?`;

            const confirmed = confirm(message);

            if (confirmed) {
                // Redirecionar
                window.location.href = zone.dataset.link;
            } else {
                // CANCELAR: Mover personagem para longe
                this.handleCancelMovement(isExit);
            }
        }
    }

    handleCancelMovement(isExit) {
        console.log('Cancelado - reposicionando personagem');
        
        if (isExit) {
            // Para saída, mover para longe da porta
            this.pos.x = this.config.initialPos.x + 150;
            this.pos.y = this.config.initialPos.y + 100;
        } else {
            // Para outras zonas, usar posição segura
            const safeX = this.config.safePos ? this.config.safePos.x : this.config.initialPos.x;
            const safeY = this.config.safePos ? this.config.safePos.y : this.config.initialPos.y;
            this.pos.x = safeX;
            this.pos.y = safeY;
        }
        
        // Forçar atualização IMEDIATA
        this.updateCamera();
        
        // Resetar estados após breve delay
        setTimeout(() => {
            this.activeZone = null;
            this.confirming = false;
            console.log('Estado resetado após cancelamento');
        }, 300);
    }

    gameLoop() {
        const moved = this.movePlayer();
        
        if (moved || this.confirming) {
            this.updateCamera();
        }
        
        // Só verificar colisões se não estiver confirmando
        if (!this.confirming) {
            const currentZone = this.checkZoneCollision();
            if (currentZone !== this.activeZone) {
                this.handleZoneInteraction(currentZone);
            }
        }

        requestAnimationFrame(() => this.gameLoop());
    }
}

// Mapa Inicial
class InitialMapGame extends UniverseGame {
    constructor(config) {
        super(config);
    }
}

// Mapas das Áreas
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
                if (this.confirming) return; // Prevenir durante confirmação
                
                const target = e.target.dataset.target;
                const allowed = e.target.dataset.allowed === 'true';
                
                if (allowed && this.config.zonePositions && this.config.zonePositions[target]) {
                    this.teleportToZone(target);
                } else if (!allowed) {
                    alert('Acesso não permitido a esta área.');
                }
            });
        });

        // Botão de saída no painel
        const exitBtn = document.querySelector('.exit-btn');
        if (exitBtn) {
            exitBtn.addEventListener('click', () => {
                if (this.confirming) return;
                
                const confirmed = confirm('Deseja voltar ao mapa inicial?');
                if (confirmed) {
                    window.location.href = '/home';
                }
            });
        }
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
            
            if (this.locationBox) {
                const zone = Array.from(this.zones).find(z => z.dataset.zone === zoneName);
                this.locationBox.textContent = zone ? zone.dataset.name : zoneName;
            }
        }
    }

    handleZoneInteraction(zone) {
        super.handleZoneInteraction(zone);
        
        // Atualizar interface para zonas internas
        if (zone && this.locationBox) {
            this.locationBox.textContent = zone.dataset.name || 'Localização';
        } else if (this.locationBox) {
            this.locationBox.textContent = this.config.defaultLocation || 'Explorando';
        }
    }
}

// Inicialização global para prevenir conflitos
window.initGame = function(config) {
    if (config.areaName === 'inicial') {
        return new InitialMapGame(config);
    } else {
        return new CampusMapGame(config);
    }
};