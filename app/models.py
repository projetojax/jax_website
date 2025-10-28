from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import sqlite3
import os

# Caminho absoluto para o banco principal
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PATH_DB = os.path.join(BASE_DIR, 'database.db')

db = SQLAlchemy()

# ======================================
# MODELO DE USUÁRIO (SQLAlchemy)
# ======================================

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile = db.Column(db.String(20), default='curioso')  # curioso, aluno, admin, funcionario
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


# ======================================
# SISTEMA DE AVATARES (sqlite3)
# ======================================

def init_avatar_tables():
    """Inicializa as tabelas necessárias para o sistema de avatares."""
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()
    
    # Tabela de itens de avatar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS avatar_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL,          -- 'hair', 'shirt', 'pants', 'shoes', 'accessory'
            item_name TEXT NOT NULL,
            item_path TEXT NOT NULL,
            rarity TEXT DEFAULT 'common',     -- 'common', 'rare', 'epic', 'legendary'
            price INTEGER DEFAULT 0,
            unlock_condition TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de inventário do usuário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_avatar_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (item_id) REFERENCES avatar_items (id)
        )
    ''')
    
    # Tabela de avatar equipado
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_equipped_avatar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            hair_item_id INTEGER,
            shirt_item_id INTEGER,
            pants_item_id INTEGER,
            shoes_item_id INTEGER,
            accessory_item_id INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Inserir alguns itens padrão
    default_items = [
        ('hair', 'Cabelo Padrão', 'img/avatar/items/hair/default.png', 'common', 0, None),
        ('shirt', 'Camiseta Básica', 'img/avatar/items/shirt/default.png', 'common', 0, None),
        ('pants', 'Calça Jeans', 'img/avatar/items/pants/default.png', 'common', 0, None),
        ('shoes', 'Tênis Básico', 'img/avatar/items/shoes/default.png', 'common', 0, None),
        ('hair', 'Cabelo Moicano', 'img/avatar/items/hair/mohawk.png', 'rare', 100, 'complete_tutorial'),
        ('shirt', 'Camiseta JAX', 'img/avatar/items/shirt/jax.png', 'rare', 150, 'first_achievement')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO avatar_items (item_type, item_name, item_path, rarity, price, unlock_condition)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', default_items)
    
    conn.commit()
    conn.close()


# ======================================
# FUNÇÕES DE GERENCIAMENTO DE AVATAR
# ======================================

def get_user_avatar_data(user_id):
    """Busca os dados completos do avatar do usuário."""
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT hair_item_id, shirt_item_id, pants_item_id, shoes_item_id, accessory_item_id
        FROM user_equipped_avatar WHERE user_id = ?
    ''', (user_id,))
    equipped = cursor.fetchone()
    
    avatar_data = {
        'hair': 'img/avatar/items/hair/default.png',
        'shirt': 'img/avatar/items/shirt/default.png',
        'pants': 'img/avatar/items/pants/default.png',
        'shoes': 'img/avatar/items/shoes/default.png',
        'accessory': None
    }
    
    if equipped:
        item_ids = [equipped[0], equipped[1], equipped[2], equipped[3], equipped[4]]
        item_types = ['hair', 'shirt', 'pants', 'shoes', 'accessory']
        
        for i, item_id in enumerate(item_ids):
            if item_id:
                cursor.execute('SELECT item_path FROM avatar_items WHERE id = ?', (item_id,))
                item = cursor.fetchone()
                if item:
                    avatar_data[item_types[i]] = item[0]
    
    conn.close()
    return avatar_data


def get_available_avatar_items(user_id, item_type=None):
    """Busca todos os itens de avatar disponíveis, com flag indicando se o usuário já os possui."""
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()
    
    query = '''
        SELECT ai.*, 
               CASE WHEN uai.user_id IS NOT NULL THEN 1 ELSE 0 END as owned
        FROM avatar_items ai
        LEFT JOIN user_avatar_items uai ON ai.id = uai.item_id AND uai.user_id = ?
    '''
    params = [user_id]
    
    if item_type:
        query += ' WHERE ai.item_type = ?'
        params.append(item_type)
    
    query += ' ORDER BY ai.rarity, ai.price'
    cursor.execute(query, params)
    items = cursor.fetchall()
    
    conn.close()
    
    return [{
        'id': item[0],
        'type': item[1],
        'name': item[2],
        'path': item[3],
        'rarity': item[4],
        'price': item[5],
        'unlock_condition': item[6],
        'owned': bool(item[8])
    } for item in items]


def equip_avatar_item(user_id, item_type, item_id):
    """Equipa um item de avatar para o usuário."""
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()
    
    # Verifica se o usuário possui o item
    cursor.execute('''
        SELECT 1 FROM user_avatar_items 
        WHERE user_id = ? AND item_id = ?
    ''', (user_id, item_id))
    
    if not cursor.fetchone():
        conn.close()
        return False
    
    # Busca o equipamento atual
    cursor.execute('SELECT * FROM user_equipped_avatar WHERE user_id = ?', (user_id,))
    equipped = cursor.fetchone()
    
    if not equipped:
        # Cria registro novo
        cursor.execute('''
            INSERT INTO user_equipped_avatar (user_id) VALUES (?)
        ''', (user_id,))
    
    # Atualiza o campo específico do item
    cursor.execute(f'''
        UPDATE user_equipped_avatar
        SET {item_type}_item_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (item_id, user_id))
    
    conn.commit()
    conn.close()
    return True


# ======================================
# UTILITÁRIO DE INICIALIZAÇÃO
# ======================================

def init_all():
    """Inicializa tanto o SQLAlchemy quanto as tabelas de avatar."""
    from app import app  # importa apenas dentro da função p/ evitar circular import
    with app.app_context():
        db.create_all()
        init_avatar_tables()