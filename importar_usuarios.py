import pandas as pd
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash
import os

# Caminho correto para o banco REAL
PATH_DB = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'data', 'jax.db')

def importar_usuarios():
    CSV_FILE = 'backup_users.csv'

    if not os.path.exists(PATH_DB):
        print("❌ Banco de dados não encontrado em:", PATH_DB)
        return

    if not os.path.exists(CSV_FILE):
        print("❌ CSV não encontrado:", CSV_FILE)
        return

    # Conectar ao banco real
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()

    try:
        df = pd.read_csv(CSV_FILE)

        print(f"Encontrados {len(df)} usuários no backup")

        for index, row in df.iterrows():
            user_id = int(row['ID'])
            username = row['Usuário']
            email = row['E-mail']
            profile = row['Perfil']

            # Nome completo — se não tiver, usa o username como fallback
            nome_completo = row.get('Nome Completo', None)
            if pd.isna(nome_completo) or nome_completo == "" or nome_completo is None:
                nome_completo = username

            # Converter data corretamente
            try:
                data_criacao = datetime.fromisoformat(row['Criado em'])
            except:
                data_criacao = datetime.utcnow()

            print(f"Processando: {username} ({email})")

            # Verifica se já existe
            cursor.execute(
                "SELECT id FROM users WHERE id = ? OR email = ? OR username = ?",
                (user_id, email, username)
            )
            existing = cursor.fetchone()

            if existing:
                print(f"⚠️ Usuário {username} já existe. Atualizando...")

                cursor.execute("""
                    UPDATE users SET
                        username = ?,
                        email = ?,
                        profile = ?,
                        date_created = ?,
                        nome_completo = ?
                    WHERE id = ?
                """, (username, email, profile, data_criacao, nome_completo, user_id))

            else:
                print(f"➕ Adicionando novo usuário: {username}")

                senha_padrao = generate_password_hash('123456')

                cursor.execute("""
                    INSERT INTO users (id, username, email, password_hash, profile, date_created, nome_completo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, username, email, senha_padrao, profile, data_criacao, nome_completo))

        conn.commit()
        print("✅ Importação concluída com sucesso!")

    except Exception as e:
        print(f"❌ Erro durante a importação: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    importar_usuarios()
