import pandas as pd
import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'data', 'jax.db')
PATH_DB = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')), 'static', 'data', 'jax.db')

def importar_matriculas():
    # Configurações
    DATABASE_URI = f'sqlite:///{PATH_DB}'  # Ajuste para seu banco
    CSV_FILE = 'backup_matriculas.csv'
    
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
        
        print(f"Encontradas {len(df)} matrículas no backup")
        
        # Para cada matrícula no backup
        for index, row in df.iterrows():
            numero_matricula = row['Nº Matrícula']
            nome_completo = row['Nome']
            email = row['Email']
            status = row['Status']
            data_criacao = row['Data']
            
            print(f"Processando: {nome_completo} (Matrícula: {numero_matricula})")
            
            # Verificar se a matrícula já existe
            cursor.execute("SELECT id FROM matriculas WHERE id = ? OR email = ?", 
                         (numero_matricula, email))
            existing = cursor.fetchone()
            
            if existing:
                print(f"⚠️  Matrícula {numero_matricula} já existe. Atualizando...")
                
                # Atualizar matrícula existente
                cursor.execute("""
                    UPDATE matriculas SET 
                    nome_completo = ?, 
                    email = ?, 
                    status = ?, 
                    data_criacao = ?
                    WHERE id = ?
                """, (nome_completo, email, status, data_criacao, numero_matricula))
                
            else:
                print(f"➕ Adicionando nova matrícula: {numero_matricula}")
                
                # Inserir nova matrícula
                cursor.execute("""
                    INSERT INTO matriculas (id, nome_completo, email, status, data_criacao)
                    VALUES (?, ?, ?, ?, ?)
                """, (numero_matricula, nome_completo, email, status, data_criacao))
        
        # Commit das mudanças
        conn.commit()
        print("✅ Importação de matrículas concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a importação: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    importar_matriculas()