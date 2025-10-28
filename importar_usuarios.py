import pandas as pd
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash
import os

BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'data', 'jax.db')
PATH_DB = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')), 'static', 'data', 'jax.db')

def importar_usuarios():
    # Configurações
    DATABASE_URI = f'sqlite:///{PATH_DB}'  # Ajuste para seu banco
    CSV_FILE = 'backup_users.csv'
    
    # Conectar ao banco
    if 'sqlite' in DATABASE_URI:
        conn = sqlite3.connect(DATABASE_URI.replace('sqlite:///', ''))
    else:
        # Para PostgreSQL/MySQL, ajuste a conexão
        import psycopg2
        conn = psycopg2.connect(DATABASE_URI)
    
    cursor = conn.cursor()
    
    try:
        # Ler o CSV
        df = pd.read_csv(CSV_FILE)
        
        print(f"Encontrados {len(df)} usuários no backup")
        
        # Para cada usuário no backup
        for index, row in df.iterrows():
            user_id = row['ID']
            username = row['Usuário']
            nome_completo = row['Nome Completo']
            email = row['E-mail']
            profile = row['Perfil']
            data_criacao = row['Criado em']
            
            print(f"Processando: {username} ({email})")
            
            # Verificar se o usuário já existe
            cursor.execute("SELECT id FROM users WHERE id = ? OR email = ? OR username = ?", 
                         (user_id, email, username))
            existing = cursor.fetchone()
            
            if existing:
                print(f"⚠️  Usuário {username} já existe. Atualizando...")
                
                # Atualizar usuário existente
                cursor.execute("""
                    UPDATE users SET 
                    username = ?, 
                    email = ?, 
                    profile = ?, 
                    date_created = ?
                    WHERE id = ?
                """, (username, email, profile, data_criacao, user_id))
                
            else:
                print(f"➕ Adicionando novo usuário: {username}")
                
                # Gerar senha padrão (usuário precisará resetar)
                senha_padrao = generate_password_hash('senha_temp_123')
                
                # Inserir novo usuário
                cursor.execute("""
                    INSERT INTO users (id, username, email, password_hash, profile, date_created)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, username, email, senha_padrao, profile, data_criacao))
        
        # Commit das mudanças
        conn.commit()
        print("✅ Importação concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a importação: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    importar_usuarios()